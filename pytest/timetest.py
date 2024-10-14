import time
from rich.console import Console
from rich.live import Live

console = Console()

def input_simulation():
    while True:
        # Simulate user input
        sentence = input("\nUser:\n")

        # Split the sentence into words
        words = sentence.split()

        # Initialize an empty string to build the output
        current_content = ""

        with Live("", refresh_per_second=10) as live:  # Live output for dynamic content
            for word in words:
                # Add the next word to the current content
                current_content += word + " "
                
                # Update the live display with the current content prefixed with "Spoken: "
                live.update(f"Spoken: {current_content}")
                time.sleep(0.5)  # Adjust the delay as needed

# Call the function to run the simulation
input_simulation()
