# youtube_2_hq
got a track you love on youtube? enter the url and download the higher bitrate mp3 file from the monkey

** how does it work?

fill the *example.txt* with youtube urls of tracks you love, following the model already existing in *example.txt*
(you can add comment in front of each url if you want)
then run in a terminal:

**ipython script.py**

** requirements
*** WARNING: this script only works on Unix systems
* this is a python script, you'll need python 2.7 installed to run it
* you need to have Beautiful Soup installed to get the script working : **pip install BeautifulSoup**
* install ffmpeg to get direct info about the bitrate of downloaded tracks
* this script will use wget to download tracks

