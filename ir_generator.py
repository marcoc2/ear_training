import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve

def generate_ir(dry_file, wet_file, output_ir_file):
    """
    Generate an impulse response (IR) from a dry (unprocessed) audio file and a wet (processed with reverb) audio file.
    
    Parameters:
    dry_file (str): Path to the dry (unprocessed) audio file.
    wet_file (str): Path to the wet (processed with reverb) audio file.
    output_ir_file (str): Path to save the generated IR file.
    
    Usage:
    ------
    To create a high-quality IR, ensure the following:
    - Both dry and wet audio files should have the same length and be well-aligned. Any mismatch or latency may affect the IR quality.
    - This method works best with stationary, linear reverbs. It may not capture time-varying reverbs (e.g., tape or modulated reverbs) accurately.
    - For capturing real room reverbs (like halls or churches), consider recording with a direct signal (e.g., using a "click" or frequency sweep) for best results.
    
    Output:
    - The IR is saved as a normalized .wav file at the specified location.
    """
    
    # Load dry (unprocessed) and wet (with reverb) audio
    dry_audio, sample_rate = sf.read(dry_file)
    wet_audio, _ = sf.read(wet_file)
    
    # Ensure both signals have the same length
    min_len = min(len(dry_audio), len(wet_audio))
    dry_audio = dry_audio[:min_len]
    wet_audio = wet_audio[:min_len]

    # Calculate the Impulse Response (IR) using deconvolution in the frequency domain
    dry_audio_fft = np.fft.fft(dry_audio)
    wet_audio_fft = np.fft.fft(wet_audio)
    
    # Avoid division by zero (adding a small constant)
    epsilon = 1e-10
    ir_fft = wet_audio_fft / (dry_audio_fft + epsilon)
    
    # Convert back to the time domain to get the IR
    impulse_response = np.fft.ifft(ir_fft).real

    # Normalize the IR to avoid clipping
    impulse_response /= np.max(np.abs(impulse_response))

    # Save the resulting IR
    sf.write(output_ir_file, impulse_response, sample_rate)
    print(f"IR saved to {output_ir_file}")

# Example usage
generate_ir("dry_audio.wav", "wet_audio_with_reverb.wav", "my_reverb_ir.wav")

