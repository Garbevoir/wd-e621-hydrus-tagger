# README-ORIGINAL.md is here for legacy purposes. It's information is quite outdated. See below for up-to-date help.

If the root folder (the folder this .md file is in) has moved or has been renamed, delete the venv folder if it exists and follow first time installation instructions.

## REQUIREMENTS:
The original requirements for this tool called for either python 3.9.x or 3.10.x. However, I have gotten it to build in it's current form on python 3.11 (pip 22.3). As such, I recommend using python 3.11 to build. You should NOT use python 3.12 as it has removed distutils, which is necessary for some of the dependencies and I don't know how I'd go about fixing everything that has broken. Sorry. Anyways:

* Python 3.11.x
* Git 2.45.2 or later
* Hydrus Network with API key
* A willingness to google stuff when things go wrong


## FOR FIRST TIME INSTALLATION:
1. Open the root folder (folder with this .md file) in cmd and run "python -m venv venv" without quotes
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
4. Save your changes
5. Repeat steps 2 through 4 with e621.bat and ratings.bat

# Now you should be prepared and ready to start automatically tagging files. 
I recommend starting with a single file or a small group of files, and testing wd.bat, e621.bat, and ratings.bat individually. Make sure the tags are being put into your AI tagging service, that tag siblings/parents are displaying correctly, and that the file is properly tagged as being AI tagged. If all is well, you can proceed to mass tagging.

## (OPTIONAL) CONVENIENCE CHANGE:
1. In the folder this .md file is in, navigate to venv\Scripts\
2. Open activate.bat in a text editor
3. At the bottom of the file, add "cmd /k" to a new line
   
You can now double-click start.bat to automatically open the venv.

