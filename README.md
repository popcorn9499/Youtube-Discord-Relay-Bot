# Youtube-Discord-Relay-Bot
This is a youtube and discord chat relay bot


Requirements
    python 3.5
    pip
    discord.py
    google-api-python-client

installation instructions:

    python3.5 -m pip install -U discord.py

    python3.5 -m pip install --upgrade google-api-python-client


Setup:

go to your google developer dashboard https://console.developers.google.com/apis/dashboard
Then go to library and find the youtube data api v3 and enable it

Next step is to go to the credentials page
then hit create credentials, select oauth client id
set the application type to other and give it a name then hit create
then click the credentials and download your json file

Then add that json file to the folder with the this program
rename it to client_secrets.json

Then finally run the python program and follow the prompts till the program is completely setup (in console make sure to use at python3.5)

link for the discord applications page https://discordapp.com/developers/applications

To find the discord token you would have to create a new application.
Take the token (bottom of the page) and put it into the bot when it asks for it
