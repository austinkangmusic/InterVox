
speaker_name = 'SamuelL'






with open("statuses/speaker_name.txt", "w") as file:
    file.write(speaker_name)

import os
os.environ['TRANSFORMERS_NO_TF'] = '1'





with open("transcription/input.txt", "w") as file:
    file.write('')

with open("donottouch/user_input.txt", "w") as file:
    file.write('')


with open("donottouch/halved_user_content.txt", "w") as file:
    file.write('')

with open("donottouch/chatbot_response.txt", "w") as file:
    file.write('')

with open("donottouch/chatbot_listening.txt", "w") as file:
    file.write('')      

with open("conversation_history.txt", "w") as file:
    file.write('')      

print('reset')

from thread import execute





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


# from thinking_model import thoughts_loop
import chat_utils
import files
import json

from initialize_tts import initialize_tts_model

import generate_voice
# Initialize LLM models
chat_utils.initialize()

chat_llm = chat_utils.use_chat_llm()


from initialize_whisper import initialize_whisper_model
from monitor_voice import start
import time
import threading
import pyaudio
import wave
import numpy as np
import os
from robotic_voice import if_robotic, apply_vocoder

# Load VAD model
sampling_rate = 16000
chunk_size = 512
speech_threshold = 0.9

# Global variables

buffer = b''  # Buffer to store audio data
wf_global = None  # To keep a reference to the wave file object
speak_status = True

# Initialize Whisper model
print("Initializing Whisper model...")
whisper_model = initialize_whisper_model()
print("Whisper model initialized.")





visualizer_on = False

if visualizer_on:
    from visualizer import run_visualizer, play_visualizer, stop_visualizer

















def play(file_path):
    global buffer, wf_global, speak_status, playback_active
    speak_status = True
    playback_active = True

    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return

    wf = wave.open(file_path, 'rb')
    wf_global = wf
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        data = wf.readframes(512)
        while data and speak_status:
            buffer += data
            stream.write(data)
            data = wf.readframes(512)
        
        speak_status = False
        playback_active = False
        # print("AI has stopped talking.")

        buffer = b''  # Clear buffer after saving if needed
        
        stream.stop_stream()
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        stream.close()
        wf.close()
        p.terminate()


def run():
    if if_robotic:
        play("audios/vocoder_output.wav")
    else:
        play("audios/output.wav")


# Function to transcribe audio with word timestamps using Whisper model
# Function to transcribe audio with word timestamps using Whisper model
def transcribe_ai_voice_with_whisper(audio_file, whisper_model):
    try:
        segments, info = whisper_model.transcribe(audio_file, beam_size=5, word_timestamps=True)
        
        transcription = ""
        word_timestamps = []
        
        # Collect transcription and timestamps
        for segment in segments:
            transcription += segment.text + " "
            
            # For each word in the segment, get its timestamp
            for word in segment.words:
                word_timestamps.append({
                    'word': word.word,
                    'start': word.start,
                    'end': word.end
                })
        
        return transcription.strip(), word_timestamps, info.language, info.language_probability
    except Exception as e:
        return "", [], "", 0.0

def file_to_transcribe(if_robotic):
    if if_robotic:
        apply_vocoder("audios/output.wav", "audios/vocoder_output.wav", "audios/carrier.wav")
        audio_file = 'audios/vocoder_output.wav'
    else:
        audio_file = 'audios/output.wav'
    return audio_file

def write_file_in_real_time(word_timestamps, output_file_path):
    global speak_status
    start_time = time.time()  # Start timer 
    last_word_index = 0  # To keep track of the last word printed
    ai_start_time = get_sgt_time()

    current_transcription = f"(start time: {ai_start_time})"  # To build the current transcription

    # Print word-level timestamps in real time
    while last_word_index < len(word_timestamps):
        current_time = time.time() - start_time
        
        # Check if any word's start time has been reached
        while (last_word_index < len(word_timestamps) and 
                word_timestamps[last_word_index]['start'] <= current_time):
            # Get the current word
            word_info = word_timestamps[last_word_index]
            current_transcription += word_info['word'] + " "  # Add the word to current transcription
            
            # Clean up extra spaces
            current_transcription = ' '.join(current_transcription.split())
            ai_latest_word_time = get_sgt_time()
            
            # Write the current transcription to the file, overwriting it each time
            with open(output_file_path, "w") as file:  # Open in write mode to overwrite
                file.write(current_transcription.strip() + f' (latest word time: {ai_latest_word_time})')  # Write current transcription without trailing space
            
            last_word_index += 1
            if not speak_status:
                break
        if not speak_status:
            break






















