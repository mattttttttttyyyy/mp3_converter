import json
import os
import sys
import tkinter as tk
from tkinter import filedialog

from pydub import AudioSegment

def load_converted_files(log_file):
    if not os.path.exists(log_file):
        return set()
    with open(log_file) as file:
        return set(line.strip() for line in file)


def save_converted_file(log_file, file_path):
    with open(log_file, 'a') as file:
        file.write(file_path + '\n')


def convert_wav_to_mp3(input_folder, output_folder, log_file='converted_files.txt'):
    if not os.path.isdir(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)

    converted_files = load_converted_files(log_file)
    print(f"Loaded {len(converted_files)} already converted files from '{log_file}'.")

    found_files = False

    for root, _, files in os.walk(input_folder):
        for file_name in files:
            if file_name.endswith('.wav'):
                found_files = True
                wav_path = os.path.join(root, file_name)
                mp3_name = f"{os.path.splitext(file_name)[0]}.mp3"
                mp3_path = os.path.join(output_folder, mp3_name)

                if mp3_path in converted_files:
                    print(f"Skipping already converted file: {mp3_name}")
                    continue

                try:
                    print(f"Converting {wav_path} to {mp3_path}...")
                    sound = AudioSegment.from_wav(wav_path)
                    sound.export(mp3_path, format="mp3")

                    save_converted_file(log_file, mp3_path)
                    print(f"Successfully converted and saved: {mp3_path}")

                except Exception as e:
                    print(f"Failed to convert {wav_path}. Error: {e}")

    if not found_files:
        print("No .wav files found in the input folder.")


def select_folder(folder_type):
    root = tk.Tk()
    root.withdraw()

    print("Please select " + folder_type + " folder.")

    folder_path = filedialog.askdirectory(title="Select Folder: " + folder_type)

    if folder_path:
        print("Selected folder:", folder_path)
        return folder_path
    else:
        print("No folder selected")
        sys.exit()


def check_existing_config():
    if os.path.exists("settings.json"):
        with open("settings.json", 'r') as file:
            saved_settings = json.load(file)
    else:
        saved_settings = {}
    return saved_settings


def save_settings(input_folder_to_save, output_folder_to_save):
    settings_to_save = {"input": input_folder_to_save, "output": output_folder_to_save}
    with open("settings.json", 'a', encoding='utf-8') as file:
        json.dump(settings_to_save, file, indent=4)


if __name__ == "__main__":
    settings = check_existing_config()
    input_folder = ""
    output_folder = ""

    if settings == {}:
        input_folder = select_folder("input")
        output_folder = select_folder("output")
        save_settings(input_folder, output_folder)
    else:
        keep_settings = input("Would you like to use last configuration [y/n]? ")
        if keep_settings.lower() == 'y':
            input_folder = settings["input"]
            output_folder = settings["output"]
        elif keep_settings.lower() == 'n':
            input_folder = select_folder("input")
            output_folder = select_folder("output")
        else:
            print("Unrecognised entry")
            sys.exit()

    convert_wav_to_mp3(input_folder, output_folder)
