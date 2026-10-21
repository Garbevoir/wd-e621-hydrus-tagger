import os
import pandas as pd
import numpy as np
import re
import click

session_debug = []

def debug(msg):
    click.echo(msg)
    session_debug.append(msg)

from typing import Tuple, Dict
from PIL import Image
from pathlib import Path

from . import dbimutils
from . import onnx_loader

tag_escape_pattern = re.compile(r'([\\()])')
use_cpu = True

if use_cpu:
    tf_device_name = '/cpu:0'
else:
    tf_device_name = '/gpu:0'


class WaifuDiffusionInterrogator:
    def __init__(
            self,
            name: str,
            model_file: str,
            tags_file: str,
            folder: str,
            ratingsflag: bool,
            numberofratings: int,
            **kwargs
    ) -> None:
        self.name = name
        self.model_file = model_file
        self.tags_file = tags_file
        self.folder = folder
        self.ratingsflag = ratingsflag
        self.numberofratings = numberofratings
        self.kwargs = kwargs

    def findpaths(self) -> Tuple[os.PathLike, os.PathLike]:
        debug(f"DEBUG: Loading {self.name} model file from {self.kwargs['repo_id']}")

        model_file = Path('./model/' + self.folder + '/' + self.model_file)
        tags_file = Path('./model/' + self.folder + '/' + self.tags_file)
        return model_file, tags_file

    def load(self, cpu=True) -> None:
        model_file, tags_file = self.findpaths()
        debug(f"DEBUG: model path = {model_file}")
        debug(f"DEBUG: model exists = {model_file.exists()}")
        debug(f"DEBUG: tags path = {tags_file}")
        debug(f"DEBUG: tags exists = {tags_file.exists()}")

        debug("DEBUG: checking if onnxruntime is installed...")
        installed = onnx_loader.is_installed('onnxruntime')
        debug(f"DEBUG: onnxruntime installed = {installed}")

        if not installed:
            debug("DEBUG: onnxruntime not found, attempting install...")
            package = os.environ.get('ONNXRUNTIME_PACKAGE', 'onnxruntime-gpu')
            onnx_loader.run_pip(f'install {package}', 'onnxruntime')

        debug("DEBUG: about to import onnxruntime...")
        try:
            import onnxruntime
            debug(f"DEBUG: onnxruntime imported, version = {onnxruntime.__version__}")
            InferenceSession = onnxruntime.InferenceSession
            debug("DEBUG: InferenceSession obtained")
        except Exception as e:
            debug("DEBUG: import failed!")
            click.echo(repr(e))
            raise

        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if cpu:
            providers.pop(0)
        debug(f"DEBUG: using providers = {providers}")

        try:
            self.model = InferenceSession(str(model_file), providers=providers)
            click.echo(f'DEBUG: Loaded {self.name} model from {model_file}')
        except Exception as e:
            debug("DEBUG: InferenceSession failed!")
            click.echo(repr(e))
            raise

        self.tags = pd.read_csv(tags_file)
        debug("DEBUG: tags CSV loaded")

    def interrogate(
            self,
            image: Image
    ) -> Tuple[
        Dict[str, float],  # rating confidents
        Dict[str, float]  # tag confidents
    ]:
        # ... rest of the interrogate method stays the same ...
        # init model
        if not hasattr(self, 'model') or self.model is None:
            self.load()

        # code for converting the image and running the model is taken from the link below
        # thanks, SmilingWolf!
        # https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py

        # convert an image to fit the model
        _, height, _, _ = self.model.get_inputs()[0].shape

        # alpha to white
        image = image.convert('RGBA')
        new_image = Image.new('RGBA', image.size, 'WHITE')
        new_image.paste(image, mask=image)
        image = new_image.convert('RGB')
        image = np.asarray(image)

        # PIL RGB to OpenCV BGR
        image = image[:, :, ::-1]

        image = dbimutils.make_square(image, height)
        image = dbimutils.smart_resize(image, height)
        image = image.astype(np.float32)
        image = np.expand_dims(image, 0)

        # evaluate model
        input_name = self.model.get_inputs()[0].name
        label_name = self.model.get_outputs()[0].name
        confidents = self.model.run([label_name], {input_name: image})[0]

        tags = self.tags[:][['name']]
        tags['confidents'] = confidents[0]
        if self.ratingsflag:
            # first X items are for rating
            ratings = dict(tags[:self.numberofratings].values)

            # rest are regular tags
            tags = dict(tags[self.numberofratings:].values)
        else: 
            tags = dict(tags.values) # all tags are regular tags
            ratings = None

        return ratings, tags
