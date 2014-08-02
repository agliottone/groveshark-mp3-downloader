#!/usr/bin/env python
import httplib
import StringIO
import hashlib
import uuid
import random
import string
import sys
import os
import subprocess
import gzip
import io
import threading
if sys.version_info[1] >= 6:  import json
else: import simplejson as json

folder = os.path.dirname(os.path.realpath(__file__))

_useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"
_token = None

URL = "grooveshark.com" #The base URL of Grooveshark
htmlclient = ('htmlshark', '20130520', 'nuggetsOfBaller', {"User-Agent":_useragent, "Content-Type":"application/json", "Accept-Encoding":"gzip"}) #Contains all the information posted with the htmlshark client
jsqueue = ['jsqueue', '20130520', 'chickenFingers']
jsqueue.append({"User-Agent":_useragent, "Referer": 'http://%s/JSQueue.swf?%s' % (URL, jsqueue[1]), "Accept-Encoding":"gzip", "Content-Type":"application/json"}) #Contains all the information specific to jsqueue

#Setting the static header (country, session and uuid)
h = {}
h["country"] = {}
h["country"]["CC1"] = 72057594037927940
h["country"]["CC2"] = 0
h["country"]["CC3"] = 0
h["country"]["CC4"] = 0
h["country"]["ID"] = 57
h["country"]["IPR"] = 0
h["privacy"] = 0
h["session"] = (''.join(random.choice(string.digits + string.letters[:6]) for x in range(32))).lower()
h["uuid"] = str.upper(str(uuid.uuid4()))

#The string that is shown when the program loads
entrystring = \
"""A Grooveshark song downloader in python
by George Stephanos <gaf.stephanos@gmail.com>
"""

#Generate a token from the method and the secret string (which changes once in a while)
def prepToken(method, secret):
    rnd = (''.join(random.choice(string.hexdigits) for x in range(6))).lower()
    return rnd + hashlib.sha1('%s:%s:%s:%s' % (method, _token, secret, rnd)).hexdigest()

#Fetch a queueID (right now we randomly generate it)
def getQueueID():
    return random.randint(10000000000000000000000,99999999999999999999999) #For now this will do

#Get the static token issued by sharkAttack!
def getToken():
    global h, _token
    p = {}
    p["parameters"] = {}
    p["parameters"]["secretKey"] = hashlib.md5(h["session"]).hexdigest()
    p["method"] = "getCommunicationToken"
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    conn = httplib.HTTPSConnection(URL)
    conn.request("POST", "/more.php", json.JSONEncoder().encode(p), htmlclient[3])
    _token = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

#Process a search and return the result as a list.
def getResultsFromSearch(query, what="Songs"):
    p = {}
    p["parameters"] = {}
    p["parameters"]["type"] = what
    p["parameters"]["query"] = query
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("getResultsFromSearch", htmlclient[2])
    p["method"] = "getResultsFromSearch"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    j = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())
    try:
        return j["result"]["result"]["Songs"]
    except:
        return j["result"]["result"]

#Get all songs by a certain artist
def artistGetSongsEx(id, isVerified):
    p = {}
    p["parameters"] = {}
    p["parameters"]["artistID"] = id
    p["parameters"]["isVerifiedOrPopular"] = isVerified
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("artistGetSongsEx", htmlclient[2])
    p["method"] = "artistGetSongsEx"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())

#Get the streamKey used to download the songs off of the servers.
def getStreamKeyFromSongIDs(id):
    p = {}
    p["parameters"] = {}
    p["parameters"]["type"] = 8
    p["parameters"]["mobile"] = False
    p["parameters"]["prefetch"] = False
    p["parameters"]["songIDs"] = [id]
    p["parameters"]["country"] = h["country"]
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("getStreamKeysFromSongIDs", jsqueue[2])
    p["method"] = "getStreamKeysFromSongIDs"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

