import subprocess
import os
import platform

def clear_screen():
    system = platform.system()
    if system == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def run_cho():
    command = ['python', 'cho.py']
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command)

def main():
    clear_screen()
    print("Starting cho.py...")
    run_cho()

if __name__ == "__main__":
    main()
