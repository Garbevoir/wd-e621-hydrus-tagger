# It's recommended to quickly read README-ORIGINAL.md, as that was the original readme file included with the tool. Specifically note the requirements section, as they are the same here.

If the root folder (the folder this .md file is in) has moved or has been renamed, delete the venv folder if it exists and follow first time installation instructions.

## FOR FIRST TIME INSTALLATION:
1. Open root folder (folder with this .md file) in cmd and run "python -m venv venv" without quotes
2. Run start.bat in your command line to open the venv
3. Type "pip install -r requirements.txt" and press enter

## DOWNLOADING THE MODELS:
This edit of the tool specifically uses local downloads of the model instead of cache downloads from the internet. This means you will need to download the models yourself. You can find the models by navigating to their specific folder in the models folder and reading the .txt file.

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



## RANDOM INFO:
Everything has been edited to work on a Windows 10 Pro installation. Your mileage may vary on other operating systems.
If you do run into problems on other operating systems, the culprit is likely in interrogate.py, specifically where path() is invoked or it's something to do with the .bat files and how they're written.

e621.bat uses an edited \_\_main__.py and interrogate.py that doesn't have any ratings handling as the e621 model doesn't tag ratings.
ratings.bat runs the normal wd model which DOES tag ratings, but discards all tags except for the ratings.
It's recommended to run ratings.bat AFTER running e621.bat so that furry art can be tagged with more accurate tags as well as a rating tag.
Note that this is UNNECESSARY if wd.bat is ran on the file FIRST, as it will already have a rating tag.

All modules have been edited to automatically add an "ai generated tags" tag to the file thats specific to which tagger was run.
All .bat files use evaluate-api-batch, meaning to check individual files you MUST use hashes.txt.

If you don't need furry or rating tagging capability, simply delete e621.bat/ratings.bat, as well as the e621-hydrus-tagger folder folder
You can also delete the Z3D-E621-Convnext folder from the models folder if not needed.

My personal workflow is to have a hydrus search page that excludes all AI tags, filters to only PNG/JPG/WEBP images, and only images with less than 10 tags already (to avoid tagging already well-tagged files.) I also limit the results to around 2048 images, since that takes roughly an hour to process on my system.
After tagging EVERYTHING with wd.bat, there will be some files that have been tagged with "furry" or "female furry".
I then have another search page that collects all these newly identified furry files, and I run e621.bat on them after a sufficient amount is identified.

I personally don't understand the difference between the different ViT/Convnext/MOAT tagging models, and since ViT was the default included with the tool, it's what I've been using.
If you prefer a different model for some reason, then just replace the "model.onnx" and "selected_tags.csv" files in the "wd-v1-4-vit-tagger-v2" folder with the ones you downloaded. I don't recommend renaming the folder, since the program looks specifically for the "wd-v1-4-vit-tagger-v2" folder to find the model.

You can have each .bat send the tags to their own personal tag service if you'd like, just create a new tag service and change the .bat file to point to the new tag service. This might be useful if you want to delete wd-hydrus-tagger tags from furry files, or delete a tag service if/when a new, better tagging model for anime/furry art comes out so you can re-tag everything.


YOU MUST REBUILD THE VENV IF YOU MOVE OR RENAME THIS FOLDER

# CREDITS:
- SmilingWolf for the WD tagging models. (https://huggingface.co/SmilingWolf)
- Abtalerico for the well made original tool that I poorly edited to make this. (https://github.com/abtalerico/wd-hydrus-tagger
- Zack3d (furzacky) for the E621 tagging model. (https://discord.com/channels/754509198674362388/1065785788698218526) (https://discord.gg/BDFpq9Yb7K)
- Hydrus Dev for developing and improving hydrus nonstop for several years, the real G.O.A.T. (https://hydrusnetwork.github.io/hydrus/index.html)
