
import json
import re
#youtube stuff imported
import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import time


#discord stuff imported
import discord #gets the discord and asyncio librarys
import asyncio



##problems
#unsure what will happen in a headless enviroment if the oauth hasnt been set
##if the token and you input a invalid token the first time it will continue to say invalid token for tokens that are even valid



##ideas
#possiblity of use of file io to get the information of the client token for discord and stuff.
#use regex to help format the chat (honestly not needed)


##youtube chat porition
#this will handle getting chat from youtube which will then be pushed to discord

#!/usr/bin/python




####variables
config = {"channelName": "", "pageToken": "", "serverName": "", "discordToken": "","discordToYoutubeFormating": "", "youtubeToDiscordFormatting":""}

botName = "none"

botUserID = "empty"

youtube = ""

firstRun = "off"

#used as global varibles and were defined before we start using them to avoid problems down the road
channelToUse = ""


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

# Retrieve a list of the liveStream resources associated with the currently
# authenticated user's channel.

def getLiveId(youtube): #this gets the live chat id
  global liveChatId,botUserID #pulls in the bots livechatid and botuserid for further saving and modifying
  
  list_streams_request = youtube.liveBroadcasts().list( #checks for the live chat id through this
    part="snippet", #this is what we look through to get the live chat id
    broadcastStatus="all", #we need both of these to get the live chat id
    broadcastType="all"
  ).execute() #executes it so its not just some object
  liveChatId = list_streams_request["items"][0]["snippet"]["liveChatId"]#sifts through the output to get the live chat id and saves it
  botUserID = list_streams_request["items"][1]["snippet"]["channelId"] #saves the bots channel user id that we will use as a identifier
  print("liveID {0}".format(liveChatId)) #print the live chat id
  
 
  

async def listChat(youtube):
  global pageToken #pulls in the page token
  global liveChatId #pulls in the liveChatID
  global botUserID #pulls in the bots channel ID
  global config
  list_chatmessages = youtube.liveChatMessages().list( #lists the chat messages
    part="id,snippet,authorDetails", #gets the author details needed and the snippet all of which giving me the message and username
    liveChatId=liveChatId,
    maxResults=500,
    pageToken=config["pageToken"] #gives the previous token so it loads a new section of the chat
  ).execute() #executes it so its not just some object

  config["pageToken"] = list_chatmessages["nextPageToken"] #page token for next use
   
  #print(list_chatmessages)
  
  msgCheckRegex = re.compile(r'[*:]') #setup for if we happen to need this it should never change either way
  for temp in list_chatmessages["items"]: #goes through all the stuff in the list messages list
    message = temp["snippet"]["displayMessage"] #gets the display message
    username = temp["authorDetails"]["displayName"] #gets the users name
    userID = temp["authorDetails"]["channelId"]
    if message != "" and username != "": #this makes sure that the message and username slot arent empty before putting this to the discord chat        
        if userID != botUserID:
            print(config["youtubeToDiscordFormatting"].format(username,message))
            msg = (config["youtubeToDiscordFormatting"].format(username,message))
            await client.send_message(channelToUse, msg)
        elif userID == botUserID: #if the userId is the bots then check the message to see if the bot sent it.
            msgCheckComplete = msgCheckRegex.search(message) #checks the message against the previously created regex for ":"
            if msgCheckComplete == ":": #if its this then go and send the message as normal
                print(config["youtubeToDiscordFormatting"].format(username,message))
                msg = (config["youtubeToDiscordFormatting"].format(username,message))
                await client.send_message(channelToUse, msg)
        
async def sendLiveChat(msg): #sends messages to youtube live chat
   list_chatmessages_inset = youtube.liveChatMessages().insert(
     part = "snippet",
     body = dict (
        snippet = dict(
           liveChatId = liveChatId,
           type = "textMessageEvent",
           textMessageDetails = dict(
               messageText = msg
           )
         )
      )
   )  

   #print(list_chatmessages_inset.execute()) #debug for sending live chat messages
  


if __name__ == "__main__":
    args = argparser.parse_args()
        
    youtube = get_authenticated_service(args) #authenticates the api and saves it to youtube
    getLiveId(youtube)
    


##discord portion of the bot
#this will be the main code

client = discord.Client() #sets this to just client for reasons cuz y not? (didnt have to be done like this honestly could of been just running discord.Client().)


async def discordSendMsg(msg): #this is for sending messages to discord
    global config
    global channelToUse #pulls in t{0} : {1}".format(author,msg)he global variable
    await client.send_message(channelToUse, msg) #sends the message to the channel specified in the beginning
    