#Add a song to the browser queue, used to imitate a browser
def addSongsToQueue(songObj, songQueueID, source = "user"):    
    queueObj = {}
    queueObj["songID"] = songObj["SongID"]
    queueObj["artistID"] = songObj["ArtistID"]
    queueObj["source"] = source
    queueObj["songQueueSongID"] = 1
    p = {}
    p["parameters"] = {}
    p["parameters"]["songIDsArtistIDs"] = [queueObj]
    p["parameters"]["songQueueID"] = songQueueID
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("addSongsToQueue", jsqueue[2])
    p["method"] = "addSongsToQueue"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

#Remove a song from the browser queue, used to imitate a browser, in conjunction with the one above.
def removeSongsFromQueue(songQueueID, userRemoved = True):
    p = {}
    p["parameters"] = {}
    p["parameters"]["songQueueID"] = songQueueID
    p["parameters"]["userRemoved"] = True
    p["parameters"]["songQueueSongIDs"]=[1]
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("removeSongsFromQueue", jsqueue[2])
    p["method"] = "removeSongsFromQueue"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

#Mark the song as being played more then 30 seconds, used if the download of a songs takes a long time.
def markStreamKeyOver30Seconds(songID, songQueueID, streamServer, streamKey):
    p = {}
    p["parameters"] = {}
    p["parameters"]["songQueueID"] = songQueueID
    p["parameters"]["streamServerID"] = streamServer
    p["parameters"]["songID"] = songID
    p["parameters"]["streamKey"] = streamKey
    p["parameters"]["songQueueSongID"] = 1
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("markStreamKeyOver30Seconds", jsqueue[2])
    p["method"] = "markStreamKeyOver30Seconds"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

#Mark the song as downloaded, hopefully stopping us from getting banned.
def markSongDownloadedEx(streamServer, songID, streamKey):
    p = {}
    p["parameters"] = {}
    p["parameters"]["streamServerID"] = streamServer
    p["parameters"]["songID"] = songID
    p["parameters"]["streamKey"] = streamKey
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("markSongDownloadedEx", jsqueue[2])
    p["method"] = "markSongDownloadedEx"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

if __name__ == "__main__":
    if len(sys.argv) < 2: #Check if we were passed any parameters
        import gui
        gui.main() #Open the gui
        exit() #Close the command line
    print entrystring #Print the welcome message
    print "Initializing..."
    i = ' '.join(sys.argv[1:]).strip()
    if os.path.isfile(folder +'/' + i + '.json'):
    	json_data=open(folder +'/' + i + '.json')
    	data = json.load(json_data)
    	json_data.close()
    	for item in data:
    		NAME = item['title']
    		NAMEFILE =  "%s/%s.mp3" %(folder,NAME)
    		if os.path.isfile(NAMEFILE.encode('utf-8')):
    			item['link'] = NAME +".mp3"
    		else:
    			item['link'] = False
    	f = io.open(folder +'/' + i + '.json','w', encoding='utf-8')
    	f.write(unicode(json.dumps(data, ensure_ascii=False)))
    	f.close()
    	print data
    	exit()

    getToken() #Get a static token
    
    #i = raw_input("Search: ") #Same as above, if you uncomment this, and comment the first 4 lines this can be run entirely from the command line.
    print "Searching for '%s'..." % i
    m = 0
    s = getResultsFromSearch(i) #Get the result from the search
    r =[]
    print s
    for m,l in enumerate(s):
        if os.path.isfile(folder + "/" + l["SongName"].encode('utf-8')  +".mp3"):
            link = l["SongName"] +".mp3"
        else:
            link = False
        item = {'title':l["SongName"], 'album':  l["AlbumName"], 'artist': l["ArtistName"], 'id':l['SongID'], 'q':i,'download':False, 'link':link}
        r.append(item)
    if r == []:
        pass
    else:
    	pass
    f = io.open(folder +'/' + i + '.json','w', encoding='utf-8')
    f.write(unicode(json.dumps(r, ensure_ascii=False)))
    f.close()
    print r
    exit()

exit()