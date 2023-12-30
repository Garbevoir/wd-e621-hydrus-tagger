# README-ORIGINAL.md is here for legacy purposes. It's information is quite outdated. See below for up-to-date help.

If the root folder (the folder this .md file is in) has moved or has been renamed, delete the venv folder if it exists and follow first time installation instructions.

## REQUIREMENTS:
The original requirements for this tool called for either python 3.9.x or 3.10.x. However, I have gotten it to build in it's current form on python 3.11 (pip 22.3). As such, I recommend using python 3.11 to build. You should NOT use python 3.12 as it has removed distutils, which is necessary for some of the dependencies and I don't know how I'd go about fixing everything that has broken. Sorry. Anyways:

* Python 3.11.x
* Hydrus Network with API key
* A willingness to google stuff when things go wrong

## FOR FIRST TIME INSTALLATION:
1. Open root folder (folder with this .md file) in cmd and run "python -m venv venv" without quotes
2. Run start.bat in your command line to open the venv
3. Type "pip install -r requirements.txt" and press enter

## DOWNLOADING THE MODELS:
This edit of the tool specifically uses local downloads of the model instead of cache downloads from the internet. This means you will need to download the models yourself. You can find the models by navigating to their specific folder in the models folder and reading the .txt file.

## INFO.JSON:
In the two pre-made model folders are info.json files. These inform the tagger of what tagging model is being loaded as well as what it's capabilities are. This is important for certain functions such as tagging only the content rating (safe, explicit, etc.) If you want to use new models that don't have a folder created by default, all you need to do is make a new folder with the new model's .onnx and .csv file in it, then create an info.json with the correct info for it.

## HYDRUS PREPARATION:
1. In Hydrus, navigate to services > manage services
2. Click "add" and select "local tag service"
3. Name your service "A.I. Tags" (or whatever you want)
4. Click apply, then click apply in manage services
5. Now navigate to services > review services
6. Nagivate to local > client api
7. Click "add", select "manually"
8. Name the new api something identifiable like "AI tagging API"
9. Click the check box next to the "edit file tags" and "search and fetch files" permissions
10. Click apply, you can close review services now as well

While optional, it's recommended to migrate tag parents and tag siblings from the PTR to the new tag service to ensure consistent tag naming, as well as more detailed tagging.
to do so:

1. Navigate to tags > migrate tags
2. Under content, select "tag parents"
3. Under source, select "public tag repository"
4. Under filter, ensure it says "current" and under action ensure it says "add"
5. Under destination, select "A.I. Tags" (or whatever you named the new service)
6. Click "Go!" and wait for it to finish
7. Repeat steps 2 through 6, but under content select "tag siblings"

## .BAT FILE PREPARATIONS:
There are 4 .bat files, start.bat, e621.bat, wd.bat, and ratings.bat. start.bat should not be edited.
1. Open wd.bat in a text editor
2. Replace "REPLACE_WITH_API_KEY" with your the key to the api you made previously
   - If you dont have your API key:
	- a. Go to hydrus
	- b. Navigate to services > review services
	- c. Navigate to local > client api
	- d. Click your AI tagging API from the list
	- e. Click "copy api access key"
	- f. now paste the access key from your clipboard to the .bat file
3. (optional) If necessary, replace "A.I. Tags" with the name of your tag service (keep the quotes)
4. (optional) Review if you're capable of using your GPU for AI work. In my personal case I am not, but if you can, you can try changing "--cpu 1" to "--cpu 0". If you can't it should default to CPU processing anyways, giving you an ugly but ignorable error.
5. Save your changes
6. Repeat steps 2 through 5 with e621.bat and ratings.bat


## COMPLETELY OPTIONAL CONVENIENCE CHANGE:
1. In the folder this .md file is in, navigate to venv\Scripts\
2. Open activate.bat in a text editor
3. At the bottom of the file, add "cmd /k" to a new line
   
You can now double-click start.bat to automatically open the venv.


# Now you should be prepared and ready to start automatically tagging files. 
I recommend starting with a single file, and testing wd.bat, e621.bat, and ratings.bat individually. Make sure the tags are being put into your AI tagging service, that tag siblings/parents are displaying correctly, and that the file is properly tagged as being AI tagged. If all is well, you can proceed to mass tagging.


## FOR NORMAL USE:
1. Open command line and type start.bat or double-click if able
2. With Hydrus OPEN:
	- a. Copy a list of sha256 hashes from Hydrus (right click on file, navigate to share > copy > hash/hashes > sha256)
	- b. Paste list into hashes.txt
	- c. Replace all the "sha256:" in the txt file with nothing, should just be the hash on each line, no spaces
3. Run wd.bat from command line OR if doing specifically furry art, run e621.bat
4. (optional) If you need or want to, you can run ratings.bat to only get ratings tags, no content tags


## Running in CLI
### Evaluate a file
```bash
python -m wd-hydrus-tagger evaluate /path/to/file
```
#### Options:
```
  --cpu BOOLEAN      Use CPU instead of GPU
  --model TEXT       The tagging model to use
  --threshold FLOAT  The threshhold to drop tags below
```

