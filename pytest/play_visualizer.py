from visualizer import run_visualizer, play_visualizer, stop_visualizer
import threading
visualizer_thread = threading.Thread(target=run_visualizer)
visualizer_thread.start()


def main():
    while True:
        command = input("Enter 'play' to play audio, 'stop' to stop audio, or 'quit' to exit: ").strip().lower()
        if command == 'play':
            play_visualizer()
        elif command == 'stop':
            stop_visualizer()
        elif command == 'quit':
            break



if __name__ == "__main__":
    main()
