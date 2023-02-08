# wd1.4-hydrus-tagger
wd1.4-hydrus-tagger is a tool that uses the [Hydrus Network](https://github.com/hydrusnetwork/hydrus) API to tag images with [the WD 1.4 Tagger model](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2).

## Requirements
* Python 3.9.x or 3.10.x
* Hydrus Network and an API key for your server

## Installing Dependencies
```bash
python -m venv venv # life is easier with a venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
### Evaluate a file
```bash
python -m wd-hydrus-tagger evaluate /path/to/file
```
Options:
```
  --cpu BOOLEAN      Use CPU instead of GPU
  --model TEXT       The tagging model version to use
  --threshold FLOAT  The threshhold to drop tags below
  --help             Show this message and exit.
```