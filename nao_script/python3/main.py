#IMPORTS
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


############
# SETTINGS #
############

#define app
app = Flask(__name__)


openai.api_key = "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"

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
            print('recognized text: ', text_data)
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
        print("Beginn speaking!")
        prompt = speech_recognition(record_audio(recordingname, SILENT_THRESHOLD))
        print("Stop speaking.")
        if prompt is not None and "stop" not in prompt:  # check again in case the prompt is "stop"
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
        elif "stop" in prompt:
            answer_content = "You stopped the conversation, I hope we see us again!"
            prompt = "stop"
            return answer_content, prompt


"""
The provided code is a Python Flask route defined for the `/chat` 
endpoint. The route accepts both GET and POST requests.

Inside the route function named `chat()`, a silent threshold value of 2 seconds 
is set as `SILENT_THRESHOLD`. This threshold determines the duration of 
silence during audio recording in the conversation.

The route function then constructs a dictionary containing the prompt and response, 
and returns it as the response to the client. The prompt and response are included in the 
dictionary with keys "prompt" and "response" respectively.
"""
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    SILENT_THRESHOLD = 2 # Set your desired silent threshold
    if request.method == 'POST' or request.method == 'GET':
        response, prompt = conversation(SILENT_THRESHOLD)
        return {'prompt':prompt,'response': response}


"""
In summary, this code block ensures that the Flask application is only run when the script 
is executed directly, rather than when it is imported as a module by another script. 
It starts the Flask application and makes it accessible on all network interfaces with debugging enabled.
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


