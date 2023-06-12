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

########
# TEXT #
########
welcome_text = ["I am Peter, an advanced AI-powered robot for Laptops designed for engaging conversations. Before we proceed, I would like to assure you that your privacy and data security are of utmost importance to us. Please note that I am an experimental entity, and our interactions serve as a learning experience.", "I am NAO, an advanced AI-powered robot designed for engaging conversations. As part of this experiment, it is important to clarify that only the conversation history is stored for analysis and improvement purposes. Rest assured, any personal or sensitive information shared during our conversation will be treated with the utmost confidentiality and will not be used for any other purpose."]
start = ["You can start now.", "I am ready to listen. Please begin speaking.", "You have the opportunity to share your ideas now.", "Feel free to start speaking now.", "You can speak now!", "It's your turn to talk. Go ahead!", "The floor is yours. You can start speaking now.", "Feel free to express your thoughts now!", "puuuuuuh, I am now out of puff... please talk now."]
introduction = "I am connected to a Large Language MOdel and you can ask me anything you want. The only problem is that I can only speak English, please try."



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

# Minimum volume to start recording
MIN_VOLUME = 500

# Number of frames that are recorded at once
CHUNK_SIZE = 1024

# Audioformat
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100



#############
# Functions #
#############

"""
The given code is a Python function called record_audio that 
records audio from a microphone and saves it as a wave file. 
The function takes two parameters: WAVE_OUTPUT_FILENAME, 
which specifies the name of the output wave file, and SILENT_THRESHOLD, 
which determines the threshold for detecting silence in the audio.

The function uses the PyAudio library to handle audio-related operations. 
It initializes the PyAudio module and retrieves information about the default 
input device. Then, it opens a stream to read audio data from the microphone.
"""
def record_audio(WAVE_OUTPUT_FILENAME, SILENT_THRESHOLD):
    # Initialisiere pyaudio
    p = pyaudio.PyAudio()
    default_source = p.get_default_input_device_info()

    # Öffne den Audiostrom vom Mikrofon
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    frames = []
    silent_counter = 0

    while True: # loop
        data = stream.read(CHUNK_SIZE) # Read a frame from the microphone
        audio_data = audioop.tomono(data, 2, 1, 0) # Convert the frame to an integer array
        volume = abs(audioop.max(audio_data, 2)) # Calculate the average volume of the frame

        if volume >= MIN_VOLUME: # If the volume is above the minimum value, add the frame to the recording data
            silent_counter = 0
            frames.append(data)
        else: # If the volume is below the minimum value, increase the "silent_counter".
            silent_counter += 1

        if silent_counter > int(RATE / CHUNK_SIZE * SILENT_THRESHOLD): # If the "silent_counter" is greater than the SILENT_THRESHOLD, stop recording
            break

    # Close the Audiostream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Create a Wave-File from the recorded frames
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()
    return WAVE_OUTPUT_FILENAME


"""
The provided code is a Python function called speech_recognition that performs 
speech recognition on an audio file. The function takes a parameter called remoteaudiofile, 
which represents the path or filename of the audio file to be recognized.
"""
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
            os.remove(remoteaudiofile) # delete the file


"""
The given code defines a Python function called open_ai_prompt that interacts with the 
OpenAI GPT-3.5 Turbo model for generating a response to a prompt. The function 
takes a parameter called messages_input, which represents a list of messages exchanged 
between the user and the model.

Inside the function, the openai.ChatCompletion.create() method is called to generate a 
response. The method takes two main arguments: model, which specifies the model to be 
used (in this case, "gpt-3.5-turbo"), and messages, which is the list of messages 
exchanged between the user and the model.

The function assigns the generated response to the variable answer and then returns it. 
The response can be used to retrieve the generated text or perform any further processing or 
actions based on the specific use case.
"""
def open_ai_prompt(messages_input):
    answer = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_input)
    return answer


"""
The provided code defines a Python function called `conversation` that simulates a 
conversation between a user and an assistant using speech recognition, 
prompt generation, and response retrieval.

The function takes a parameter called `SILENT_THRESHOLD`, which determines the 
threshold for detecting silence during audio recording.

Within the function, there is a while loop that continues until the prompt is "stop". 
In each iteration of the loop, the user is prompted to speak by calling the `record_audio` 
function, which records audio and returns the recognized speech as a prompt.

If the prompt is not None and does not contain the word "stop", it means the user has 
provided a valid input. The prompt is then added to the `messages` list with the role of 
the user. The `open_ai_prompt` function is called with the collected messages to generate 
a response from the assistant. The response content is extracted and added to the `messages` 
list with the role of the assistant.

The function then returns the response content and the user's prompt as a tuple.

If the prompt is None, it means the user was too slow in providing input within the specified 
silent threshold. In this case, an appropriate message is assigned to `answer_content`, 
and the prompt is set to "No prompt!". The function then returns the response content and 
the prompt as a tuple.

If the prompt contains the word "stop", it means the user has explicitly requested to end 
the conversation. In this case, an appropriate message is assigned to `answer_content`, 
and the prompt is set to "stop". The function then returns the response content and the prompt as a tuple.
"""
def conversation(SILENT_THRESHOLD):
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


"""
The provided code defines a Python function named get_and_save that 
retrieves data from the conversation function, saves it, and performs text-to-speech conversion.
"""
def get_and_save(id, existing_data):
    current_time = datetime.now().strftime("%H:%M:%S")
    prompt = ""
    json_file = "conversation.json"
    while True:
        if prompt != "stop":
            current_time = datetime.now().strftime("%H:%M:%S")
            response, prompt = conversation(2)
            new_data = {"time": current_time, "prompt": prompt, "response": response}
            existing_data["conversation"][str(id)].append(new_data)
            with open(json_file, 'w') as file:
                json.dump(existing_data, file)
        elif "stop" in prompt:
            break


"""
In summary, the main function handles different cases depending on the value of new_file. 
It either retrieves existing data from a JSON file and appends new conversation entries, 
or it starts a new conversation with an identifier of "1". The function interacts with an 
API, saves conversation data, and performs text-to-speech conversion.
"""
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


if __name__ == '__main__':
    engine.say(welcome_text[0])
    engine.runAndWait()
    time.sleep(2)
    engine.say(introduction)
    engine.runAndWait()
    time.sleep(2)
    main()