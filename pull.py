import requests
import json
import time
import os
import sys
from shutil import copyfile

user = 'REDACTED' # your 9 character user ID
token = "REDACTED" # your token (test or bot)
selfies_channel='REDACTED'

SAVE_FILES_LOCALLY=False

#This function takes some known parameters and turns them into the public URL format that Slack uses
def construct_selfie_url(name,puburl):
    #PUBLIC FILE URL FORMAT:
    #https://files.slack.com/files-pri/T1C6G4L3C-F1SABLELC/img_20160715_212825.jpg?pub_secret=0b4e08f31c
    puburl_token=puburl.split('/')[3]
    pub_secret=puburl_token.split('-')[2] #pub_secret=0b4e08f31c
    pub_other=puburl_token.split('-')[0] + '-' + puburl_token.split('-')[1] #/T1C6G4L3C-F1SABLELC/
    result = "https://files.slack.com/files-pri/" + pub_other + "/" + name + "?pub_secret=" + pub_secret
    return result.replace(' ','_')

# Set to only collect new images since previous run
last_run_time_file=open('/home/pricecomstock/slash-selfie/lastruntime.txt', 'r+')
last_run_time = last_run_time_file.readline().strip('\n')
#last_run_time = '1462060800' #UNCOMMENT FOR DEBUG/FIRST RUN START TIME OVERRIDE. Beginning of may: 1462060800
this_run_time = str(int(time.time()))


#Here's our JSON file full of URLs
url_list_file_name="/home/pricecomstock/slash-selfie/url_list_file.json"



#Open, or create JSON if it does not exist
if os.path.isfile(url_list_file_name):
    url_list_file=open(url_list_file_name, "r+b")
    url_dict=json.load(url_list_file)
    #make a backup
    copyfile(url_list_file_name,'/home/pricecomstock/slash-selfie/selfiebackups/'+str(this_run_time)+url_list_file_name.split('/')[-1])
else:
    url_list_file=open(url_list_file_name, "wb")
    url_dict={}

howmanynewselfies=0 #keep a count

# Get our list of images
slack_api_url="https://slack.com/api/files.list?token=" + token + "&channel=" + selfies_channel + "&ts_from=" + last_run_time + "&types=images"
selfie_request = requests.get(slack_api_url)
image_list = selfie_request.json()

for selfie in image_list["files"]:
    #Get some basic info
    selfie_user = selfie["user"]
    selfie_name = selfie["name"].lower()
    selfie_puburl = selfie["permalink_public"]
    selfie_id = selfie["id"]
    selfie_url = construct_selfie_url(selfie_name, selfie_puburl)

    #Slack API call to make file available for public sharing
    requests.get("https://slack.com/api/files.sharedPublicURL?token=" + token + "&file=" + selfie_id)

    #Add a new user if necessary
    if selfie_user not in url_dict:
        #API call to get username
        slack_user_list_api_url='https://slack.com/api/users.list?token=' + token
        user_list=requests.get(slack_user_list_api_url).json()
        selfie_uname=""
        #Check each username for a match to user ID
        for x in user_list['members']:
            if x['id'] == selfie_user:
                selfie_uname = x['name']
        
        #Put username and ID in URL dictionary
        url_dict.update( [ (selfie_user,{"uname" : selfie_uname, "selfies" : [] }) ] ) #"USERID": ["price",[http..., http...]]

    #Add URL to dictionary, checking that it isn't a duplicate
    if selfie_url not in url_dict[selfie_user]['selfies']:
        howmanynewselfies +=1
        #Some logging
        print "+selfie: "
        print "user: " + selfie_user + " (" + url_dict[selfie_user]['uname'] +")"
        print "url: " + selfie_url
        url_dict[selfie_user]['selfies'].append(selfie_url)

    if (SAVE_FILES_LOCALLY):
        print "Downloading from " + selfie_url
        #Set up some file location, named like \selfies\USERIDID-uname\abc.jpg
        selfie_uname = url_dict[selfie_user]['uname']
        selfie_dir = "selfies\\" + selfie_user + "-" + selfie_uname
        
        #make the user directory if it's not there
        if not os.path.exists(selfie_dir):
            os.makedirs(selfie_dir)
        
        selfie_file = open(selfie_dir + "\\" + selfie_name, 'wb') #Open file for writing
        r = requests.get(selfie_url) #Open URL with image
        selfie_file.write(r.read()) #Read image binary into file
        selfie_file.close()
        print ("Download Finished!")

url_list_file.truncate(0)
url_list_file.seek(0)
url_list_file.write(json.dumps(url_dict,sort_keys=True, indent=4))
print "Done!"
print "Pulled " + str(howmanynewselfies) + " new selfies!"

url_list_file.close()

#record this run time for future use
last_run_time_file.truncate(0)
last_run_time_file.seek(0)
last_run_time_file.write(this_run_time)
last_run_time_file.close()
