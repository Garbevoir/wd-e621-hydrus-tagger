import click
from PIL import Image, ImageFile
from . import tag


@click.group()
def cli():
    pass


@click.command()
@click.argument("filename")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="SmilingWolf/wd-v1-4-vit-tagger-v2", help="The tagging model version to use")
@click.option("--threshold", default=0.35, help="The threshhold to drop tags below")
def evaluate(filename, cpu, model, threshold):
    integerator = tag.WaifuDiffusionInterrogator(
        'wd14-vit-v2',
        repo_id=model,
        revision='v2.0'
    )
    image = Image.open(filename)
    integerator.load()
    ratings, tags = integerator.interrogate(image)
    rating = "general"
    for key in ratings.keys():
        if ratings[key] > ratings[rating]:
            rating = key
    clipped_tags = []
    for key in tags.keys():
        if (tags[key] > threshold):
            clipped_tags.append(key)
    click.echo("rating: " + rating)
    click.echo("tags: " + ",".join(clipped_tags))


@click.command()
@click.argument("hash")
@click.option("--api-key", help="The API key for your Hydrus server")
@click.option("--cpu", help="Use CPU instead of GPU")
def evaluateApi():
    pass


if __name__ == '__main__':
    Image.init()
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    cli.add_command(evaluate)
    cli.add_command(evaluateApi)
    cli()
