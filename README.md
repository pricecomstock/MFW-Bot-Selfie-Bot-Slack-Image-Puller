# MFW-Bot-Selfie-Bot-Slack-Image-Puller
A Slack slash-command meant to crawl a certain channel (#selfies_only should give you the idea) and post back the pictures on command.

#Setup
Simplest setup is on pythonanywhere. Set pull.py to run at some interval (daily for the free plan). Create a web app with getselfie.py. Create a slash command in slack to POST to your pythonanywhere URL.
