import numpy as np
import scipy.signal
import cv2
import time
from scipy.signal import square, ShortTimeFFT
from scipy.signal.windows import hann
import numpy as np

import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import gaussian
def spectro2(infile):
    frame = 1024
    step = 512
    # Read the WAV file
    fs, sig = wavfile.read(infile)

    # Initialize ShortTimeFFT with desired parameters
    window = hann(frame)
    SFT = ShortTimeFFT(fs=fs, win=window, mfft=frame, hop=step,fft_mode='onesided', scale_to='psd')
    # Compute the STFT
    Sx = SFT.stft(sig)  #

    fig1, ax1 = plt.subplots(figsize=(6., 4.))  # enlarge plot a bit
    #t_lo, t_hi = SFT.extent(N)[:2]  # time range of plot
    im1 = ax1.imshow(abs(Sx), origin='lower', aspect='auto', cmap='viridis')
    #ax1.plot(t_x, f_i, 'r--', alpha=.5, label='$f_i(t)$')
    plt.show()
    # # Plot the spectrogram
    # plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [sec]')
    # plt.title('Spectrogram')
    # plt.colorbar(label='Magnitude')
    # plt.show()

def fast_spectrogram(audio_file, output_file="spectrogram.png"):
    from scipy.io import wavfile

    # Load audio
    sr, y = wavfile.read(audio_file)
    if y.ndim > 1:  # Convert stereo to mono if needed
        y = np.mean(y, axis=1)

        # Compute spectrogram using ShortTimeFFT (Modern & Faster)
        stft = scipy.signal.ShortTimeFFT(nperseg=1024)
        freqs, times, Sxx = stft.compute(y, fs=sr)

        # Convert magnitude to log scale for better visualization
        Sxx = np.log1p(np.abs(Sxx))

        # Normalize for image saving
        Sxx = (255 * (Sxx - np.min(Sxx)) / (np.max(Sxx) - np.min(Sxx))).astype(np.uint8)

        # Save as PNG using OpenCV (Fast!)
        cv2.imwrite(output_file, Sxx)

infile = r"C:\Users\xavier.mouy\Documents\GitHub\SoundScope\test_data\200_sec.wav"

start_time = time.perf_counter()

#fast_spectrogram(infile)
spectro2(infile)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time create spectro plot: {elapsed_time:.2f} seconds")