import json
import os
import sys
import tkinter as tk
from tkinter import filedialog
import subprocess
import re

def load_converted_files(log_file):
    if not os.path.exists(log_file):
        with open(log_file, 'w'):
            pass
        return set()
    with open(log_file) as file:
        return set(line.strip() for line in file)

def save_converted_file(log_file, file_path):
    base_name = os.path.basename(file_path)
    with open(log_file, 'a') as file:
        file.write(base_name + '\n')

def detect_silence_ffmpeg(input_file, silence_threshold=-30, min_silence_duration=60):
    print(f"Detecting silence in {input_file} using ffmpeg...")

    command = [
        "ffmpeg", "-i", input_file, "-af",
        f"silencedetect=noise={silence_threshold}dB:d={min_silence_duration}",
        "-f", "null", "-"
    ]

    process = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    output = process.stderr

    silence_segments = []
    for match in re.finditer(r"silence_start: (\d+\.\d+)", output):
        silence_start = float(match.group(1))
        silence_segments.append(silence_start)

    print(f"Detected {len(silence_segments)} silence points using ffmpeg.")
    return silence_segments

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
                base_name = os.path.splitext(file_name)[0]

                if base_name + ".wav" in converted_files:
                    print(f"Skipping already converted file: {wav_path}")
                    continue

                try:
                    print(f"Processing {wav_path}...")

                    silence_points = detect_silence_ffmpeg(wav_path)

                    if len(silence_points) == 0:
                        mp3_path = os.path.join(output_folder, f"{base_name}.mp3")
                        print(f"Exporting full audio to {mp3_path}...")
                        subprocess.run(["ffmpeg", "-i", wav_path, "-b:a", "64k", mp3_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"Successfully converted and saved: {mp3_path}")
                    else:
                        prev_time = 0
                        for idx, start_time in enumerate(silence_points):
                            segment_path = os.path.join(output_folder, f"{base_name}_part{idx+1}.mp3")

                            print(f"Exporting segment {idx+1} (from {prev_time}s to {start_time}s) to {segment_path}...")
                            subprocess.run(["ffmpeg", "-i", wav_path, "-ss", str(prev_time), "-to", str(start_time), "-b:a", "64k", segment_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            print(f"Saved segment {idx+1} as {segment_path}")
                            prev_time = start_time

                        final_segment_path = os.path.join(output_folder, f"{base_name}_part{len(silence_points)+1}.mp3")
                        print(f"Exporting final segment (from {prev_time}s to end) to {final_segment_path}...")
                        subprocess.run(["ffmpeg", "-i", wav_path, "-ss", str(prev_time), "-b:a", "64k", final_segment_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"Saved final segment as {final_segment_path}")

                    save_converted_file(log_file, wav_path)

                except Exception as e:
                    print(f"Failed to process {wav_path}. Error: {e}")

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
    if not os.path.exists("settings.json"):
        with open("settings.json", 'w') as file:
            json.dump({}, file)
        return {}

    with open("settings.json", 'r') as file:
        return json.load(file)

def save_settings(input_folder_to_save, output_folder_to_save):
    settings_to_save = {"input": input_folder_to_save, "output": output_folder_to_save}
    with open("settings.json", 'w', encoding='utf-8') as file:
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
