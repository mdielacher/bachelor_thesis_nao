'''
MAIN SCRIPT
'''
# Imports
import requests
import calendar
import os
import ast
import time
import json
import random
import threading
from flask import Flask, request
from naoqi import ALProxy
from scipy.io.wavfile import write
from csv import writer
from datetime import datetime
import multiprocessing




#settings
NAOIP = 'NAO_IP 
PORT = 9559
NAME = "nao"
PASSWD = "NAOPWD"
BASE_API = 'http://IP/chat'

# fileshare
json_file = "fileshare/nao_conversation.json"
new_file = False
if not os.path.isfile(json_file):
    conversation_id = int(1)
    data = {"conversation":{conversation_id:[]}}
    new_file = True
    with open(json_file, "w") as f:
        json.dump(data, f)

# dialog text
dialog = ["I am NAO, an advanced AI-powered robot designed for engaging conversations. Before we proceed, I would like to assure you that your privacy and data security are of utmost importance to us. Please note that I am an experimental entity, and our interactions serve as a learning experience.", "I am NAO, an advanced AI-powered robot designed for engaging conversations. As part of this experiment, it is important to clarify that only the conversation history is stored for analysis and improvement purposes. Rest assured, any personal or sensitive information shared during our conversation will be treated with the utmost confidentiality and will not be used for any other purpose."]
introduction = "I am connected to a Large Language MOdel and you can ask me anything you want. The only problem is that I can only speak English, please try."
start = ["You can start now.", "I am ready to listen. Please begin speaking.", "You have the opportunity to share your ideas now.", "Feel free to start speaking now.", "You can speak now!", "It's your turn to talk. Go ahead!", "The floor is yours. You can start speaking now.", "Feel free to express your thoughts now!", "puuuuuuh, I am now out of puff... please talk now."]


# Proxies
# Proxy for Text2Speech 
TEXTPROXY = ALProxy('ALTextToSpeech', NAOIP, PORT)
TEXTPROXY.setParameter("speed", 85) #talk slower 0-100

POSTUREPROXY = ALProxy('ALRobotPosture', NAOIP, PORT) #Posture proxy
MOTIONPROXY = ALProxy('ALMotion', NAOIP, PORT) # Motion proxy
SOUNDPROXY = ALProxy("ALAudioPlayer", NAOIP, PORT) # Play sound on NAO
MANAGERPROXY = ALProxy("ALBehaviorManager", NAOIP, PORT) # Behavior proxy
LEDSPROXY = ALProxy('ALLeds', NAOIP, PORT)





fileshare = os.path.join(os.getcwd(), 'fileshare')
#time.sleep(2) # Time sleep 3 seconds
#TEXTPROXY.say(dialog[0])# welcome speech from Dialog.py
#time.sleep(3)
#TEXTPROXY.say(introduction)

def get_and_save(id, existing_data):
    current_time = datetime.now().strftime("%H:%M:%S")
    prompt = ""
    while True:
        if prompt != "stop":
            current_time = datetime.now().strftime("%H:%M:%S")
            start_text = start[random.randint(0, len(start)-1)]
            time.sleep(2)
            print(start_text)
            TEXTPROXY.say(start_text)
            response = requests.get(BASE_API)
            print("done!")
            data = json.loads(response.text)
            prompt = data.get("prompt")
            response = data.get("response")
            print('prompt: ' + str(prompt))
            print('prompt: ' + str(response))
            TEXTPROXY.say(str(response))
            new_data = {"time": current_time, "prompt": prompt, "response": response}
            existing_data["conversation"][str(id)].append(new_data)
            with open(json_file, 'w') as file:
                json.dump(existing_data, file)
        elif prompt == "stop":
            print("stop")
            break
        

# MAIN FUNCTION
def main():
    if new_file == True:
        with open(json_file, 'r') as file:
            existing_json = file.read()
        existing_data = json.loads(existing_json)
        get_and_save("1", existing_data)

    else:
        with open(json_file, 'r') as file:
            existing_json = file.read()
        existing_data = json.loads(existing_json)
        print(existing_data)
        new_id = int(existing_data["conversation"].keys()[-1])+1
        new_id_str = str(new_id)
        new_conversation = {new_id_str: []}
        existing_data["conversation"].update(new_conversation)
        print(existing_data)
        get_and_save(new_id_str, existing_data)


if __name__ == '__main__':
    main()