### Evaluate a file in Hydrus
```bash
python -m wd-hydrus-tagger evaluate-api --token your_hydrus_token 123_your_files_hash_456
```
#### Options:
```
  --token TEXT        The API token for your Hydrus server
  --cpu BOOLEAN       Use CPU instead of GPU
  --model TEXT        The tagging model to use
  --threshold FLOAT   The threshhold to drop tags below
  --host TEXT         The URL for your Hydrus server
  --tag-service TEXT  The tag service to send tags that match the threshold to
  --ratings-only BOOL Drop all tags except for those that identify the content rating
  --privacy BOOL      Show or hide the tag output to the cli
```

### Evaluate a number of files in Hydrus
```bash
python -m wd-hydrus-tagger evaluate-api-batch --token your_hydrus_token hashes.txt
```
Where hashes.txt is a file containing one Hydrus file hash per line.

#### Options:
```
  --token TEXT        The API token for your Hydrus server
  --cpu BOOLEAN       Use CPU instead of GPU
  --model TEXT        The tagging model to use
  --threshold FLOAT   The threshhold to drop tags below
  --host TEXT         The URL for your Hydrus server
  --tag-service TEXT  The tag service to send tags that match the threshold to
  --ratings-only BOOL Drop all tags except for those that identify the content rating
  --privacy BOOL      Show or hide the tag output to the cli
```

## RANDOM INFO:
Everything has been edited to work on a Windows 10 Pro installation. Your mileage may vary on other operating systems.
If you do run into problems on other operating systems, the culprit is likely in interrogate.py, specifically where path() is invoked or it's something to do with the .bat files and how they're written.

e621.bat uses an e621 model that doesn't tag ratings.
ratings.bat runs the normal wd model which DOES tag ratings, but discards all tags except for the ratings.
It's recommended to run ratings.bat AFTER running e621.bat so that furry art can be tagged with more accurate tags as well as a rating tag.
Note that this is UNNECESSARY if wd.bat is ran on the file FIRST, as it will already have a rating tag. (unless you decide to delete the wd tags afterwards

All modules have been edited to automatically add an "ai generated tags" tag to the file thats specific to which tagger was run.
All .bat files use evaluate-api-batch, meaning to check individual files you MUST use hashes.txt or enter the command yourself.

If you don't need furry or rating tagging capability, simply delete e621.bat/ratings.bat, as well as the Z3d-E621-Convnext folder

My personal workflow is to have a hydrus search page that excludes all AI tags, filters to only PNG/JPG/WEBP images, and only images with less than 10 tags already (to avoid tagging already well-tagged files.) I also limit the results to around 2048 images, since that takes roughly an hour to process on my system.
After tagging EVERYTHING with wd.bat, there will be some files that have been tagged with "furry" or "female furry".
I then have another search page that collects all these newly identified furry files, and I run e621.bat on them after a sufficient amount is identified.

I personally don't understand the difference between the different ViT/Convnext/MOAT tagging models, and since ViT was the default included with the tool, it's what I've been using.

If you prefer a different model for some reason, then just create a new folder in the /model/ folder, put your .onnx and .csv file in there, then copy and paste an info.json from another folder and edit it appropriately. Then you can edit or copy wd.bat and change the folder being pointed to from "wd-v1-4-vit-tagger-v2" to whatever you named your new folder. alternatively, you could just replace the "model.onnx" and "selected_tags.csv" files in the "wd-v1-4-vit-tagger-v2" folder with the ones you downloaded. I don't recommend this since it could lead to confusion on what model is actually being ran as well as overwriting the original tagging model, but if it's similar enough it should work okay.

You can have each .bat send the tags to their own personal tag service if you'd like, just create a new tag service and change the .bat file to point to the new tag service. This might be useful if you want to delete wd-hydrus-tagger tags from furry files, or delete a tag service if/when a new, better tagging model for anime/furry art comes out so you can re-tag everything.

As of the latest version of this tagging tool, the way that the "ai generated tags" tags are made is different, meaning they very likely wont match the tags given to already processed files. I recommend sibling-ing the previous tag to the newly created one, or vice versa.

Ages ago I tried setting up the required tools to utilize my GPU for tagging. Unfortunately I've forgotten most of the steps to accomplish this, but what I remembered involved installing software outside the venv from nvidia. I also remember that it's not possible to include the software with the venv via requirements.txt. The results were actually pretty good, I went from processing 2048 files in 2 hours to doing 8192 in about the same amount of time. Of course, my GPU sounded like a jet engine the entire time, so I don't really recommend it if you plan to run it all night. 

Python 3.12 seems to have severely broken some of the dependencies used by this tool. Perhaps with enough fiddling and changing required package versions it might work, but it's much easier to just use python 3.11. python 3.10 might also work, but I believe the latest version of onnxruntime as well as a couple other packages that were updated require atleast python 3.11.

YOU MUST REBUILD THE VENV IF YOU MOVE OR RENAME THIS FOLDER

# CREDITS:
- SmilingWolf for the WD tagging models. (https://huggingface.co/SmilingWolf)
- Abtalerico for the well made original tool that I poorly edited to make this. (https://github.com/abtalerico/wd-hydrus-tagger) (deleted, copy can be found at  https://github.com/Garbevoir/wd-e621-hydrus-tagger/tree/main)
- Zack3d (furzacky) for the E621 tagging model. (https://discord.com/channels/754509198674362388/1065785788698218526) (https://discord.gg/BDFpq9Yb7K)
- Hydrus Dev for developing and improving hydrus nonstop for several years, the real G.O.A.T. (https://hydrusnetwork.github.io/hydrus/index.html)
