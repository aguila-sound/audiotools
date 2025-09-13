#!/usr/bin/env python3
import sys
import os
import soundfile as sf
import numpy as np

SUPPORTED_EXT = ('.wav', '.WAV', '.aif', '.AIF', '.aiff', '.AIFF', '.flac', '.FLAC')
DC_THRESHOLD = 1e-5

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_help():
    help_text = f"""
Usage: {os.path.basename(sys.argv[0])} <file_or_folder> [--fix] [--zero] [--force] [--help]

Checks mono audio files for DC offset and optionally corrects it.

Supported file types: {', '.join(SUPPORTED_EXT)} (mono only)

Default behavior (no flags):
  - Scans the given file(s) for DC offset and reports the values for each file.
  - The scan itself does not touch the files in any destructive way.
  - Files with DC offset are shown in {RED}red{RESET}.
  - Stereo/multi-channel files are skipped and shown in {YELLOW}yellow{RESET}.
  - You will then be prompted with what you would like to do.

Flags:
  --fix     Removes DC offset and zero aligns the file. Prompts before overwriting unless --force is used.
  --zero    Aligns the first sample to zero only (no DC offset applied). Runs automatically, no prompt.
  --force   Skips confirmation prompts when using --fix. Also overwrites files automatically.
  --help    Show this help message and exit.

Output behavior:
  - If you choose not to overwrite, a new folder 'DC_Fixed' is created in the same directory and corrected files are placed there.
  - The script reports where new files are saved.

Examples:
  {os.path.basename(sys.argv[0])} mix.wav
      → Reports DC offset only (mono files). Stereo files are skipped.

  {os.path.basename(sys.argv[0])} folder_of_audio --fix
      → Prompts to remove DC offset and zero-align mono files.

  {os.path.basename(sys.argv[0])} folder_of_audio --zero
      → Aligns mono files to zero-crossing at start (auto overwrite).

  {os.path.basename(sys.argv[0])} folder_of_audio --fix --force
      → Removes DC offset and zero-aligns mono files, overwriting files without prompting.
"""
    print(help_text)
    sys.exit(0)

def process_file(file_path):
    try:
        data, _ = sf.read(file_path)
        if data.ndim > 1 and data.shape[1] > 1:
            print(f"{YELLOW}Skipping {os.path.basename(file_path)}: stereo/multi-channel detected{RESET}")
            return None
        mean_val = np.mean(data) if data.ndim == 1 else np.mean(data, axis=0)
        if np.abs(mean_val) > DC_THRESHOLD:
            return (file_path, mean_val)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return None

def apply_filter(file_list, overwrite=False, zero_align=True):
    output_folder = None
    for file_path, mean_val in file_list:
        data, samplerate = sf.read(file_path)
        data = data - mean_val
        if zero_align:
            if data.ndim > 1:
                data[0, :] = 0
            else:
                data[0] = 0
        if overwrite:
            out_file = file_path
        else:
            if not output_folder:
                output_folder = os.path.join(os.path.dirname(file_list[0][0]), "DC_Fixed")
                os.makedirs(output_folder, exist_ok=True)
            out_file = os.path.join(output_folder, os.path.basename(file_path))
        sf.write(out_file, data, samplerate)
        print(f"Filtered: {os.path.basename(out_file)}")
    if not overwrite and output_folder:
        print(f"\nAll corrected files saved to: {output_folder}")

def scan_path(path):
    files_with_offset = []
    files_to_scan = []
    if os.path.isfile(path) and path.endswith(SUPPORTED_EXT):
        files_to_scan.append(path)
    else:
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(SUPPORTED_EXT):
                    files_to_scan.append(os.path.join(root, f))
    for file_path in files_to_scan:
        res = process_file(file_path)
        if res:
            files_with_offset.append(res)
    return files_to_scan, files_with_offset

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print_help()
    path = sys.argv[1]
    apply_all = '--fix' in sys.argv
    force_all = '--force' in sys.argv
    zero_only = '--zero' in sys.argv
    all_files, files_with_offset = scan_path(path)
    if not files_with_offset and not zero_only:
        print("No mono files exceeding DC threshold found.")
        return
    if files_with_offset:
        print(f"\nFound {len(files_with_offset)} mono file(s) that could use a filter:")
        for file_path, mean_val in files_with_offset:
            print(f"  {RED}{os.path.basename(file_path)} → {mean_val:.8f}{RESET}")
    if apply_all or zero_only:
        overwrite = force_all
        apply_filter(files_with_offset, overwrite=overwrite, zero_align=True)
    else:
        apply_only = input("\nDo you want to apply the filter only to these files? (y/n): ").strip().lower() == 'y'
        if apply_only:
            overwrite = input("Overwrite original files? (y/n): ").strip().lower() == 'y'
            apply_filter(files_with_offset, overwrite=overwrite, zero_align=True)

if __name__ == "__main__":
    main()
