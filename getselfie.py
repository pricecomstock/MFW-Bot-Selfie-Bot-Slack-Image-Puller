import random
import requests
import time
from flask import Flask, request, jsonify, json

app = Flask(__name__)

@app.route('/selfie', methods=['POST'])
def getselfie(title="Selfie",user=None):
    #Open and read our selfie URL file
    selfie_urls_file = open('/home/pricecomstock/slash-selfie/url_list_file.json','rb')
    selfie_urls_json = json.load(selfie_urls_file)
    
    #Find the incoming command
    arguments = request.form['text'].split(' ')
    #initialize response
    response=''

    #/selfie stats
    if arguments[0] == 'stats' and len(arguments)==1:
        response+="```Selfie Leaderboard:\n"
        response+='-'*30+'\n'
        leaderboard={}
        
        #Assemble names and scores and sort them, adding each line to leaderboard
        for x in selfie_urls_json:
            leaderboard.update([(selfie_urls_json[x]['uname'],len(selfie_urls_json[x]['selfies']))])
        leaderboard = sorted(leaderboard.items(), key=lambda x: x[1],reverse=True)
        
        #Go back through leaderboard and count total selfies
        totalselfies=0
        for x in leaderboard:
            totalselfies += x[1]
        
        #Formatting
        response+="RNK".ljust(5) + "NAME".ljust(11) +"COUNT".rjust(7) + "PROB".rjust(8) + '\n'
        place=1
        for x in leaderboard:
            response += (('#' + str(place)).ljust(4) + ' ' + x[0].ljust(14) + str(x[1]).rjust(4) + (("%.1f" % (x[1]/float(totalselfies)*100.0))+'%').rjust(8)+ "\n")
            place += 1
        response+='-'*30+'\n'
        response+='TOTAL'.ljust(18)+str(totalselfies).rjust(4)+" selfies\n"
        response+="```"
        return jsonify({'response_type':'in_channel','text':response})
    
    #/selfie, or if this function was called from mfw with user='any' 
    elif arguments[0] == '' or user == 'any':
        #Assemble all urls into an array and choose one, weighted equally amongst each selfie
        pick_a_selfie=[]
        for x in selfie_urls_json:
            for y in selfie_urls_json[x]['selfies']:
                pick_a_selfie.append(y)
        response=pick_a_selfie[random.randint(0,len(pick_a_selfie)-1)].replace(' ','_')
    
    #Only used when called from MFW if a user has been specified
    elif user is not None:
        response = random.choice(selfie_urls_json[user]['selfies']).replace(' ','_')
    
    #/selfie [name]
    else:
        for x in selfie_urls_json:
            if selfie_urls_json[x]['uname'] == arguments[0]:
                response = random.choice(selfie_urls_json[x]['selfies']).replace(' ','_')
        if response == '': #if unchanged, so if no usernames matched, just pick a random selfie
            pick_a_selfie=[]
            for x in selfie_urls_json:
                for y in selfie_urls_json[x]['selfies']:
                    pick_a_selfie.append(y)
            response=pick_a_selfie[random.randint(0,len(pick_a_selfie)-1)].replace(' ','_')
    
    #Return our well formatted message to slack
    return jsonify(
        {
          "response_type": "in_channel",
          "attachments": [
            {
              "fallback": "It's a selfie",
              "color": "#FFAA22",
              "title": title,
              "title_link": response,
              "image_url": response
            }
          ]
        } )

@app.route('/mfw', methods=['POST'])
def mfw():
    #/mfw me, [anything]
    if len(request.form['text'].split(','))>1 and request.form['text'].split(',',1)[0].strip(' ')=='me':
        return getselfie("MFW " + request.form['text'].split(',',1)[1].strip(' '), request.form['user_id'])
    #/mfw [anything]
    else:
        return getselfie("MFW " + request.form['text'],'any')