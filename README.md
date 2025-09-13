# Audio Tools

A collection of small CLI Python utilities for audio file processing: dccheck, monomake, and pcheck.

---

## Requirements

- Python 3.13 or higher
- numpy
- soundfile (pysoundfile)

Install dependencies:

python3 -m pip install numpy soundfile

---

## Scripts

### dccheck

Checks mono audio files for DC offset and optionally corrects it.

Usage:

python3 dccheck.py <file_or_folder> [--fix] [--zero] [--force] [--help]

Behavior:

- Scans files for DC offset and reports values. The scan does not modify files.
- Files with DC offset are shown in red.
- Stereo/multi-channel files are skipped and shown in yellow.
- After scanning, you will be prompted for action.

Flags:

- --fix     Remove DC offset. Automatically applies zero alignment. Prompts before overwriting unless --force is used.
- --zero    Aligns first sample to zero without applying DC offset. Runs automatically.
- --force   Skips prompts and overwrites files automatically.
- --help    Show help message.

Output behavior:

- If you choose not to overwrite originals, a DC_Fixed folder is created and corrected files are saved there.
- After processing, the script reports the folder location.

Examples:

- python3 dccheck.py mix.wav
- python3 dccheck.py folder_of_audio --fix
- python3 dccheck.py folder_of_audio --zero
- python3 dccheck.py folder_of_audio --fix --force

---

### monomake

Converts stereo audio files to mono.

Usage:

python3 monomake.py <file_or_folder> [--force] [--help]

Behavior:

- Scans files for stereo audio.
- Lists all files; stereo files are shown in red.
- Prompts to convert to mono and whether to overwrite originals or create a Mono/ folder.

Flags:

- --force    Skip prompts and overwrite originals automatically.
- --help     Show help message.

Examples:

- python3 monomake.py mix.wav
- python3 monomake.py folder_of_audio
- python3 monomake.py folder_of_audio --force

---

### pcheck

Checks polarity of audio files against a master file and optionally flips inverted files.

Usage:

python3 pcheck.py <master_file> <folder1> [folder2 ...] [--fix] [--help]

Behavior:

- Compares files against a master.
- Reports polarity; inverted files are shown in red.
- Prompts to flip inverted files unless --fix is used.
- If not overwriting originals, a p_fix folder is created for flipped files.

Flags:

- --fix      Automatically flips inverted files.
- --help     Show help message.

Examples:

- python3 pcheck.py master.wav folder_of_audio
- python3 pcheck.py master.wav folder_of_audio --fix

---

## Installation / Usage

1. Clone repository:

git clone https://github.com/aguila-sound/audiotools.git
cd audiotools

2. Make scripts executable (optional):

chmod +x *.py

3. Run any script:

python3 dccheck.py <file_or_folder>

Or add the repo folder to your PATH for easier CLI usage.