## (OPTIONAL) ENABLING GPU USE:
The program does not have GPU utilization capability by default due to the necessary files having to be sourced from elsewhere. To enable GPU use for windows installations:
1. Install [CUDA 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive). You only need the runtime libraries, and you can uncheck the other install options. Alternatively, just do the express installation.
2. add "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin" to your Windows PATH environment variable. There are several guides online on how to do this, it isn't that hard.
3. download the [cuDNN 8.9.2 for CUDA 11.x](https://developer.nvidia.com/rdp/cudnn-archive) windows archive, and extract it to a safe location. I recommend putting the folders from the archive in "C:\Program Files\NVIDIA\CUDNN\v8.9.2", as this matches where Nvidia installs cuDNN when installed through an automatic installer.
4. add "C:\Program Files\NVIDIA\CUDNN\v8.9.2\bin" to your Windows PATH environment variable.
5. Download [zlib123dllx64.zip](https://forums.developer.nvidia.com/uploads/short-url/e76PYqafTHaGM1XQhQumCSL4vqb.zip) and extract the files to a temporary location
6. copy zlibwapi.dll from inside the dll_x64 folder, and place it inside the "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin" folder.

With all this done, you should be able to utilize the GPU when tagging. To enable GPU utilization, set the CPU option to 0. I recommend testing just as you would on a first install, with a small amount of test hashes. There's chance of an error, but from my experience this doesn't necessarily mean the GPU isn't being utilized. Really, just take the ETA time when CPU is set to 1 and compare to when it's set to 0, and see if it's noticeably faster. If so, then the GPU is being utilized.

### Additional note on enabling GPU use with latest tagging models
To enable GPU use for *wd-v3* SmilingWolf models, such as [wd-eva02-large-tagger-v3](https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3) or [wd-swinv2-tagger-v3](https://huggingface.co/SmilingWolf/wd-swinv2-tagger-v3) you will need to use updated versions of CUDA (12.x) and cuDNN (9.x).

> [!WARNING] 
> This was tested with Python 3.11.9; CUDA 12.6.3; cuDNN 9.5.1; onnxruntime-gpu 1.20.1
>
> If you willing to test it with other 12.x CUDA and 9.x cuDNN installations please refer to [onnxruntime dependencies table](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements)

- Install [CUDA Toolkit 12.6.3](https://developer.nvidia.com/cuda-toolkit-archive); as said above, you only need runtime libraries, so please uncheck other install options if you want to reduce the size of installation.
- Check if CUDA installer properly added binaries to your Windows PATH:
	- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin`
  	- and `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\libnvvp`
- Install [cuDNN 9.5.1](https://developer.nvidia.com/cudnn-archive); by default cuDNN install libraries for both CUDA 11.8 and CUDA 12.6, you can uncheck 11.8 if you don't need it.
	- **VERY IMPORTANT!** The installer automatically adds only `\bin\` folder to your Windows PATH which is incorrect!
	- To make it correct you need to edit the Windows PATH variable to according to CUDA version you are using, so it should look like this `C:\Program Files\NVIDIA\CUDNN\v9.5\bin\12.6` please **double check** this PATH to avoid issues.
- Additionally make sure that you have all possible **Visual C++ Redistributables** installed on your system, decent source for all-in-one package can be found [here](https://github.com/abbodi1406/vcredist) if you don't want to install each one of them manually.
- After you make sure that PATH variables are correct you can utilize your GPU for tagging. If you followed the initial preparation/setup steps correctly — refer to the instructions below on how to add different models. Once you edited your wd.bat to use `--cpu 0` it should automatically install latest onnxruntime-gpu to your venv on the first run.

## FOR NORMAL USE:
1. Open command line in the root folder and type start.bat or double-click if the convenience change has been made
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
  --model TEXT       The tagging model folder to use
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
  --model TEXT        The tagging model folder to use
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
  --model TEXT        The tagging model folder to use
  --threshold FLOAT   The threshhold to drop tags below
  --host TEXT         The URL for your Hydrus server
  --tag-service TEXT  The tag service to send tags that match the threshold to
  --ratings-only BOOL Drop all tags except for those that identify the content rating
  --privacy BOOL      Show or hide the tag output to the cli
```
### Evaluate files with specified tags
```bash
python -m wd-hydrus-tagger evaluate-api-search --token your_hydrus_token "tag 1" "tag 2"...
```
#### Options:
```
  --token TEXT              The API token for your Hydrus server
  --cpu BOOLEAN             Use CPU instead of GPU
  --model TEXT              The tagging model folder to use
  --threshold FLOAT         The threshhold to drop tags below
  --host TEXT               The URL for your Hydrus server
  --tag-service TEXT        The tag service to send tags that match the threshold to.
  --search-tag-service TEXT The tag service that specified tags will be searched within.
  --ratings-only BOOL       Drop all tags except for those that identify the content rating
  --privacy BOOL            Show or hide the tag output to the cli
```
## RANDOM INFO:
Everything has been confirmed to work on various Windows 10 installations. I've also read about other people getting everything (except GPU utilization) working on various linux distributions by changing the .bat files.
If you do run into problems on other operating systems, the culprit is likely in interrogate.py, specifically where path() is invoked or it's something to do with the .bat files and how they're written.

e621.bat uses an e621 model that doesn't tag content ratings but should provide much more accurate tags for furry artwork. For example, where an anthropomorphic dragon would be tagged "demon girl" by the WD tagger, e621 will properly recognize it as an anthropomorphic dragon and tag it as such.
ratings.bat runs the normal WD model which DOES tag ratings, but discards all tags except for the ratings.
It's recommended to run ratings.bat AFTER running e621.bat so that furry art can be tagged with more accurate tags as well as a rating tag.
Note that this is UNNECESSARY if wd.bat is ran on the file FIRST, as it will already have a rating tag. (unless you decide to delete the WD tags afterwards)

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

Python 3.12 seems to have severely broken some of the dependencies used by this tool. Perhaps with enough fiddling and changing required package versions it might work, but it's much easier to just use python 3.11. python 3.10 might also work, but I believe the latest version of onnxruntime as well as a couple other packages that were updated require atleast python 3.11.

I tested and confirmed that cuDNN 8.9.7 also works without issue, however as the onnxruntime documentation specifically calls for cuDNN 8.9.2, it's what i've listed in the setup instructions.

I've read that "zlibwapi.dll" often exists elsewhere in windows installations, including in Nvidia Nsight installations (renamed to zlib.dll). I don't know if these would work, but they might do the trick if you can't/don't want to download the file separately. 

YOU MUST REBUILD THE VENV IF YOU MOVE OR RENAME THIS FOLDER

# CREDITS:
- SmilingWolf for the WD tagging models as well as some simple code to detect Kaomojis. (https://huggingface.co/SmilingWolf)
- Abtalerico for the well made original tool that I poorly edited to make this. (https://github.com/abtalerico/wd-hydrus-tagger) (deleted, copy can be found at  https://github.com/Garbevoir/wd-e621-hydrus-tagger/tree/main)
- Zack3d (furzacky) for the E621 tagging model. (https://discord.com/channels/754509198674362388/1065785788698218526) (https://discord.gg/BDFpq9Yb7K)
- This moderator on the Nvidia developer forums for providing safe downloads for zlibwapi.dll. (https://forums.developer.nvidia.com/t/could-not-load-library-cudnn-cnn-infer64-8-dll-error-code-193/218437/16)
- Hydrus Dev for developing and improving hydrus nonstop for several years, the real G.O.A.T. (https://hydrusnetwork.github.io/hydrus/index.html)
