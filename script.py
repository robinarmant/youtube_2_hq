# Requirements : pip install BeautifulSoup 

from BeautifulSoup import BeautifulSoup as BS
import urllib2
import os.path as op
import os
import requests
from requests.exceptions import HTTPError
from string import *
import unicodedata
import re
import numpy as np
import commands

def get_track():
	###READ THE FILE CONTAINING URL TO DL
	with open(op.join(os.getcwd(), "example.txt"), 'r') as to_dl:
		to_dl_lines = to_dl.readlines()
		url_list = [str(tdl.split(' ')[0]) for tdl in to_dl_lines]
		comment_list = [str(tdl.split(' ', 1)[1]) for tdl in to_dl_lines]
		to_dl.close()


	for main_index, main_url in enumerate(url_list):
		print "#####################################"
		print "getting ready to download a new track"
		print "comment %s" % (comment_list[main_index])

		#########################################
		### BUILD THE MONKEY SEARCH REQUEST FROM YOUTUBE URL
		#get the youtube name of the track
		html = urllib2.urlopen(main_url)
		soup = BS(html)
		elem  = soup.findAll("meta",{"name": "title"})

		if "='" in str(elem[0]):
			track_name = str(elem[0]).split("\'")[-2].lower()
		else:
			track_name = str(elem[0]).split('\"')[-2].lower()

		#keeping only artist and track name
		track_name = track_name.split("(")[0]
		print "going to ask monkey if he know this track :", track_name
		print "\n"


		#get the length of the youtube track
		length_text = str(soup.findAll("script"))
		index = length_text.find('"length_seconds"')
		yt_length = int(length_text[index+len('"length_seconds"')+2:index+len('"length_seconds"')+5])
		print "duration of the track: ", yt_length

		#convert it to ascii to remove potential accents
		unicode_name = unicode(track_name,'utf-8')
		nfkd_form = unicodedata.normalize('NFKD', unicode_name)
		only_ascii = nfkd_form.encode('ASCII', 'ignore')

		#transform any punctuation sign in underscore sign to fit monkeymp3 request
		intab = " \"()-'#,.?!"
		outtab = "___________"
		trantab = maketrans(intab, outtab)
		remove_punc = only_ascii.translate(trantab)

		#remove repeating underscore and last underscore if any
		final = re.sub(r'(_)\1+', r'\1', remove_punc)  
		if final[-1] == "_": final = final[:-1]


		#build the search request
		monkey_url = "http://mp3monkey.net/mp3/" + final + ".html"

		#########################################
		###GET THE RIGHT FILE FROM THE SEARCH URL
		#get list of dl urls from the search results
		search_html = urllib2.urlopen(monkey_url)
		soup = BS(search_html)
		elem  = soup.findAll("a",{"class": "button blue small d3 downloadButton"})
		try :
			dl_url = [str(elem[i]).split(" ")[-1].split("\"")[1] for i in range(0, len(elem))]
		except :
			print "Couldn't download the track named %s" % track_name
			continue
		if len(dl_url) == 0:
			print "the monkey doesn't have this track, sorry!"
			continue

		#get lengths in seconds of tracks sent by monkey
		length = soup.findAll("div",{"class": "floatRight"})
		monkey_lengths = [str(length[i]).split("\t")[-1].split("<")[0][0:-1] for i in range(0,len(length))]
		monkey_lengths_sec = [int(monkey_lengths[i].split(":")[0]) * 60 + int(monkey_lengths[i].split(":")[1]) for i in range(0,len(monkey_lengths))]

		#keep only monkey tracks that have the same length than the youtube track
		tolerance = 5
		print "we asked the monkey to check track duration with a tolerance of %s seconds" % (str(tolerance))
		print "\n"
		dl_url_good = []
		for i,l in enumerate(monkey_lengths_sec):
			if np.abs(l - yt_length) < 5:
				dl_url_good.append(dl_url[i])

		#get the mp3 urls and retrieve the max quality mp3
		current_max_size = 0
		for dug in dl_url_good:
			mp3_url = dug[:-1] + '2'
			#print mp3_url
			ind = str(commands.getstatusoutput("wget --referer=http://mp3monkey.net --spider %s" % '"' + mp3_url + '"')).find("Length")
			#print str(commands.getstatusoutput("wget --referer=http://mp3monkey.net --spider %s" % '"' + mp3_url + '"'))
			size = int(str(commands.getstatusoutput("wget --referer=http://mp3monkey.net --spider %s" % '"' + mp3_url + '"'))[ind:ind + 19].split(":")[-1].split("(")[0].split("[")[0])
			#print size
			if size>current_max_size:
				max_quality_url = mp3_url
				current_max_size = size

		#DL-DL-Dl-DL
		os.system("wget --referer=http://mp3monkey.net %s" % '"' + max_quality_url + '"')
		os.rename(op.join(os.getcwd(), max_quality_url.split("/")[-1]), op.join(os.getcwd(), final + ".mp3"))
		ind = str(commands.getstatusoutput("ffmpeg -i %s" % op.join(os.getcwd(), final + ".mp3"))).find(", bitrate:")
		try:
			quality = str(commands.getstatusoutput("ffmpeg -i %s" % op.join(os.getcwd(), final + ".mp3")))[ind+2:ind+19]
			print "best quality the monkey had for this track was:", quality
		except:
			print "install ffmpeg to get direct info about track quality"

		print "\n"
		print "#####################################"


if __name__ == '__main__':
    get_track()