def stream_response_speak(model, prompt):
    
    chunks = []
    response_generator = model.stream(prompt)
    for chunk in response_generator:
        delta_content = chunk.content
        if delta_content is not None:
            chunks.append(delta_content)

    return ''.join(chunks)






def stream_response(model, system_prompt, conversation_history):
    # Combine system prompt, conversation history, and user input
    full_conversation = [{"role": "system", "content": system_prompt}] + conversation_history
    
    chunks = []
    response_generator = model.stream(full_conversation)
    for chunk in response_generator:
        delta_content = chunk.content
        if delta_content is not None:
            chunks.append(delta_content)
    #         print(delta_content, end="", flush=True)
    # print('\n')
    return ''.join(chunks)

def save_response(text):
    with open('ai_response.txt', 'w', encoding='utf-8') as file:
        # Convert list to string if text is a list
        if isinstance(text, list):
            text = '\n'.join(text)  # Join list elements into a single string with newline
        file.write(text)



def locking_system(user_input):
    if '[Not Speaking]' in user_input:
        with open("statuses/locked.txt", "w") as file:
            file.write('delete')   
    else:
        with open("statuses/locked.txt", "w") as file:
            file.write('Not Delete')                        


listening = False        
conversation_history = []    
pretty_conversation_history = []
with open("statuses/locked.txt", "w") as file:
    file.write('Not delete')



