from bs4 import BeautifulSoup
import requests
import re
import time

#Url to fetch changes from
baseUrl = "http://redis.io/commands"

# We know something is a command because of the
# directory structure (redis uses redis.io/commands/srandmember
commandSeparator = "/commands/"

# Redis adds /commands/srandmember to command links
base = "http://redis.io"

# The regex to match version numbers with
# we only want versions that are 2.(4-9)
pattern = "[2.]\.[4-9]+"


data = requests.get(baseUrl)

soup = BeautifulSoup(data.text)

commandUrls = []

# Find all links in page
for tag in soup.find_all('a'):
    # get the link location
    link = tag['href']
    
    # Command separator is the way the commands are 
    # displayed in links (redis uses 'redis.io/commands/COMMANDNAME'
    if commandSeparator in link:
        commandUrls.append(link)

# Redis uses redirects instead of full link locations ('/commands/set'
# rather than 'redis.io/commands/set' so we need to add the base 'redis.io'
fullCommandUrls = [base+commandUrl for commandUrl in commandUrls]

# Compile our regex
versions = re.compile(pattern)

# If we find something that matches our regex,
# we will put it into the array to know that this
# command was updated in recent versions
workToDo = []

for url in fullCommandUrls:
    # don't destroy the server
    time.sleep(0.5)
    
    data = requests.get(url)
    soup = BeautifulSoup(data.text)
    
    # The command text in redis is at the top,
    # given in the H1 tag
    commandText = soup.find('h1')
    for p in soup.find_all('p'):
        pstr = str(p)
        result = re.findall(pattern, pstr)
        if result:
            # Get the command name by splitting on '/' and taking the last member
            commandName = url.split("/")[-1]
            commandJSON  = {'commandName':commandName, 'url':url, 'command':commandText, 'version':result, 'text':pstr}
            
            workToDo.append(commandJSON)
            
            # if you want to log in a redis instance to display somewhere
            # r.hmset(commandName, commandJSON) 
            # r.lpush('Commands', commandName)
            print "Work to do for", commandName, "version: ", result
            print 'Command Text : ', commandText

for item in workToDo:
    print item
    
 
    
