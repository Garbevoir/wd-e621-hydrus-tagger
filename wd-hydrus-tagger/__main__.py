import os.path
import re

import click
from PIL import Image, ImageFile
from . import interrogate
import hydrus_api
from io import BytesIO
import json
import yaml
import imageio.v3 as iio
import numpy as np

Image.MAX_IMAGE_PIXELS = None


def load_config(path="config.yaml"):
    """Load optional config.yaml from the current working directory."""
    if os.path.isfile(path):
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            click.echo(f"Warning: could not load {path}: {e}", err=True)
    return {}


def resolve(cli_value, config_key, fallback, config):
    """Prefer an explicitly supplied CLI value; otherwise use config.yaml, then the hard-coded fallback."""
    if cli_value is not None:
        return cli_value
    return config.get(config_key, fallback)


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
    ":d",
    ":3",
    ":o",
    ";d",
    ":>="
]


@click.group()
def cli():
    pass


@click.command()
@click.argument("filename")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="wd-v1-4-vit-tagger-v2", help="The tagging model to use")
@click.option("--threshold", default=0.35, help="The threshold to drop tags below")
def evaluate(filename, cpu, model, threshold):
    config = load_config()
    cpu = resolve(cpu if cpu is not False else None, "cpu", False, config)
    model = resolve(model if model != "wd-v1-4-vit-tagger-v2" else None, "model", "wd-v1-4-vit-tagger-v2", config)
    threshold = resolve(threshold if threshold != 0.35 else None, "threshold", 0.35, config)

    if not os.path.isfile('./model/' + model + '/info.json'):
        raise ValueError("info.json not found in model folder!")

    with open('./model/' + model + '/info.json') as json_f:
        modelinfo = json.load(json_f)

    integerator = interrogate.WaifuDiffusionInterrogator(
        modelinfo['modelname'],
        modelinfo['modelfile'],
        modelinfo['tagsfile'],
        model,
        modelinfo['ratingsflag'],
        modelinfo['numberofratings'],
        repo_id=modelinfo['source'],
    )
    integerator.load(cpu)
    image = Image.open(filename)
    ratings, tags = integerator.interrogate(image)
    rating = "none"
    if modelinfo['ratingsflag']:
        ratings["none"] = 0.0
        for key in ratings.keys():
            if ratings[key] > ratings[rating]:
                rating = key
    clipped_tags = []

    for key in tags.keys():
        if tags[key] > threshold:
            clipped_tags.append(key)
    click.echo("rating: " + rating)
    click.echo("tags: " + ", ".join(clipped_tags))


