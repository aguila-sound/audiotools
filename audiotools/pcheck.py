#!/Users/Lazz/polarity_en/bin/python3
import os
import sys
import glob
import soundfile as sf
import numpy as np

# ANSI colors
RED = "\033[91m"
RESET = "\033[0m"

SUPPORTED_EXT = ["wav", "WAV", "aif", "AIF", "aiff", "AIFF", "flac", "FLAC"]

def show_help():
    print(f"""
Usage: pcheck <master_file> <file_or_folder1> [file_or_folder2 ...] [--fix] [--help]

Checks polarity of audio files against a master file and optionally flips inverted files.

Supported file types: .wav, .aif, .aiff, .flac

Default behavior (no --fix):
  - Scans all files in the given file(s) or folder(s) against the master file.
  - Reports polarity of each file.
  - Inverted files are shown in {RED}red{RESET}.
  - Prompts you if you want to flip the inverted files.
  - If you choose not to overwrite originals, a new folder 'p_fix' is created and flipped files are saved there.

Flags:
  --fix      Automatically flips inverted files (no prompt, overwrites originals).
  --help     Show this help message and exit.

Examples:
  pcheck master.wav folder_of_audio
      → Scans folder, shows inverted files in red, prompts to flip them. 
         If you decline overwrite, flipped files go into 'p_fix'.

  pcheck master.wav folder_of_audio --fix
      → Scans folder and automatically flips inverted files, overwriting originals.

  pcheck master.wav testfile.wav
      → Checks just that single file.
""")
    sys.exit(0)

def find_audio_files(path):
    """Return a list of supported audio files from either a folder or a single file."""
    path = os.path.abspath(path)
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1][1:]
        if ext in SUPPORTED_EXT:
            return [path]
        else:
            return []
    elif os.path.isdir(path):
        files = []
        for ext in SUPPORTED_EXT:
            pattern = os.path.join(path, f"*.{ext}")
            files.extend(glob.glob(pattern))
        return files
    return []

def read_audio(file_path):
    """Read audio file and return mono float32 array"""
    data, sr = sf.read(file_path, always_2d=True)
    if data.shape[1] > 1:
        data = np.mean(data, axis=1)
    return data

def check_polarity(master, test):
    """Return True if in polarity, False if inverted"""
    length = min(len(master), len(test))
    corr = np.sum(master[:length] * test[:length])
    return corr >= 0

def invert_audio(file_path, out_path=None):
    """Invert audio in place or save to out_path"""
    data, sr = sf.read(file_path)
    data = -data
    target_path = out_path if out_path else file_path
    sf.write(target_path, data, sr)

def main():
    if len(sys.argv) < 3 or '--help' in sys.argv:
        show_help()

    master_file = sys.argv[1]
    args = sys.argv[2:]

    fix_mode = False
    paths = []
    for arg in args:
        if arg == "--fix":
            fix_mode = True
        else:
            paths.append(arg)

    print(f"Comparing against {master_file}...\n")

    master_audio = read_audio(master_file)
    inverted_files = []

    for path in paths:
        files = find_audio_files(path)
        if not files:
            print(f"No valid test files found in {path}.")
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

    if not inverted_files:
        print("\nNo inverted files found.")
        return

    print(f"\nFound {len(inverted_files)} inverted file(s).")

    if fix_mode:
        for f in inverted_files:
            invert_audio(f)
            print(f"Flipped: {os.path.basename(f)}")
    else:
        do_fix = input("Do you want to flip the inverted ones? (y/n): ").strip().lower()
        if do_fix != "y":
            print("No files were flipped.")
            return

        overwrite = input("Overwrite original files? (y/n): ").strip().lower() == 'y'

        output_folder = None
        if not overwrite:
            # Save flipped files in p_fix (next to first path)
            first_path = os.path.abspath(paths[0])
            if os.path.isdir(first_path):
                base_folder = first_path
            else:
                base_folder = os.path.dirname(first_path)
            output_folder = os.path.join(base_folder, "p_fix")
            os.makedirs(output_folder, exist_ok=True)
            print(f"\nFlipped files will be saved to: {output_folder}")

        for f in inverted_files:
            if overwrite:
                invert_audio(f)
            else:
                out_path = os.path.join(output_folder, os.path.basename(f))
                invert_audio(f, out_path=out_path)
            print(f"Flipped: {os.path.basename(f)}")

if __name__ == "__main__":
    main()
