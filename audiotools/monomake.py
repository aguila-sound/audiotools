#!/usr/bin/env python3
import sys
import os
import soundfile as sf
import numpy as np

SUPPORTED_EXT = ('.wav', '.WAV', '.aif', '.AIF', '.aiff', '.AIFF', '.flac', '.FLAC')

RED = "\033[91m"
RESET = "\033[0m"

def show_help():
    print(f"""
Usage: monomake <file_or_folder> [--force] [--help]

Converts stereo audio files to mono.

Supported file types: {', '.join(SUPPORTED_EXT)}

Default behavior (no flags):
  - Scans the given file(s) for stereo files.
  - Lists all files found, marking stereo files in {RED}red{RESET}.
  - Prompts you to confirm conversion to mono.
  - Prompts you whether to overwrite originals or create new files in a Mono/ folder.

Flags:
  --force    Skip all prompts and overwrite original files automatically.
  --help     Show this help message and exit.

Output behavior:
  - If you choose not to overwrite, a new folder 'Mono' is created in the same directory and converted files are placed there.

Examples:
  monomake mix.wav
      → Prompts to convert mix.wav to mono, asks about overwriting.

  monomake folder_of_audio --force
      → Converts all files to mono automatically, overwriting originals without prompting.
""")
    sys.exit(0)

def make_mono(file_path, overwrite=False):
    try:
        data, samplerate = sf.read(file_path)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        if overwrite:
            out_file = file_path
        else:
            mono_folder = os.path.join(os.path.dirname(file_path), "Mono")
            os.makedirs(mono_folder, exist_ok=True)
            out_file = os.path.join(mono_folder, os.path.basename(file_path))
        sf.write(out_file, data, samplerate)
        return out_file
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def gather_files(path):
    files = []
    if os.path.isfile(path) and path.endswith(SUPPORTED_EXT):
        files.append(path)
    else:
        for root, _, fs in os.walk(path):
            for f in fs:
                if f.endswith(SUPPORTED_EXT):
                    files.append(os.path.join(root, f))
    return files

def is_stereo(file_path):
    try:
        data, _ = sf.read(file_path)
        return data.ndim > 1 and data.shape[1] > 1
    except:
        return False

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        show_help()
    path = sys.argv[1]
    force = '--force' in sys.argv
    files = gather_files(path)
    if not files:
        print("No supported audio files found.")
        return
    stereo_files = [f for f in files if is_stereo(f)]
    mono_files = [f for f in files if f not in stereo_files]
    print(f"Found {len(files)} file(s) to convert to mono:")
    for f in stereo_files:
        print(f"  {RED}{f} (stereo){RESET}")
    for f in mono_files:
        print(f"  {f} (mono)")
    if not force:
        proceed = input("\nDo you want to convert these files to mono? (y/n): ").strip().lower() == 'y'
        if not proceed:
            print("No files were processed.")
            return
        overwrite = input("Overwrite original files? (y/n): ").strip().lower() == 'y'
    else:
        overwrite = True
    converted_count = 0
    skipped_count = 0
    for f in files:
        if is_stereo(f):
            result = make_mono(f, overwrite=overwrite)
            if result:
                converted_count += 1
        else:
            skipped_count += 1
    if not overwrite:
        print(f"\nConverted files saved in: {os.path.join(os.path.dirname(files[0]), 'Mono')}")
    print(f"\nSummary:\n  Converted to mono: {converted_count}\n  Already mono/skipped: {skipped_count}")

if __name__ == "__main__":
    main()
