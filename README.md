# WAV to MP3 Converter

A Python tool for batch converting `.wav` files to `.mp3` format. This script uses the `pydub` library and a simple Tkinter-based GUI for folder selection. It also supports saving and reusing previous input/output folder configurations and maintains a log of already converted files to avoid duplicates.

## Features
- Batch conversion of `.wav` to `.mp3` files.
- Folder selection via GUI.
- Saves and loads conversion history to skip already processed files.
- Configurable input and output directories with settings stored in `settings.json`.

## Dependencies
- `pydub`
- `tkinter`
- `ffmpeg` or `libav` (for audio processing)

## Usage
1. Run the script.
2. Select the input folder containing `.wav` files.
3. Select the output folder where `.mp3` files will be saved.
4. The script will convert the files and skip already processed files.

## Configuration
The script saves the folder paths in a `settings.json` file for future use. If no configuration is found, the user will be prompted to select the folders again. If a configuration exists, the user can choose whether to use it or specify new folders.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
