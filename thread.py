import pyaudio
import os
import wave
import numpy as np
from pprint import pprint

import torch
from initialize_whisper import initialize_whisper_model
from silero_vad import (load_silero_vad, read_audio, get_speech_timestamps, save_audio, VADIterator, collect_chunks)
from monitor_voice import start
# from chatbot import run
import threading
import queue

# Initialize Whisper model

whisper_model = initialize_whisper_model()


# Load VAD model
print("Loading VAD model...")
model = load_silero_vad(onnx=False)
sampling_rate = 16000
chunk_size = 512
voice_detected = False
speech_threshold = 0.2
print("VAD model loaded.")


from datetime import datetime
import time
import pytz

# Set timezone to Singapore Time (SGT)
sgt_tz = pytz.timezone('Asia/Singapore')

# Function to get formatted current time in Singapore Time (SGT)
def get_sgt_time():
    # Set timezone to Singapore Time (SGT)
    sgt_tz = pytz.timezone('Asia/Singapore')
    # Get current time in SGT
    current_time = datetime.now(sgt_tz)
    # Format time in HH:MM:SS and extended microseconds
    formatted_time = current_time.strftime('%H:%M:%S.') + f'{current_time.microsecond}'
    return formatted_time

#user_start_time = get_sgt_time()
#user_end_time = get_sgt_time()
#ai_start_time = get_sgt_time()
#ai_end_time = get_sgt_time()




# Function to process full audio and convert segments to time
def process_full_audio(audio_file):
    # print(f"Processing full audio file: {audio_file}")
    try:
        wav = read_audio(audio_file, sampling_rate=sampling_rate)
        # print("Audio file read successfully.")
    except RuntimeError as e:
        if 'sox extension is not supported on Windows' in str(e):
            # print("Error: Sox is not supported on Windows. Please use a compatible backend.")
            return
        else:
            # print(f"Runtime error while reading audio: {e}")
            return
    except Exception as e:
        # print(f"Exception while reading audio: {e}")
        return
    
    # Get speech timestamps from full audio file
    # print("Getting speech timestamps...")
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate)
    # print(f"Found {len(speech_timestamps)} speech segments.")

    # Collect and save speech chunks
    try:
        valid_speech_chunks = []
        
        for idx, segment in enumerate(speech_timestamps):
            start_sample = segment['start']
            end_sample = segment['end']
            
            # Extract the chunk based on the start and end timestamps
            chunk = wav[start_sample:end_sample]
            
            # Only keep valid chunks (non-empty)
            if chunk.numel() > 0:
                valid_speech_chunks.append(chunk)
                # print(f"Valid chunk collected: {start_sample} to {end_sample}")

        if len(valid_speech_chunks) == 0:
            # print("No valid speech chunks found.")
            return
        
        # Concatenate and save the valid chunks
        # print("Saving valid speech chunks...")
        save_audio('only_speech.wav', torch.cat(valid_speech_chunks), sampling_rate=sampling_rate)
        # print("Speech chunks saved successfully as 'only_speech.wav'.")
    except Exception as e:
        print(f"An error occurred while saving audio: {e}")

# Function to transcribe audio using Whisper model
def transcribe_with_whisper(audio_file, whisper_model):
    # print(f"Transcribing audio file: {audio_file}")
    try:
        segments, info = whisper_model.transcribe(audio_file, beam_size=5)
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
        # print("Transcription completed.")
        return transcription.strip()
    except Exception as e:
        # print(f"Exception during transcription: {e}")
        return ""
import sys
# Threaded function to process the audio and transcribe it
def process_and_transcribe(audio_file, whisper_model):
    while True:
            # Define the file name
        file_name = "statuses/voice_detected.txt"

        # Read the content of the file and store it in the voice_detected variable
        try:
            with open(file_name, 'r') as file:
                voice_detected = file.read()
            
        except FileNotFoundError:
            voice_detected = ""

        # You can now use the voice_detected variable in your program

        if voice_detected.lower() == 'true':
            with open("statuses/locked.txt", "w") as file:
                file.write('Not Delete')                        
            user_start_time = get_sgt_time()

            while True:
                # Read the content of the file and store it in the voice_detected variable
                try:
                    with open(file_name, 'r') as file:
                        voice_detected = file.read()
                    
                except FileNotFoundError:
                    voice_detected = ""
                # Read the content of the file and store it in the voice_detected variable
                try:
                    with open('statuses/pause_detected.txt', 'r') as file:
                        pause_detected = file.read()
                    
                except FileNotFoundError:
                    pause_detected = ""

                # print('process_full_audio ongoing...')
                process_full_audio(audio_file)
                # print('process_full_audio completed...')
                user_latest_word_time = get_sgt_time()

                # Transcribe the recorded audio
                user_input = transcribe_with_whisper(audio_file, whisper_model)
                if voice_detected.lower() == 'true' and pause_detected.lower() == 'false':
                    if user_input:
                        user_input = f'(start time: {user_start_time}) {user_input}... [Speaking] (latest word time: {user_latest_word_time})'

                        # Save transcription to a file
                        try:
                            with open("transcription/input.txt", "w") as file:
                                file.write(user_input)
                                # print("Transcription saved to 'transcription/input.txt'.")
                        except Exception as e:
                            pass

                if voice_detected.lower() == 'false':
                    if user_input:
                        user_input = transcribe_with_whisper(audio_file, whisper_model)

                        user_input = f'(start time: {user_start_time}) {user_input} [Not Speaking] (latest word time: {user_latest_word_time})'

                        with open("transcription/input.txt", "w") as file:
                            file.write(user_input)
                    break
                
        else:
            with open("statuses/locked.txt", "r") as file:
                locked = file.read()    
                if locked.lower() == 'delete':
                    with open("transcription/input.txt", "w") as file:
                        file.write('')                



# Queue for audio files
audio_queue = queue.Queue()

def audio_worker():
    while True:
        audio_file = audio_queue.get()
        if audio_file is None:  # Exit condition
            # print("Audio worker exiting...")
            break
        # print(f"Processing audio file from queue: {audio_file}")
        process_and_transcribe(audio_file, whisper_model)
        audio_queue.task_done()

def execute():
    # Specify the path to the file
    file_path = 'audios/input.wav'
    
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)  # Delete the file
        # print(f"{file_path} has been deleted.")
    else:
        pass
    
    with open("transcription/input.txt", "w") as file:
        file.write('')

    # Start worker thread
    worker_thread = threading.Thread(target=audio_worker)
    worker_thread.start()
    # print("Worker thread started.")

    # llm_thread = threading.Thread(target=run)
    # llm_thread.start()

    # Add audio file to the queue
    audio_file = "audios/input.wav"
    audio_queue.put(audio_file)
    # print(f"Audio file added to the queue: {audio_file}")

    try:
        # Start processing
        start()

        # Optionally, wait for all processing to complete
        audio_queue.join()
        # print("All tasks in the audio queue have been processed.")

    except KeyboardInterrupt:
        pass
        # print("KeyboardInterrupt received. Stopping processing...")

    finally:
        # Stop the worker thread
        audio_queue.put(None)
        worker_thread.join()
        # llm_thread.join()
        # print("Worker thread has been stopped.")

# execute()