@click.command()
@click.argument("hash")
@click.option("--token", help="The API token for your Hydrus server")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="SmilingWolf/wd-v1-4-vit-tagger-v2", help="The tagging model to use")
@click.option("--threshold", default=0.35, help="The threshold to drop tags below")
@click.option("--host", default="http://127.0.0.1:45869", help="The URL for your Hydrus server ")
@click.option("--tag-service", default="A.I. Tags", help="The Hydrus tag service to add tags to")
@click.option("--ratings-only", default=False, help="Strip all tags except for content rating")
@click.option("--privacy", default=True, help="hides the tag output from the cli")
def evaluate_api(hash, token, cpu, model, threshold, host, tag_service, ratings_only, privacy):
    config = load_config()
    token = resolve(token, "token", None, config)
    if not token:
        raise click.UsageError("API token required. Set 'token' in config.yaml or pass --token")
    cpu = resolve(cpu if cpu is not False else None, "cpu", False, config)
    model = resolve(model if model != "wd-v1-4-vit-tagger-v2" else None, "model", "wd-v1-4-vit-tagger-v2", config)
    threshold = resolve(threshold if threshold != 0.35 else None, "threshold", 0.35, config)
    host = resolve(host if host != "http://127.0.0.1:45869" else None, "host", "http://127.0.0.1:45869", config)
    tag_service = resolve(tag_service if tag_service != "A.I. Tags" else None, "tag_service", "A.I. Tags", config)
    ratings_only = resolve(ratings_only if ratings_only is not False else None, "ratings_only", False, config)
    privacy = resolve(privacy if privacy is not True else None, "privacy", True, config)

    if not os.path.isfile('./model/' + model + '/info.json'):
        raise ValueError("info.json not found in model folder!")

    with open('./model/' + model + '/info.json') as json_f:
        modelinfo = json.load(json_f)

    integerator = interrogate.WaifuDiffusionInterrogator(
        modelinfo['modelname'],
        modelinfo['modelfile'],
        modelinfo['tagsfile'],
        model,
        modelinfo['ratingsflag'],
        modelinfo['numberofratings'],
        repo_id=modelinfo['source'],
    )
    integerator.load(cpu)
    client = hydrus_api.Client(token, host)

    services = client.get_services()
    service_key = None
    for key, info in services.get("services", {}).items():
        if info.get("name") == tag_service:
            service_key = key
            break
    if not service_key:
        raise ValueError(f"Tag service '{tag_service}' not found")

    image_bytes = BytesIO(client.get_file(hash).content)
    image = Image.open(image_bytes)
    ratings, tags = integerator.interrogate(image)
    rating = "none"
    if modelinfo['ratingsflag']:
        ratings["none"] = 0.0
        for key in ratings.keys():
            if ratings[key] > ratings[rating]:
                rating = key
    clipped_tags = []

    if not ratings_only:
        for key in tags.keys():
            if tags[key] > threshold:
                clipped_tags.append(key)

    if not privacy:
        click.echo("rating: " + rating)
        click.echo("tags: " + ", ".join(clipped_tags))

    if modelinfo['ratingsflag']:
        clipped_tags.append("rating:" + rating)
    if ratings_only:
        clipped_tags.append("ratings only " + modelinfo['modelname'] + " ai generated tags")
    else:
        clipped_tags.append(modelinfo['modelname'] + " ai generated tags")
    client.add_tags(hashes=[hash], service_keys_to_tags={
        service_key: clipped_tags
    })


def debug(msg):
    """Print a debug line and record it for session.log."""
    click.echo(msg)
    interrogate.session_debug.append(msg)


