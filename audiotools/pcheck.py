#!/usr/bin/env python3
import os
import sys
import glob
import soundfile as sf
import numpy as np

RED = "\033[91m"
RESET = "\033[0m"

SUPPORTED_EXT = ["wav", "WAV", "aif", "AIF", "aiff", "AIFF", "flac", "FLAC"]

def show_help():
    print(f"""
Usage: pcheck <master_file> <folder1> [folder2 ...] [--fix] [--help]

Checks polarity of audio files against a master file and optionally flips inverted files.

Supported file types: {', '.join(SUPPORTED_EXT)}

Default behavior (no --fix):
  - Scans all files in the given folder(s) against the master file.
  - Reports polarity of each file.
  - Inverted files are shown in {RED}red{RESET}.
  - Prompts you if you want to flip the inverted files.

Flags:
  --fix      Automatically flips inverted files (no prompt). If user denies overwrite, files go to 'p_fix' folder.
  --help     Show this help message and exit.
""")
    sys.exit(0)

def find_audio_files(folder):
    files = []
    for ext in SUPPORTED_EXT:
        files.extend(glob.glob(os.path.join(folder, f"*.{ext}")))
    return files

def read_audio(file_path):
    data, sr = sf.read(file_path, always_2d=True)
    if data.shape[1] > 1:
        data = np.mean(data, axis=1)
    return data

def check_polarity(master, test):
    length = min(len(master), len(test))
    return np.sum(master[:length] * test[:length]) >= 0

def invert_audio(file_path, output_path=None):
    data, sr = sf.read(file_path)
    data = -data
    sf.write(output_path or file_path, data, sr)

def main():
    if len(sys.argv) < 3 or '--help' in sys.argv:
        show_help()
    master_file = sys.argv[1]
    args = sys.argv[2:]
    fix_mode = '--fix' in args
    folders = [a for a in args if a != '--fix']
    master_audio = read_audio(master_file)
    inverted_files = []
    for folder in folders:
        folder = os.path.abspath(folder)
        files = find_audio_files(folder)
        if not files:
            print(f"No valid test files found in {folder}.")
            continue
        for f in files:
            try:
                test_audio = read_audio(f)
            except Exception as e:
                print(f"Error reading {f}: {e}")
                continue
            if check_polarity(master_audio, test_audio):
                print(f"{os.path.basename(f)} → In polarity")
            else:
                print(f"{RED}{os.path.basename(f)} → Inverted{RESET}")
                inverted_files.append(f)
    if inverted_files:
        print(f"\nFound {len(inverted_files)} inverted file(s).")
        if fix_mode:
            overwrite = input("Overwrite original files? (y/n): ").strip().lower() == 'y'
            output_folder = None
            if not overwrite:
                output_folder = os.path.join(os.path.dirname(inverted_files[0]), "p_fix")
                os.makedirs(output_folder, exist_ok=True)
            for f in inverted_files:
                invert_audio(f, os.path.join(output_folder, os.path.basename(f)) if output_folder else f)
                print(f"Flipped: {os.path.basename(f)}")
            if output_folder:
                print(f"\nAll flipped files saved to: {output_folder}")
        else:
            do_fix = input("Do you want to flip the inverted ones? (y/n): ").strip().lower() == "y"
            if do_fix:
                for f in inverted_files:
                    invert_audio(f)
                    print(f"Flipped: {os.path.basename(f)}")
    else:
        print("\nNo inverted files found.")

if __name__ == "__main__":
    main()
