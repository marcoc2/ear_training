
# Audio Training for Music Production

This repository contains Python scripts for audio training and impulse response (IR) generation, designed to improve skills in recognizing EQ changes, panning positions, and reverb types. Additionally, a script is included for generating custom IRs from audio processed with reverb. Each script provides a unique training experience or audio processing functionality.

## Setup

1. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
   ```

2. **Install Dependencies**:
   ```bash
   pip install numpy scipy soundfile sounddevice pyqt5
   ```

## Scripts Overview

### 1. Equalization Training (`equalization_training.py`)

- **Purpose**: Helps users identify changes in specific frequency ranges by applying EQ boosts to random frequency bands in a 5-second audio clip.
- **Instructions**:
  - Run the script: `python equalization_training.py`
  - Load an audio file, then listen to the original and altered versions.
  - Use the frequency slider to guess the altered frequency range.
  - After each guess, the script will select a new clip and boost a different frequency.

### 2. Panning Training (`panning_training.py`)

- **Purpose**: Trains users to detect the panning position (left or right balance) of an audio clip.
- **Instructions**:
  - Run the script: `python panning_training.py`
  - Load an audio file, then listen to the original and altered (panned) versions.
  - Use the panning slider to guess the panning position (-100% for full left, 0% for center, and +100% for full right).
  - Adjust the error margin using the spin box (default is 10%).
  - Each guess is evaluated, and the script selects a new clip with a random panning position.

### 3. Reverb Training (`reverb_training.py`)

- **Purpose**: Provides practice in identifying different reverb types, such as small room, large hall, and church reverbs.
- **Instructions**:
  - Run the script: `python reverb_training.py`
  - Load an audio file and select a reverb type from the dropdown menu.
  - Listen to the original and reverberated versions.
  - The script uses impulse responses (IRs) to apply reverb; ensure you have IR files named `small_room_ir.wav`, `large_hall_ir.wav`, and `church_ir.wav` in the same directory.

### 4. Impulse Response (IR) Generation (`ir_generation.py`) (tool for the Reverb Training)

- **Purpose**: Generates an IR file from a dry (unprocessed) and a wet (processed with reverb) version of the same audio file.
- **Instructions**:
  - Run the script: `python ir_generation.py`
  - Make sure you have both a dry (original) and wet (reverb-processed) version of the same audio file, aligned to avoid timing issues.
  - The script will create an IR by deconvolving the wet audio with the dry audio and save it as a `.wav` file.
  - Example usage:
    ```bash
    python ir_generation.py dry_audio.wav wet_audio_with_reverb.wav my_reverb_ir.wav
    ```

## Important Notes

- **Impulse Response Files (IRs)**: For `reverb_training.py` and `ir_generation.py`, you will need IR files or audio files that represent the specific reverbs you want to use.
  - Recommended sources for IRs include:
    - [OpenAirLib](https://www.openairlib.net/)
    - [EchoThief](https://echothief.com/)
    - [Samplicity's Bricasti M7 IRs](https://www.samplicity.com/bricasti-m7-impulse-responses/)

- **Audio File Compatibility**: Ensure all audio files are in `.wav` format and have compatible sample rates (e.g., 44100 Hz) for accurate playback and processing.

- **Error Margin Settings**: In `panning_training.py`, you can adjust the acceptable error margin for panning accuracy using the spin box control. 

## License

This repository is provided for educational purposes. Check individual IR sources for licensing restrictions.
```

Copy and paste this content into a file named `README.md`, and it will be ready for use. Let me know if you need further assistance.
