#IMPORTS
import pandas as pd
import os
import json

import openai
import pyaudio
import wave
import time
import speech_recognition as sr
import pyttsx3
import audioop
from flask import Flask, request

#API 
app = Flask(__name__)


############
# SETTINGS #
############
print(os.getcwd())
with open("python3/Settings/secret_keys.json") as json_file:
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
    default_source = p.get_default_input_device_info()
    print("Aktuell verwendete Audioquelle:")
    print("Name:", default_source['name'])

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
            print('recognized text: ', text_data)
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
        prompt = speech_recognition(record_audio(recordingname, SILENT_THRESHOLD))
        print(prompt)
        if prompt is not None and prompt != "stop":  # check again in case the prompt is "stop"
            print("You said: " + prompt)
            messages.append({"role": role[0], "content": prompt})
            answer = open_ai_prompt(messages)
            answer_content = answer['choices'][0]['message']["content"]
            messages.append({"role": role[1], "content": answer_content})
            return answer_content, prompt
        elif prompt is None:
            answer_content = "You was too slow, because the silent treshold is 2 seconds."
            prompt = "No prompt!"
            return answer_content, prompt
        elif prompt == "stop":
            answer_content = "You stopped the conversation, I hope we see us again!"
            prompt = "stop"
            return answer_content, prompt

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    SILENT_THRESHOLD = 2 # Set your desired silent threshold
    if request.method == 'POST' or request.method == 'GET':
        response, prompt = gespreach(SILENT_THRESHOLD)
        return {'prompt':prompt,'response': response}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
