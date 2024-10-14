from datetime import datetime
import time
import pytz

# Set timezone to Singapore Time (SGT)
sgt_tz = pytz.timezone('Asia/Singapore')

# Function to get formatted current time in Singapore Time (SGT)
def get_sgt_time():
    # Get current time in SGT
    current_time = datetime.now(sgt_tz)
    # Format time in HH:MM:SS and extended microseconds
    formatted_time = current_time.strftime('%H:%M:%S.') + f'{current_time.microsecond}'
    return formatted_time

def output_simulation():
    global speak_status, playback_active
    speak_status = True
    playback_active = True

    time.sleep(1)
    with open("ai_response.txt", "r") as file:
        ai_response = file.read()            
    # Given sentence
    sentence = ai_response

    # Get start time
    ai_start_time = get_sgt_time()

    # Split the sentence into words
    words = sentence.split()

    # Initialize an empty string to build the output
    current_content = ""

    for word in words:
        if not speak_status:  # Check speak_status in each iteration
            break
        
        ai_latest_word_time = get_sgt_time()
        # Add the next word to the current content
        current_content += word + " "
        
        # Open the file in write mode and overwrite it with the current content
        with open("transcription/output.txt", "w") as file:
            file.write(f'(start time: {ai_start_time}) ' + current_content.strip() + f" (latest word time: {ai_latest_word_time})\n")
        
        time.sleep(0.25)  # Wait before adding the next word

    speak_status = False
    playback_active = False

output_simulation()