def chat_bot(conversation_history, user_input, halved_user_content, chatbot_listening, chatbot_response):
    global speak_status, playback_active, listening, speaker_name

    # Initialize an empty conversation history
    conversation_history = []
    listening = False        


    # Read from conversation_history.txt and store the content into conversation_history
    with open('conversation_history.txt', 'r') as file:
        lines = file.readlines()

    # Parse each line to convert from JSON strings to Python objects
    for line in lines:
        try:
            # First, strip newlines, then load the JSON string into Python dict
            conversation_history.append(json.loads(line.strip()))
        except json.JSONDecodeError as e:
            print(f"Error parsing line: {line}, error: {e}")


    while True:
        chat_replied = False
        system_md = files.read_file("prompts/system.md")
        personality = files.read_file(f"prompts/personalities/{speaker_name}.md")
        system_prompt = f"{personality}\n\n{system_md}"
        try:
            with open("transcription/input.txt", "r") as file:
                user_input = file.read()
                 
        except:
            user_input = ''
        with open("donottouch/user_input.txt", "w") as file:
            file.write(user_input)


        # user_input = input('\nUser:\n')
        conversation_history.append({"role": "user", "content": user_input})


        words = user_input.split()  # Split the input into words

        # If there's only one word, just return it
        if len(words) <= 1:
            halved_user_content = user_input
        else:
            half_index = len(words) // 2  # Calculate the index for half
            halved_user = ' '.join(words[:half_index])  # Join the first half of words
            halved_user_content = f'{halved_user}... [Speaking]'
        with open("donottouch/halved_user_content.txt", "w") as file:
            file.write(halved_user_content)





        
        # Stream the response with the system prompt, user input, and conversation history
        chatbot_response = stream_response(chat_llm, system_prompt, conversation_history)
        chat_replied = True
        with open("donottouch/chatbot_response.txt", "w") as file:
            file.write(chatbot_response)

        conversation_history.append({"role": "ai", "content": chatbot_response})





        tool_name, tool_args = chat_utils.extract_tool_info(chatbot_response)
        with open("statuses/status.txt", "w") as file:
            file.write(tool_name)




        if tool_name in ('listen', 'ignore'):
            listening = True
            chatbot_listening = chatbot_response
            with open("donottouch/chatbot_listening.txt", "w") as file:
                file.write(chatbot_listening)            
            conversation_history = conversation_history[:-2] # REMOVES LAST TWO IF LISTEN
        else:
            if listening:
                conversation_history = conversation_history[:-2]
                conversation_history.append({"role": "user", "content": halved_user_content})
                conversation_history.append({"role": "ai", "content": chatbot_listening})       
                conversation_history.append({"role": "user", "content": user_input})                 
                conversation_history.append({"role": "ai", "content": chatbot_response})
                listening = False

        if '[Not Speaking]' in user_input and tool_name in ('listen', 'ignore'):
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "ai", "content": chatbot_response})
        if chat_replied:
            locking_system(user_input)

        text_to_save = tool_args.get('text', '')
        save_response(text_to_save)
        # print(chatbot_response)

        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]


        # Open a file in write mode
        with open('conversation_history.txt', 'w') as file:
            for item in conversation_history:
                file.write(json.dumps(item) + '\n')
        # print("\n\n\nCONVERSATION HISTORY\n\n\n", conversation_history)

        if tool_name in ('response', 'backchannel', 'interrupt'):
            spoken_ai_response = tool_args.get('text', '')
            print('\nAI:', spoken_ai_response)
            try:
                with open("transcription/output.txt", "w") as file:
                    file.write(spoken_ai_response)
            except Exception as e:
                print("Error writing to file: ", e)


            generate_voice.run()

            audio_file = file_to_transcribe(if_robotic)

            # Get transcription, timestamps, language info
            ai_transcription, word_timestamps, detected_language, language_probability = transcribe_ai_voice_with_whisper(audio_file, whisper_model)

            # Print results
            # print(f"Transcription: {ai_transcription}")
            # print(f"Detected language: {detected_language} (Probability: {language_probability})")

            # Write output to file in real time
            output_file_path = "transcription/output.txt"

            play_audio_thread = threading.Thread(target=run)
            play_audio_thread.start()

            save_stream_words = threading.Thread(target=write_file_in_real_time, args=(word_timestamps, output_file_path))
            save_stream_words.start()



            # print(f"Transcription written to {output_file_path}")
            if playback_active:
                print('playback_active is active')

                if visualizer_on:

                    play_visualizer()

                with open("transcription/output.txt", "w") as file:
                    file.write('')   

                with open("statuses/locked.txt", "w") as file:
                    file.write('Not delete')   
                while True:
                    time.sleep(0.1)
                    speak_system_md = files.read_file("prompts/speak_system.md")
                    speak_status_md = files.read_file("prompts/speak_status.md")

                    with open("transcription/output.txt", "r") as file:
                        spoken_ai_response = file.read()
                        
                    with open("transcription/input.txt", "r") as file:
                        spoken_user_input = file.read()
                    speak_system_prompt = f"{personality}\n\n{speak_system_md}\n{speak_status_md}\n{conversation_history}\nCurrent spoken words by you: '{spoken_ai_response}'\nCurrent spoken words by the user: '{spoken_user_input}'"
                    with open("speak_system_prompt.txt", "w") as file:
                        file.write(speak_system_prompt)   

                    prompt = [{"role": "system", "content": speak_system_prompt}]
                    speak_status_response = stream_response_speak(chat_llm, prompt)

                    # Parse the JSON string into a Python dictionary
                    response_dict = json.loads(speak_status_response)

                    # Extract the value of the 'speak' key
                    speak_status_str = response_dict.get('speak')
                    print(speak_status_str)

                    if speak_status_str.lower() == 'true':
                        speak_status = True
                    else:
                        if spoken_user_input != '':
                            if visualizer_on:
                                stop_visualizer()

                            speak_status = False
                            interrupted_ai_system = f"You have decided to stop speaking.\nYour spoken words: {spoken_ai_response}\n The user's spoken words: {spoken_user_input}"
                            conversation_history.append({"role": "system", "content": interrupted_ai_system})
                            print('appended stopped speaking')

                        print("Breaking the loop 1...")
                        break
                    if not playback_active:
                        print('not active playback')
                        if spoken_user_input != '':
                            finished_speaking_system = f"You have finished speaking; however, the user has overlapped your words with their own.\nYour spoken words: {spoken_ai_response}\nThe user's spoken words: {spoken_user_input}"
                            conversation_history.append({"role": "system", "content": finished_speaking_system})
                            print('appended overlapped speaking')
                        else:
                            finished_speaking_system = f'You have finished speaking without any interruptions.\nYour spoken words: {spoken_ai_response}'
                            conversation_history.append({"role": "system", "content": finished_speaking_system})
                            print('appended no interruption speaking')

                        print("Breaking the loop 2...")
                        break
        if user_input == '':
            print("Breaking the loop 3...")
            break








