import pyaudio
import os
import wave
import numpy as np
import torch
from silero_vad import (load_silero_vad, read_audio, get_speech_timestamps, save_audio, VADIterator, collect_chunks)# from initialize_whisper import initialize_whisper_model

current_status = None  # Initialize the current status

# Load VAD model
model = load_silero_vad(onnx=False)
sampling_rate = 16000
chunk_size = 512
speech_threshold = 0.5

# Function to process audio chunks with VAD
def process_chunk(chunk):
    tensor_chunk = torch.from_numpy(chunk).float()
    speech_prob = model(tensor_chunk, sampling_rate).item()
    return speech_prob

import time
# Function to record audio from the microphone and save it to a file
def record_audio(file_path, channels=1, rate=16000, silence_duration=0.5, max_no_voice_duration=15):
    file_name = "statuses/voice_detected.txt"
    with open(file_name, 'w') as file:
        file.write('False')

    p = pyaudio.PyAudio()
    # Open the WAV file for writing
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size)
    frames = []
    audio_buffer = []
    silence_counter = 0
    voice_detected = False
    silence_threshold = sampling_rate / chunk_size * silence_duration
    print(silence_threshold)

    start_time = time.time()
    print("Monitoring voice...")
    try:
        while True:
            data = stream.read(chunk_size, exception_on_overflow=False)  # Avoid exceptions on overflow
            # Write the chunk of audio data to the WAV fil
            wf.writeframes(data)
            frames.append(data)
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0  # Normalize
            
            audio_buffer.extend(audio_data)
            while len(audio_buffer) >= chunk_size:
                chunk = np.array(audio_buffer[:chunk_size])
                audio_buffer = audio_buffer[chunk_size:]

                speech_prob = process_chunk(chunk)
                percentage = speech_prob* 100
                rounded_value = round(percentage, 2)  # Rounds to 2 decimal places (nearest 0.01)

                if speech_prob >= speech_threshold:

                    # print(speech_prob)
                    first = True
                    voice_detected = True    
                    start_time = time.time()  # Reset timer
                    
                    # Open the file in write mode and write the message
                    with open(file_name, 'w') as file:
                        file.write('True')

                    with open("statuses/pause_detected.txt", "w") as file:
                        file.write('false')   
                        
                    silence_counter = 0

                else:

                    if voice_detected:
                        silence_counter += 1
                        # print(silence_counter)

                    if voice_detected and silence_counter >= silence_threshold:
                        # print("Silence detected after voice.")

                        voice_detected = False

                        # Open the file in write mode and write the message
                        with open(file_name, 'w') as file:
                            file.write('False')
                        with open("statuses/pause_detected.txt", "w") as file:
                            file.write('true')    

                                    # Check if no voice detected for the max duration
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_no_voice_duration and not voice_detected:
                # print(f'No voice detected for the last {max_no_voice_duration} seconds. Restarting.')
                frames = []  # Clear frames to start fresh
                audio_buffer = []
                silence_counter = 0
                voice_detected = False  # Reset voice detected flag    
                with open("audios/input.wav", "wb") as file:
                    file.write(b'')

                p = pyaudio.PyAudio()
                # Open the WAV file for writing
                wf = wave.open(file_path, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(rate)

                stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size)
                start_time = time.time()  # Reset timer


            # if voice_detected:
            #     with open('statuses/status.txt', 'r') as file:
            #         status = file.read().strip()  # Read status from the file
            #     if status.lower() in ('response', 'ignore', 'interrupt', 'backchannel'):
            #         if current_status != status.lower():  # Check if the status has changed
            #             print('hello world')
            #             current_status = status.lower()  # Update the current status
            #             frames = []  # Clear frames to start fresh
            #             audio_buffer = []
            #             with open("audios/input.wav", "wb") as file:
            #                 file.write(b'')

            #             p = pyaudio.PyAudio()
            #             # Open the WAV file for writing
            #             wf = wave.open(file_path, 'wb')
            #             wf.setnchannels(channels)
            #             wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            #             wf.setframerate(rate)

            #             stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size)
            #     else:
            #         pass  # Reset if the status is something else


    except KeyboardInterrupt:
        print("Recording interrupted.")
    finally:
        # Ensure the stream is properly closed
        stream.stop_stream()
        stream.close()
        p.terminate()

# Function to manage the whole process
def start():
    
    audio_file = "audios/input.wav"

    # Record new audio
    record_audio(audio_file)


# start()
