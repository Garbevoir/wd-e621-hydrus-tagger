import os.path

import click
from PIL import Image, ImageFile
from . import interrogate
import hydrus_api
from io import BytesIO
import json

Image.MAX_IMAGE_PIXELS = None

kaomojis = [
    "0_0",
    "(o)_(o)",
    "+_+",
    "+_-",
    "._.",
    "<o>_<o>",
    "<|>_<|>",
    "=_=",
    ">_<",
    "3_3",
    "6_9",
    ">_o",
    "@_@",
    "^_^",
    "o_o",
    "u_u",
    "x_x",
    "|_|",
    "||_||",
]

@click.group()
def cli():
    pass


@click.command()
@click.argument("filename")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="wd-v1-4-vit-tagger-v2", help="The tagging model to use")
@click.option("--threshold", default=0.35, help="The threshhold to drop tags below")
def evaluate(filename, cpu, model, threshold):
    if not os.path.isfile('./model/' + model + '/info.json'):
        raise ValueError("info.json not found in model folder!")

    with open('./model/' + model + '/info.json') as json_f:
        modelinfo = json.load(json_f)

    integerator = interrogate.WaifuDiffusionInterrogator(
        modelinfo['modelname'], # the name of the model for display purposes
        modelinfo['modelfile'], # the filename of the model file
        modelinfo['tagsfile'], # the filename of the tags file
        model, # the folder storing the previous two files as well as the info file
		modelinfo['ratingsflag'], # flag indicating whether model identifies content rating
		modelinfo['numberofratings'], # amount of tags to consider for content rating if so
        repo_id=modelinfo['source'], # source of the model, credit where credit is due
    )
    integerator.load(cpu)
    image = Image.open(filename)
    ratings, tags = integerator.interrogate(image)
    rating = "none"
    if modelinfo['ratingsflag']: 
        ratings["none"] = 0.0 # assign none a value of zero so that rating comparison can still occur
        for key in ratings.keys():
            if ratings[key] > ratings[rating]:
                rating = key
    clipped_tags = []

    for key in tags.keys():
        if (tags[key] > threshold):
            clipped_tags.append(key)
    click.echo("rating: " + rating)
    click.echo("tags: " + ", ".join(clipped_tags))


@click.command()
@click.argument("hash")
@click.option("--token", help="The API token for your Hydrus server")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="SmilingWolf/wd-v1-4-vit-tagger-v2", help="The tagging model to use")
@click.option("--threshold", default=0.35, help="The threshhold to drop tags below")
@click.option("--host", default="http://127.0.0.1:45869", help="The URL for your Hydrus server ")
@click.option("--tag-service", default="A.I. Tags", help="The Hydrus tag service to add tags to")
@click.option("--ratings-only", default=False, help="Strip all tags except for content rating")
@click.option("--privacy", default=True, help="hides the tag output from the cli")
def evaluate_api(hash, token, cpu, model, threshold, host, tag_service, ratings_only, privacy):
    if not os.path.isfile('./model/' + model + '/info.json'):
        raise ValueError("info.json not found in model folder!")

    with open('./model/' + model + '/info.json') as json_f:
        modelinfo = json.load(json_f)

    if ratings_only and not modelinfo['ratingsflag']:
        raise ValueError("--ratings-only set, but model does not support ratings!")

    integerator = interrogate.WaifuDiffusionInterrogator(
        modelinfo['modelname'], # the name of the model for display purposes
        modelinfo['modelfile'], # the filename of the model file
        modelinfo['tagsfile'], # the filename of the tags file
        model, # the folder storing the previous two files as well as the info file
		modelinfo['ratingsflag'], # flag indicating whether model identifies content rating
		modelinfo['numberofratings'], # amount of tags to consider for content rating if so
        repo_id=modelinfo['source'], # source of the model, credit where credit is due
    )
    integerator.load(cpu)
    client = hydrus_api.Client(token, host)
    image_bytes = BytesIO(client.get_file(hash).content)
    image = Image.open(image_bytes)
    ratings, tags = integerator.interrogate(image)
    rating = "none"
    if modelinfo['ratingsflag']: 
        ratings["none"] = 0.0 # assign none a value of zero so that rating comparison can still occur
        for key in ratings.keys():
            if ratings[key] > ratings[rating]:
                rating = key
    clipped_tags = []

    if not ratings_only:
        for key in tags.keys():
            if (tags[key] > threshold):
                clipped_tags.append(key.replace("_", " ") if key not in kaomojis else key)

    if not privacy:
        click.echo("rating: " + rating)
        click.echo("tags: " + ", ".join(clipped_tags))

    if modelinfo['ratingsflag']: clipped_tags.append("rating:" + rating)
    if ratings_only:
        clipped_tags.append("ratings only " + modelinfo['modelname'] + " ai generated tags") # create tag specifying that content tags were excluded
    else:
        clipped_tags.append(modelinfo['modelname'] + " ai generated tags") # create tag from given model name
    client.add_tags(hashes=[hash], service_names_to_tags={
        tag_service: clipped_tags
    })


@click.command()
@click.argument("hashfile")
@click.option("--token", help="The API token for your Hydrus server")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="wd-v1-4-vit-tagger-v2", help="The tagging model to use")
@click.option("--threshold", default=0.35, help="The threshhold to drop tags below")
@click.option("--host", default="http://127.0.0.1:45869", help="The URL for your Hydrus server ")
@click.option("--tag-service", default="A.I. Tags", help="The Hydrus tag service to add tags to")
@click.option("--ratings-only", default=False, help="Strip all tags except for content rating")
@click.option("--privacy", default=True, help="hides the tag output from the cli")
def evaluate_api_batch(hashfile, token, cpu, model, threshold, host, tag_service, ratings_only, privacy):
    if not os.path.isfile(hashfile):
        raise ValueError("hashfile not found!")
    if not os.path.isfile('./model/' + model + '/info.json'):
        raise ValueError("info.json not found in model folder!")

    with open('./model/' + model + '/info.json') as json_f:
        modelinfo = json.load(json_f)

    if ratings_only and not modelinfo['ratingsflag']:
        raise ValueError("--ratings-only set, but model does not support ratings!")

    integerator = interrogate.WaifuDiffusionInterrogator(
        modelinfo['modelname'], # the name of the model for display purposes
        modelinfo['modelfile'], # the filename of the model file
        modelinfo['tagsfile'], # the filename of the tags file
        model, # the folder storing the previous two files as well as the info file
		modelinfo['ratingsflag'], # flag indicating whether model identifies content rating
		modelinfo['numberofratings'], # amount of tags to consider for content rating if so
        repo_id=modelinfo['source'], # source of the model, credit where credit is due
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
            ratings, tags = integerator.interrogate(image)
            rating = "none"
            if modelinfo['ratingsflag']: 
                ratings["none"] = 0.0 # assign none a value of zero so that rating comparison can still occur
                for key in ratings.keys():
                    if ratings[key] > ratings[rating]:
                        rating = key
            clipped_tags = []

            if not ratings_only:
                for key in tags.keys():
                    if (tags[key] > threshold):
                        clipped_tags.append(key.replace("_", " ") if key not in kaomojis else key)

            if not privacy:
                click.echo("rating: " + rating)
                click.echo("tags: " + ", ".join(clipped_tags))
                click.echo()

            if modelinfo['ratingsflag']: clipped_tags.append("rating:" + rating)
            if ratings_only:
                clipped_tags.append("ratings only " + modelinfo['modelname'] + " ai generated tags") # create tag specifying that content tags were excluded
            else:
                clipped_tags.append(modelinfo['modelname'] + " ai generated tags")

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
