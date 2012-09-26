from bs4 import BeautifulSoup
import requests
import re
import time
import redis

r = redis.Redis()

#Url to fetch changes from
baseUrl = "http://redis.io/commands"

data = requests.get(baseUrl)

soup = BeautifulSoup(data.text)

commandUrls = []

for tag in soup.find_all('a'):
    link = tag['href']
    if "/commands/" in link:
        commandUrls.append(link)

fullCommandUrls = ["http://redis.io"+commandUrl for commandUrl in commandUrls]

pattern = "[2.]\.[4-9]+"
versions = re.compile(pattern)

workToDo = []

for url in fullCommandUrls:
    time.sleep(0.5)
    data = requests.get(url)
    soup = BeautifulSoup(data.text)
    commandText = soup.find('h1')
    for p in soup.find_all('p'):
        pstr = str(p)
        result = re.findall(pattern, pstr)
        if result:
            commandName = url.split("/")[-1]
            
            r.hmset(commandName, {'url':url, 'command':commandText, 'version':result, 'text':pstr})
            r.rpush('Affected commands', commandName)
            print "Work to do for", commandName, "version: ", result
            print 'Command Text : ', commandText
            
for item in workToDo:
    print item
    
 
    
