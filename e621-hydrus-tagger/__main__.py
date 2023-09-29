import os.path

import click
from PIL import Image, ImageFile
from . import interrogate
import hydrus_api
from io import BytesIO

Image.MAX_IMAGE_PIXELS = None

@click.group()
def cli():
    pass


@click.command()
@click.argument("filename")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="SmilingWolf/wd-v1-4-vit-tagger-v2", help="The tagging model version to use")
@click.option("--threshold", default=0.35, help="The threshhold to drop tags below")
def evaluate(filename, cpu, model, threshold):
    integerator = interrogate.WaifuDiffusionInterrogator(
        'wd14-vit-v2',
        repo_id=model,
        revision='v2.0'
    )
    integerator.load(cpu)
    image = Image.open(filename)
    ratings, tags = integerator.interrogate(image)
#    rating = "general"
#    for key in ratings.keys():
#        if ratings[key] > ratings[rating]:
#            rating = key
    clipped_tags = []
    for key in tags.keys():
        if (tags[key] > threshold):
            clipped_tags.append(key)
#    click.echo("rating: " + rating)
    click.echo("tags: " + ",".join(clipped_tags))


@click.command()
@click.argument("hash")
@click.option("--token", help="The API token for your Hydrus server")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="SmilingWolf/wd-v1-4-vit-tagger-v2", help="The tagging model version to use")
@click.option("--threshold", default=0.35, help="The threshhold to drop tags below")
@click.option("--host", default="http://127.0.0.1:45869", help="The URL for your Hydrus server ")
@click.option("--tag-service", default="my tags", help="The Hydrus tag service to add tags to")
def evaluate_api(hash, token, cpu, model, threshold, host, tag_service):
    integerator = interrogate.WaifuDiffusionInterrogator(
        'wd14-vit-v2',
        repo_id=model,
        revision='v2.0'
    )
    integerator.load(cpu)
    client = hydrus_api.Client(token, host)
    image_bytes = BytesIO(client.get_file(hash).content)
    image = Image.open(image_bytes)
    tags = integerator.interrogate(image)

    clipped_tags = []
    for key in tags.keys():
        if (tags[key] > threshold):
            clipped_tags.append(key.replace("_", " "))
    click.echo("tags: " + ",".join(clipped_tags))
    clipped_tags.append("e621-hydrus-tagger ai generated tags")
    client.add_tags(hashes=[hash], service_names_to_tags={
                tag_service: clipped_tags
    })


@click.command()
@click.argument("hashfile")
@click.option("--token", help="The API token for your Hydrus server")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="discord.gg/BDFpq9Yb7K", help="The tagging model version to use")
@click.option("--threshold", default=0.50, help="The threshhold to drop tags below")
@click.option("--host", default="http://127.0.0.1:45869", help="The URL for your Hydrus server ")
@click.option("--tag-service", default="my tags", help="The Hydrus tag service to add tags to")
def evaluate_api_batch(hashfile, token, cpu, model, threshold, host, tag_service):
    if not os.path.isfile(hashfile):
        raise ValueError("hashfile not found")
    integerator = interrogate.WaifuDiffusionInterrogator(
        'Z3D-E621-Convnext',
        repo_id=model,
        revision='v2.0'
    )
    integerator.load(cpu)
    client = hydrus_api.Client(token, host)
    with open(hashfile) as hashfile_f:
        hashes = hashfile_f.readlines()

    with click.progressbar(hashes) as bar:
        for hash in bar:
            click.echo(" processing: "+ hash)
            image_bytes = BytesIO(client.get_file(hash).content)
            image = Image.open(image_bytes)
            tags = integerator.interrogate(image)

            clipped_tags = []
            for key in tags.keys():
                if (tags[key] > threshold):
                    clipped_tags.append(key.replace("_", " "))
            clipped_tags.append("e621-hydrus-tagger ai generated tags")
            client.add_tags(hashes=[hash], service_names_to_tags={
                tag_service: clipped_tags
            })


if __name__ == '__main__':
    Image.init()
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    cli.add_command(evaluate)
    cli.add_command(evaluate_api)
    cli.add_command(evaluate_api_batch)
    cli()
