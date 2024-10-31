import os
import platform
import subprocess

def clear_screen():
    system = platform.system()
    if system == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# 2024 Oct,31, pending ... everything; real cli menu needed BEFORE starting to analyze a file/url
def run_cho(): 
    command = ['python', './engine/cho.py']
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command)

def main():
    clear_screen()
    print("Starting cho.py...")
    run_cho()

if __name__ == "__main__":
    main()