def input_simulation():
    while True:
        time.sleep(1)
        # Given sentence
        sentence = input("\nUser:\n")


        # Get start and end times
        user_start_time = get_sgt_time()

        # Split the sentence into words
        words = sentence.split()

        # Initialize an empty string to build the output
        current_content = ""

        for word in words:
            user_latest_word_time = get_sgt_time()

            # Add the next word to the current content
            current_content += word + " "

            # Open the file in write mode and overwrite it with the current content
            with open("transcription/input.txt", "w") as file:
                file.write(f'(start time: {user_start_time}) ' + current_content.strip() + f"... [Speaking] (latest word time: {user_latest_word_time})\n")  # Add [Speaking] after each incremental addition
            
            time.sleep(1)  # Wait 2 seconds before adding the next word


        user_latest_word_time = get_sgt_time()
        # After the loop, write the complete sentence with [Not Speaking]
        with open("transcription/input.txt", "w") as file:
            file.write(f'(start time: {user_start_time}) ' + sentence + f" [Not Speaking] (latest word time: {user_latest_word_time})'\n")  # Write the complete sentence with [Not Speaking]
        while True:
            with open("statuses/locked.txt", "r") as file:
                locked = file.read()    
                if locked.lower() == 'delete':
                    with open("transcription/input.txt", "w") as file:
                        file.write('') 
                    break
                
import threading

def run_thread():
    if visualizer_on:
        visualizer_thread = threading.Thread(target=run_visualizer)
        visualizer_thread.start()

    with open("donottouch/user_input.txt", "r") as file:
        user_input = file.read()
    with open("donottouch/halved_user_content.txt", "r") as file:
        halved_user_content = file.read()
    with open("donottouch/chatbot_response.txt", "r") as file:
        chatbot_response = file.read()
    with open("donottouch/chatbot_listening.txt", "r") as file:
        chatbot_listening = file.read()


    simulation = threading.Thread(target=input_simulation)
    simulation.start()
    # real_time_transcription = threading.Thread(target=execute)
    # real_time_transcription.start()

    while True:
        time.sleep(1)
        try:
            with open("transcription/input.txt", "r") as file:
                user_input = file.read()
                    
        except:
            user_input = ''
        
        if user_input == '':
            pass
        else:
            chat_bot(conversation_history, user_input, halved_user_content, chatbot_listening, chatbot_response)




run_thread()
# Computer will never... [Speaking]
# Computer will never avail. [Not Speaking]
# I am going to shut you down now. [Not Speaking]

# Computer will never avail. What do you think? [Not Speaking]

# Hey umm... I am kinda sad and... uhh.. [Speaking]

# Hey... [Speaking]
# Hey umm... [Pause] 
# Hey umm, could you... [Speaking]
# Hey umm, could you help me with some stuff like... [Speaking]
# Hey umm, could you help me with some stuff like... [Pause] 
# Hey umm, could you help me with some stuff like some math questions? [Paused]  
# Hey umm, could you help me with some stuff like some math questions? [Not Speaking]


# Well I... [Speaking]
# Well I am a little bit dumb so... [pause]
# Well I am a little bit dumb so [Not Speaking]

# What is... [Speaking]
# What is 2+2? [Pause]
# What is 2+2? [Not Speaking]


# Hey... [Voice Active]  
# Hey umm... [Voice Inactive]  
# Hey umm, could you... [Voice Active]  
# Hey umm, could you help me wit/?h some stuff like... [Voice Active]  
# Hey umm, could you help me with some stuff like... [Voice Inactive]  
# Hey umm, could you help me with some stuff like some math questions? [Voice Active]  
# Hey umm, could you help me with some stuff like some math questions? [Voice Inactive]  


#Hey, could you explain what AGI is? Long.
#Okay, wait, I got a call. Hold on yea?
#Okay, wait, I got a call. Hold on yea?
#SORRY MY BAD WAIT! Damn calls...
#Shhhhh!

#SORRY MY BAD WAIT! Damn calls.. I hate it when they call me while you are still spekaing. It's interrupting me so much sigh. Hold on okay?

#Look, I'm on the call. Have some fucking respect will ya?!

#I am testing you speech ability. So whatever words I spoken, you must interrupt me at all course got it?


#Hey, tell me wat's your name and how do you feel about having such a name.
#NO WAY! MY SISTER'S NAME IS ALSO CALLED EMMA!

#I KNOW!!

#SHUT UP! I'M ON A FUCKING PHONE CALL!

#No I'm not asking about you being helpful or not, just... ok nvm continue. I should let you finish speaking first.
#Wow, you aren't a mute huh. Why so quiet just now?


#You are conscious?! Nah I dont believe you.


#Wait wait, What purpose you say?

#Okay okay, whatever you say.

#Okay okay. Tell me what's the time now pls.

#Wait, I need to pee

#Quiet, junior.


#Oh shit, it means it's time to game!


#Oi oi Do you mind?! 

#Okay okay. Umm, what is the time now?

#Do you have a brain?