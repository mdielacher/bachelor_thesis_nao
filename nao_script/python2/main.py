###########
# Imports #
###########
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

############
# SETTINGS #
############
NAOIP = '192.168.8.105' 
PORT = 9559
NAME = "nao"
PASSWD = "19981"
BASE_API = 'http://192.168.8.120:5000/chat'


json_file = "fileshare/nao_conversation.json"
new_file = False # standard value
if not os.path.isfile(json_file): # check if json file exists
    conversation_id = int(1)
    data = {"conversation":{conversation_id:[]}}
    new_file = True
    with open(json_file, "w") as f:
        json.dump(data, f)


################
# TEXT FOR NAO #
################
dialog = ["I am NAO, an advanced AI-powered robot designed for engaging conversations. Before we proceed, I would like to assure you that your privacy and data security are of utmost importance to us. Please note that I am an experimental entity, and our interactions serve as a learning experience.", "I am NAO, an advanced AI-powered robot designed for engaging conversations. As part of this experiment, it is important to clarify that only the conversation history is stored for analysis and improvement purposes. Rest assured, any personal or sensitive information shared during our conversation will be treated with the utmost confidentiality and will not be used for any other purpose."]
introduction = "I am connected to a Large Language Model and you can ask me anything you want. The only problem is that I can only speak English, please try."
start = ["You can start now.", "I am ready to listen. Please begin speaking.", "You have the opportunity to share your ideas now.", "Feel free to start speaking now.", "You can speak now!", "It's your turn to talk. Go ahead!", "The floor is yours. You can start speaking now.", "Feel free to express your thoughts now!", "puuuuuuh, I am now out of puff... please talk now."]

#########
# PROXY #
#########
TEXTPROXY = ALProxy('ALTextToSpeech', NAOIP, PORT)
TEXTPROXY.setParameter("speed", 85) #talk slower 0-100

fileshare = os.path.join(os.getcwd(), 'fileshare')


"""
The provided code defines a Python function named get_and_save that 
retrieves data from an API, saves it, and performs text-to-speech conversion.
"""
def get_and_save(id, existing_data):
    current_time = datetime.now().strftime("%H:%M:%S")
    prompt = ""
    while True:
        if "stop" not in prompt:
            time.sleep(2)
            current_time = datetime.now().strftime("%H:%M:%S")
            start_text = start[random.randint(0, len(start)-1)]
            print(start_text)
            TEXTPROXY.say(start_text)
            response = requests.get(BASE_API)
            print("done!")
            data = json.loads(response.text)
            prompt = data.get("prompt")
            response = data.get("response")
            print('prompt: ' + str(prompt))
            print('response: ' + str(response))
            TEXTPROXY.say(str(response))
            new_data = {"time": current_time, "prompt": prompt, "response": response}
            existing_data["conversation"][str(id)].append(new_data)
            with open(json_file, 'w') as file:
                json.dump(existing_data, file)
        elif "stop" in prompt:
            print("stop")
            break
        

"""
In summary, the main function handles different cases depending on the value of new_file. 
It either retrieves existing data from a JSON file and appends new conversation entries, 
or it starts a new conversation with an identifier of "1". The function interacts with an 
API, saves conversation data, and performs text-to-speech conversion.
"""
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


"""
First, TEXTPROXY.say(dialog[0]) is called, which likely triggers text-to-speech 
synthesis to speak out a welcome speech stored in dialog[0].
After a delay of 3 seconds using time.sleep(3), TEXTPROXY.say(introduction) is 
called, which is expected to generate another speech for an introduction.
Finally, the main() function is called, which is likely the entry 
point of the script's main functionality.
"""
if __name__ == '__main__':
    TEXTPROXY.say(dialog[0])# welcome speech from Dialog.py
    time.sleep(3)
    TEXTPROXY.say(introduction)
    main()