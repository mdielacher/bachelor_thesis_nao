# This script is for 

##################
# IMPORT SECTION #
##################

import openai
import pyaudio
import wave
import json
import time
import speech_recognition as sr
import os
import pyttsx3
import audioop
import random
from datetime import datetime

# TEXT
welcome_text = ["I am Peter, an advanced AI-powered robot for Laptops designed for engaging conversations. Before we proceed, I would like to assure you that your privacy and data security are of utmost importance to us. Please note that I am an experimental entity, and our interactions serve as a learning experience.", "I am NAO, an advanced AI-powered robot designed for engaging conversations. As part of this experiment, it is important to clarify that only the conversation history is stored for analysis and improvement purposes. Rest assured, any personal or sensitive information shared during our conversation will be treated with the utmost confidentiality and will not be used for any other purpose."]
start = ["You can start now.", "I am ready to listen. Please begin speaking.", "You have the opportunity to share your ideas now.", "Feel free to start speaking now.", "You can speak now!", "It's your turn to talk. Go ahead!", "The floor is yours. You can start speaking now.", "Feel free to express your thoughts now!", "puuuuuuh, I am now out of puff... please talk now."]


############
# SETTINGS #
############

json_file = "conversation.json"
global new_file
new_file = False
if not os.path.isfile(json_file):
    conversation_id = int(1)
    data = {"conversation":{conversation_id:[]}}
    new_file = True
    with open(json_file, "w") as f:
        json.dump(data, f)


with open("Settings/secret_keys.json") as json_file:
        keys = json.load(json_file)
openai.api_key = keys['Open_AI']

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty("voice", voices[0].id)

# Minimale Lautstärke, um eine Aufnahme zu starten
MIN_VOLUME = 500

# Anzahl der Frames, die auf einmal aufgenommen werden
CHUNK_SIZE = 1024

# Audioformat
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100



#############
# Functions #
#############

def record_audio(WAVE_OUTPUT_FILENAME, SILENT_THRESHOLD):
    # Initialisiere pyaudio
    p = pyaudio.PyAudio()

    # Öffne den Audiostrom vom Mikrofon
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    frames = []
    silent_counter = 0

    while True:
        # Lese einen Frame aus dem Mikrofon ein
        data = stream.read(CHUNK_SIZE)
        # Konvertiere den Frame in ein Integer-Array
        audio_data = audioop.tomono(data, 2, 1, 0)
        # Berechne die durchschnittliche Lautstärke des Frames
        volume = abs(audioop.max(audio_data, 2))

        # Wenn die Lautstärke über dem Mindestwert liegt, füge den Frame zu den Aufnahmedaten hinzu
        if volume >= MIN_VOLUME:
            silent_counter = 0
            frames.append(data)
        # Wenn die Lautstärke unter dem Mindestwert liegt, erhöhe den "silent_counter"
        else:
            silent_counter += 1

        # Wenn der "silent_counter" größer als die SILENT_THRESHOLD ist, beende die Aufnahme
        if silent_counter > int(RATE / CHUNK_SIZE * SILENT_THRESHOLD):
            break

    # Schließe den Audiostrom
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Erstelle eine Wave-Datei aus den aufgenommenen Frames
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()
    return WAVE_OUTPUT_FILENAME


def speech_recognition(remoteaudiofile):
    r = sr.Recognizer() # initliaze speech_recognition
    with sr.AudioFile(remoteaudiofile) as file:
        audio_file = r.listen(file)
        try:
            text_data = str(r.recognize_google(audio_file))
            return text_data
        except sr.UnknownValueError as uve: # Error handling
            print('Error ', uve)
        finally:
            os.remove(remoteaudiofile)


def open_ai_prompt(messages_input):
    answer = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_input)
    return answer

def gespreach(SILENT_THRESHOLD):
    messages = []
    role = ["user", "assistant"]
    count = 0
    while True:  # loop until prompt is "stop"
        recordingname = str(int(time.time())) + ".wav"
        start_text = start[random.randint(0, len(start)-1)]
        print(start_text)
        engine.say(start_text)
        engine.runAndWait()
        print("START speech_recognition!")
        prompt = speech_recognition(record_audio(recordingname, SILENT_THRESHOLD))
        print("STOP speech_recognition!")
        print(f"prompt: {prompt}")
        if prompt is not None and "stop" not in prompt:  # check again in case the prompt is "stop"
            print("You said: " + prompt)
            messages.append({"role": role[0], "content": prompt})
            answer = open_ai_prompt(messages)
            answer_content = answer['choices'][0]['message']["content"]
            print(f"Answer: {answer_content}")
            engine.say(answer_content)
            engine.runAndWait()
            return answer_content, prompt
        elif prompt is None:
            print("You said nothing")
            answer_content = "You was too slow, because the silent treshold is 2 seconds."
            prompt = "No prompt!"
            print(f"Answer: {answer_content}")
            engine.say(answer_content)
            engine.runAndWait()
            return answer_content, prompt
        elif "stop" in prompt:
            print("You said: stop")
            answer_content = "You stopped the conversation, I hope we see us again!"
            prompt = "stop"
            print(f"Answer: {answer_content}")
            engine.say(answer_content)
            engine.runAndWait()
            return answer_content, prompt


def get_and_save(id, existing_data):
    current_time = datetime.now().strftime("%H:%M:%S")
    prompt = ""
    json_file = "conversation.json"
    while True:
        if prompt != "stop":
            current_time = datetime.now().strftime("%H:%M:%S")
            response, prompt = gespreach(2)
            new_data = {"time": current_time, "prompt": prompt, "response": response}
            existing_data["conversation"][str(id)].append(new_data)
            with open(json_file, 'w') as file:
                json.dump(existing_data, file)
        elif "stop" in prompt:
            break


# MAIN FUNCTION
def main():
    json_file = "conversation.json"
    if new_file == True:
        with open(json_file, 'r') as file:
            existing_json = file.read()
        existing_data = json.loads(existing_json)
        get_and_save("1", existing_data)

    else:
        with open(json_file, 'r') as file:
            existing_json = file.read()
        existing_data = json.loads(existing_json)
        list_last_id = int(list(existing_data["conversation"].keys())[-1])
        new_id_str = str(list_last_id+1)
        new_conversation = {new_id_str: []}
        existing_data["conversation"].update(new_conversation)
        get_and_save(new_id_str, existing_data)

            


main()