@click.command()
@click.argument("inputfile")
@click.option("--token", help="The API token for your Hydrus server")
@click.option("--cpu", default=False, help="Use CPU instead of GPU")
@click.option("--model", default="wd-v1-4-vit-tagger-v2", help="The tagging model to use")
@click.option("--threshold", default=0.35, help="The threshold to drop tags below")
@click.option("--host", default="http://127.0.0.1:45869", help="The URL for your Hydrus server ")
@click.option("--tag-service", default="A.I. Tags", help="The Hydrus tag service to add tags to")
@click.option("--ratings-only", default=False, help="Strip all tags except for content rating")
@click.option("--privacy", default=True, help="hides the tag output from the cli")
@click.option("--tags", is_flag=True, help="Treat inputfile as a list of Hydrus search tags instead of hashes")
@click.option("--skip-resume", is_flag=True, help="Ignore any unfinished checkpoint and start a fresh batch")
@click.option("--skip-tagged", is_flag=True, help="Skip files that already have an AI-generated tags marker")
@click.option("--limit", type=int, default=None, help="Stop after this many files have been successfully tagged (skips do not count)")
def evaluate_api_batch(inputfile, token, cpu, model, threshold, host, tag_service, ratings_only, privacy, tags, skip_resume, skip_tagged, limit):
    interrogate.session_debug.clear()
    config = load_config()
    token = resolve(token, "token", None, config)
    if not token:
        raise click.UsageError("API token required. Set 'token' in config.yaml or pass --token")
    cpu = resolve(cpu if cpu is not False else None, "cpu", False, config)
    model = resolve(model if model != "wd-v1-4-vit-tagger-v2" else None, "model", "wd-v1-4-vit-tagger-v2", config)
    threshold = resolve(threshold if threshold != 0.35 else None, "threshold", 0.35, config)
    host = resolve(host if host != "http://127.0.0.1:45869" else None, "host", "http://127.0.0.1:45869", config)
    tag_service = resolve(tag_service if tag_service != "A.I. Tags" else None, "tag_service", "A.I. Tags", config)
    ratings_only = resolve(ratings_only if ratings_only is not False else None, "ratings_only", False, config)
    privacy = resolve(privacy if privacy is not True else None, "privacy", True, config)

    if not os.path.isfile(inputfile):
        raise ValueError("input file not found!")
    if not os.path.isfile('./model/' + model + '/info.json'):
        raise ValueError("info.json not found in model folder!")

    with open('./model/' + model + '/info.json') as json_f:
        modelinfo = json.load(json_f)

    if ratings_only and not modelinfo['ratingsflag']:
        raise ValueError("--ratings-only set, but model does not support ratings!")

    integerator = interrogate.WaifuDiffusionInterrogator(
        modelinfo['modelname'],
        modelinfo['modelfile'],
        modelinfo['tagsfile'],
        model,
        modelinfo['ratingsflag'],
        modelinfo['numberofratings'],
        repo_id=modelinfo['source'],
    )
    integerator.load(cpu)
    client = hydrus_api.Client(token, host)

    services = client.get_services()
    service_key = None
    for key, info in services.get("services", {}).items():
        if info.get("name") == tag_service:
            service_key = key
            break
    if not service_key:
        raise ValueError(f"Tag service '{tag_service}' not found")

    checkpoint_file = "session.log"
    complete_marker = "session.complete"
    resuming = False
    already_done = set()
    hashes = []

    # Resume check loads what was already processed so we can exclude it
    # after the search. The log only contains hashes we actually attempted,
    # so we always re-query and then skip anything already in the log.
    if skip_resume:
        debug("DEBUG: --skip-resume set; starting fresh batch")
    elif os.path.isfile(complete_marker):
        debug("DEBUG: previous batch completed; starting fresh")
    elif os.path.isfile(checkpoint_file):
        with open(checkpoint_file) as f:
            lines = [line.rstrip("\n") for line in f if line.strip()]
        stored_limit = None
        hash_lines = []
        for line in lines:
            if line.startswith("#limit:"):
                try:
                    stored_limit = int(line.split(":", 1)[1])
                except ValueError:
                    pass
                continue
            # Only real hashes count. Debug lines and comments are ignored.
            candidate = line.split("\t", 1)[0]
            if re.fullmatch(r"[0-9a-fA-F]{64}", candidate):
                hash_lines.append(line)
        already_done = {line.split("\t", 1)[0] for line in hash_lines}
        ok_count = sum(1 for line in hash_lines if line.endswith("\tOK"))
        done_count = len(already_done)
        if done_count:
            resuming = True
            if stored_limit is not None:
                remaining_limit = max(0, stored_limit - ok_count)
                limit = remaining_limit
                debug(f"DEBUG: unfinished batch found — resuming with {done_count} done ({ok_count} OK), {remaining_limit} left of original limit {stored_limit}")
                if remaining_limit == 0:
                    debug("DEBUG: original limit already reached; nothing to do")
                    hashes = None  # sentinel: skip search and processing
            else:
                debug(f"DEBUG: unfinished batch found — resuming with {done_count} done")
        else:
            debug("DEBUG: checkpoint empty; starting fresh")
    else:
        debug("DEBUG: no previous batch found; starting fresh")

    if hashes is None:
        hashes = []
    elif tags:
        with open(inputfile) as f:
            search_tags = [line.strip() for line in f if line.strip()]
        # --limit stops the run after N successful tags. It does not override
        # a system:limit the user put in the search. If they didn't set one,
        # add a safety cap so we don't pull the entire database.
        if limit:
            has_system_limit = any(t.lower().startswith("system:limit") for t in search_tags)
            if not has_system_limit:
                safety = limit * 20
                search_tags.append(f"system:limit is {safety}")
                debug(f"DEBUG: --limit {limit} set with no system:limit; adding safety cap of {safety}")
            else:
                debug(f"DEBUG: --limit {limit} set; keeping your system:limit")
        # Flash files (.swf/.fla/.flash) cannot be processed. Always exclude them
        # from tag searches so Hydrus never returns them.
        flash_filter = "system:filetype is not flash"
        if flash_filter not in search_tags:
            search_tags.append(flash_filter)
            debug("DEBUG: excluding flash files from search")
        # --skip-tagged: let Hydrus exclude already-tagged files instead of
        # fetching them and skipping after the fact. Uses the current model's
        # own marker so it works for any model the user has installed.
        if skip_tagged:
            marker = modelinfo['modelname'] + " ai generated tags"
            negative = "-" + marker
            if negative not in search_tags and marker not in search_tags:
                search_tags.append(negative)
                debug(f"DEBUG: --skip-tagged set; adding negative search term: {negative}")
        debug(f"DEBUG: Searching Hydrus for tags: {search_tags}")
        result = client.search_files(tags=search_tags, return_hashes=True)
        if isinstance(result, dict):
            hashes = result.get("hashes", [])
        else:
            hashes = result
        debug(f"DEBUG: Found {len(hashes)} files")
    else:
        with open(inputfile) as hashfile_f:
            hashes = []
            for line in hashfile_f:
                line = line.strip()
                if not line:
                    continue
                # Hydrus copies hashes as "sha256:<hash>". Drop the prefix if present.
                if line.lower().startswith("sha256:"):
                    line = line[7:]
                hashes.append(line.strip())

    # Exclude anything already in the log so resume continues cleanly.
    if already_done:
        before = len(hashes)
        hashes = [h for h in hashes if h not in already_done]
        debug(f"DEBUG: excluded {before - len(hashes)} already-logged hashes; {len(hashes)} candidates remaining")

    # Fresh batch: write the debug block, then the limit header. Hashes are
    # appended as they are actually processed, so the log never holds
    # unprocessed ones. On resume, append a separator and the new debug.
    if not resuming:
        if os.path.isfile(complete_marker):
            os.remove(complete_marker)
        debug(f"DEBUG: initialized {checkpoint_file}")
        with open(checkpoint_file, "w") as f:
            for line in interrogate.session_debug:
                f.write(line + "\n")
            if limit:
                f.write(f"#limit:{limit}\n")
    else:
        with open(checkpoint_file, "a") as f:
            f.write("\n# resumed\n")
            for line in interrogate.session_debug:
                f.write(line + "\n")

    # Append a processed hash to the log. status is "OK" or a failure reason.
    def log_result(hash_value, status):
        try:
            with open(checkpoint_file, "a") as f:
                f.write(f"{hash_value}\t{status}\n")
        except Exception as e:
            debug(f"DEBUG: failed to update checkpoint for {hash_value}: {e}")

    tagged_count = 0
    skipped_count = 0

    # Collect every tag string out of a Hydrus metadata dict, whatever nesting it uses
    def collect_tags(obj):
        found = []
        if isinstance(obj, dict):
            for v in obj.values():
                found.extend(collect_tags(v))
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str):
                    found.append(item)
                else:
                    found.extend(collect_tags(item))
        return found

    # True if the file already carries an AI-generated marker for this model
    # (handles both spaced and underscored forms, and the "ratings only" variant)
    def already_ai_tagged(file_meta):
        if not file_meta:
            return False
        existing = collect_tags(file_meta.get("tags", {}))
        model_name = modelinfo['modelname'].lower().replace("_", " ")
        for tag in existing:
            normalized = tag.lower().replace("_", " ")
            if "ai generated tags" in normalized and model_name in normalized:
                return True
        return False

    # When --limit is set, the bar tracks successful tags against that limit.
    # Otherwise it tracks the full hash list.
    if limit:
        bar = click.progressbar(length=limit)
    else:
        bar = click.progressbar(length=len(hashes))
    with bar:
        for hash in hashes:
            click.echo(" processing: " + hash)
            try:
                file = client.get_file(hash).content
                metadata = client.get_file_metadata(hashes=[hash])
            except Exception as e:
                log_result(hash, f"failed to fetch from Hydrus: {e}")
                skipped_count += 1
                continue
            if isinstance(metadata, dict) and "metadata" in metadata:
                file_meta = metadata["metadata"][0] if metadata["metadata"] else None
            else:
                file_meta = metadata[0] if metadata else None
            num_frames = file_meta["num_frames"] if file_meta else None
            ext = file_meta.get("ext", "").lower() if file_meta else ""

            # Skip files that already have this model's AI-generated marker
            if skip_tagged and already_ai_tagged(file_meta):
                log_result(hash, "already ai-tagged")
                skipped_count += 1
                continue

            # Skip formats that hang or aren't useful to tag
            if ext in (".swf", ".fla", ".flash"):
                log_result(hash, f"unsupported format {ext}")
                skipped_count += 1
                continue

            if num_frames is None:
                try:
                    image = Image.open(BytesIO(file))
                    ratings, tags = integerator.interrogate(image)
                    threshold_local = threshold
                except Exception as e:
                    log_result(hash, f"unsupported file: {e}")
                    skipped_count += 1
                    continue
            else:
                # Multi-frame (video / animated)
                if num_frames >= 7:
                    frames_indexes = np.round(np.linspace(0, num_frames, 7)[1:-1])
                else:
                    frames_indexes = [np.round(num_frames / 2)]
                ratings, tags = {}, {}
                threshold_local = threshold * 2
                successful_frames = 0
                try:
                    for index in frames_indexes:
                        frame = None
                        # Prefer pyav when available; fall back to default backend
                        for plugin in ("pyav", None):
                            try:
                                kwargs = {"index": int(index)}
                                if plugin:
                                    kwargs["plugin"] = plugin
                                frame = iio.imread(BytesIO(file), extension=file_meta["ext"], **kwargs)
                                break
                            except Exception:
                                continue
                        if frame is None:
                            click.echo(f"  could not read frame {int(index)} of {hash}")
                            continue
                        image = Image.fromarray(frame)
                        rate, tag = integerator.interrogate(image)
                        if rate:
                            for r in rate:
                                ratings[r] = ratings.get(r, 0) + rate[r]
                        for t in tag:
                            tags[t] = tags.get(t, 0) + tag[t]
                        successful_frames += 1
                    if successful_frames == 0:
                        log_result(hash, "failed to decode any frames")
                        skipped_count += 1
                        continue
                except BaseException as e:
                    log_result(hash, f"failed to decode: {e}")
                    skipped_count += 1
                    continue

            rating = "none"
            if modelinfo['ratingsflag']:
                ratings["none"] = 0.0
                for key in ratings.keys():
                    if ratings[key] > ratings[rating]:
                        rating = key
            clipped_tags = []

            if not ratings_only:
                for key in tags.keys():
                    if tags[key] > threshold_local:
                        clipped_tags.append(key)

            if not privacy:
                click.echo("rating: " + rating)
                click.echo("tags: " + ", ".join(clipped_tags))
                click.echo()

            if modelinfo['ratingsflag']:
                clipped_tags.append("rating:" + rating)
            if ratings_only:
                clipped_tags.append("ratings only " + modelinfo['modelname'] + " ai generated tags")
            else:
                clipped_tags.append(modelinfo['modelname'] + " ai generated tags")

            # Write tags to Hydrus, then record the hash so we can resume later
            try:
                client.add_tags(hashes=[hash], service_keys_to_tags={
                    service_key: clipped_tags
                })
                # Only mark as done after a successful write
                log_result(hash, "OK")
                tagged_count += 1
                if limit:
                    bar.update(1)
                if limit and tagged_count >= limit:
                    debug(f"DEBUG: reached --limit {limit}; stopping")
                    break
            except Exception as e:
                log_result(hash, f"failed to add tags: {e}")
                skipped_count += 1
                continue

    # Batch finished cleanly. Strip the OK status from successful lines so the
    # log is a clean hash list for copy-paste. Failures keep their reason.
    try:
        with open(checkpoint_file) as f:
            lines = f.readlines()
        with open(checkpoint_file, "w") as f:
            for line in lines:
                stripped = line.rstrip("\n")
                if stripped.endswith("\tOK"):
                    f.write(stripped[:-3] + "\n")
                else:
                    f.write(line if line.endswith("\n") else line + "\n")
        debug("DEBUG: stripped OK status from successful hashes in session.log")
    except Exception as e:
        debug(f"DEBUG: failed to clean OK statuses: {e}")

    debug(f"DEBUG: batch complete — tagged {tagged_count} files, skipped {skipped_count} files — see session.log for details")
    # Mark the batch as finished so the next launch starts fresh by default.
    with open(complete_marker, "w") as f:
        f.write(f"tagged={tagged_count} skipped={skipped_count}\n")


if __name__ == '__main__':
    Image.init()
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    cli.add_command(evaluate)
    cli.add_command(evaluate_api)
    cli.add_command(evaluate_api_batch)
    cli()
