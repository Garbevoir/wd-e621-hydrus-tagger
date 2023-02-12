import os
import pandas as pd
import numpy as np
import re

from typing import Tuple, Dict
from PIL import Image
from pathlib import Path
from huggingface_hub import hf_hub_download

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
            model_path='model.onnx',
            tags_path='selected_tags.csv',
            **kwargs
    ) -> None:
        self.name = name
        self.model_path = model_path
        self.tags_path = tags_path
        self.kwargs = kwargs

    def download(self) -> Tuple[os.PathLike, os.PathLike]:
        print(f"Loading {self.name} model file from {self.kwargs['repo_id']}")

        model_path = Path(hf_hub_download(
            **self.kwargs, filename=self.model_path))
        tags_path = Path(hf_hub_download(
            **self.kwargs, filename=self.tags_path))
        return model_path, tags_path

    def load(self, cpu) -> None:
        model_path, tags_path = self.download()

        # only one of these packages should be installed at a time in any one environment
        # https://onnxruntime.ai/docs/get-started/with-python.html#install-onnx-runtime
        # TODO: remove old package when the environment changes?
        if not onnx_loader.is_installed('onnxruntime'):
            package = os.environ.get(
                'ONNXRUNTIME_PACKAGE',
                'onnxruntime-gpu'
            )

            onnx_loader.run_pip(f'install {package}', 'onnxruntime')

        from onnxruntime import InferenceSession

        # https://onnxruntime.ai/docs/execution-providers/
        # https://github.com/toriato/stable-diffusion-webui-wd14-tagger/commit/e4ec460122cf674bbf984df30cdb10b4370c1224#r92654958
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if cpu:
            providers.pop(0)

        self.model = InferenceSession(str(model_path), providers=providers)

        print(f'Loaded {self.name} model from {model_path}')

        self.tags = pd.read_csv(tags_path)

    def interrogate(
            self,
            image: Image
    ) -> Tuple[
        Dict[str, float],  # rating confidents
        Dict[str, float]  # tag confidents
    ]:
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

        # first 4 items are for rating (general, sensitive, questionable, explicit)
        ratings = dict(tags[:4].values)

        # rest are regular tags
        tags = dict(tags[4:].values)

        return ratings, tags