@client.event
async def on_ready(): #when the discord api has logged in and is ready then this even is fired
    if firstRun == "off":
        #these 2 variables are used to keep track of what channel is thre real channel to use when sending messages to discord
        global config , botName
        global channelToUse #this is where we save the channel information (i think its a class)
        global channelUsed #this is the channel name we are looking for
        #this is just to show what the name of the bot is and the id
        print('Logged in as') ##these things could be changed a little bit here
        print(client.user.name+ "#" + client.user.discriminator)
        botName = client.user.name+ "#" + client.user.discriminator #gets and saves the bots name and discord tag
        print(client.user.id)
        for server in client.servers: #this sifts through all the bots servers and gets the channel we want
            #should probly add a check in for the server in here im guessing
            for channel in server.channels:
                if channel.name == config["channelName"] and str(channel.type) == "text": #checks if the channel name is what we want and that its a text channel
                    channelToUse = channel #saves the channel that we wanna use since we found it
        
        await youtubeChatImport() #runs the youtube chat import code
    else:
        await getFirstRunInfo()
                
async def youtubeChatImport(): #this is used to pull the from youtube to discord
    i = 0
    while True:
        i += 1
        await listChat(youtube) #checks the youtube chat
        if i == 8:
            fileSave(config)
            i = 0
        await asyncio.sleep(5) #this works
            
@client.event
async def on_message(message): #waits for the discord message event and pulls it somewhere
    global config
    global channelToUse #pulls in the global variable
    if firstRun == "off":
        if str(channelToUse.name) == str(message.channel) and str(message.author) != botName:
            print(config["discordToYoutubeFormating"].format(message.author,message.content)) #prints this to the screen
            await sendLiveChat(config["discordToYoutubeFormating"].format(message.author,message.content)) #prints this to the screen


##file load and save stuff

def fileSave(config):
    print("Saving")
    f = open("config.json", 'w') #opens the file your saving to with write permissions
    f.write(json.dumps(config) + "\n") #writes the string to a file
    f.close() #closes the file io


def fileLoad():
    f = open("config.json", 'r') #opens the file your saving to with read permissions 
    config = "" 
    for line in f: #gets the information from the file
        config = json.loads(line) #this will unserialize the table
    return config


##first run stuff


def getToken(): #gets the token 
    global config
    realToken = "false" #this is just for the while loop
    while realToken == "false":
        config["discordToken"] = input("Discord Token: ") #gets the user input
        try:
            client.run(config["discordToken"]) #atempts to run it and if it fails then execute the next bit of code if not then save it and go on
        except:
            print("Please enter a valid token")
            sys.exit(0) #this is a work around for the bug that causes the code not think the discord token is valid even tho it is after the first time of it being invalid
        else:
            realToken = "true"


async def getFirstRunInfo():
    global config
    print('Logged in as') ##these things could be changed a little bit here
    print(client.user.name) 
    print(client.user.id)
    while config["serverName"] == "":
        for server in client.servers: #this sifts through all the bots servers and gets the channel we want
            print(server.name)
            if input("If this is the server you want type yes if not hit enter: ") == "yes":
                config["serverName"] = server.name
                break    
    while config["channelName"] == "":
        for server in client.servers: #this sifts through all the bots servers and gets the channel we want
            #should probly add a check in for the server in here im guessing
            #print(server.name)
            for channel in server.channels:
                if str(channel.type) == "text":
                    print(channel.name)
                    if input("If this is the channel you want type yes if not hit enter: ") == "yes":
                        config["channelName"] = channel.name
                        break
    while config["youtubeToDiscordFormatting"] == "": #fills the youtube to discord formating
        config["youtubeToDiscordFormatting"] = input("""Please enter the chat formatting for chat coming from youtube to go to discord. 
{0} is the placeholder for the username
{1} is the placeholder for the message
Ex. "{0} : {1}: """)
    while config["discordToYoutubeFormating"] == "": #fills the discord to youtube formating
        config["discordToYoutubeFormating"] = input("""Please enter the chat formatting for chat coming from discord to go to youtube. 
{0} is the placeholder for the username
{1} is the placeholder for the message
Ex. "{0} : {1}": """)
    print("Configuration complete")
    fileSave(config) #saves the file
    print("Please run the command normally to run the bot")
    await client.close()
            
if os.path.isfile("config.json") == False:#checks if the file exists and if it doesnt then we go to creating it
    print("Config missing. This may mean this is your first time setting this up")
    firstRun = "on"
else:
    config = fileLoad() #if it exists try to load it
if firstRun == "on":
    config = {"channelName": "", "pageToken": "", "serverName": "", "discordToken": "","discordToYoutubeFormating": "", "youtubeToDiscordFormatting":""}
    getToken()






client.run(config["discordToken"])#starts the discord bot







