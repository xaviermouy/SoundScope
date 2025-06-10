import numpy as np
import panel as pn
import holoviews as hv
import datashader as ds
import holoviews.operation.datashader as hd
from holoviews.streams import RangeXY
import time
from ecosound.core.audiotools import Sound  # Ecosound Sound class object.
from ecosound.core.spectrogram import Spectrogram  # Ecosound Spectrogram class object.

hv.extension('bokeh')
pn.extension()

hv.extension('bokeh')
pn.extension()
wavfilename=r'F:\NEFSC_SBNMS_201811_SB03\671879182_48kHz\671879182.20181118040936.wav'
t1 = 1
t2 = 100
fmax = 4000
frame=0.1
window_type='hann'
nfft=0.1
step=0.05



# load audio data
start_time = time.perf_counter()  # start timer
sound = Sound(wavfilename)
selected_sound = sound
sound.read(
    channel= 0,
    chunk=[t1, t2],
    unit="sec",
    detrend=True,
)

# decimate audio data
new_fs = 2.5 * fmax
sound.decimate(new_fs)

# compute spectrogram
start_time = time.perf_counter()  # start timer
spectro = Spectrogram(
    frame,
    window_type,
    nfft,
    step,
    sound.waveform_sampling_frequency,
    unit="sec",
)
spectro.compute(sound, dB=True, use_dask=False, dask_chunks=40)
end_time = time.perf_counter()  # end timer
elapsed_time = end_time - start_time
print(f"Elapsed time compute spectro: {elapsed_time:.2f} seconds")


start_time = time.perf_counter()  # start timer
spectrogram = spectro.spectrogram
# Create coordinates
x = spectro.axis_times
y = spectro.axis_frequencies

# --- Create HoloViews image ---
base_image = hv.Image((x, y, spectrogram), ['time', 'frequency'], 'amplitude')

# --- Define interactive controls ---
min_slider = pn.widgets.FloatSlider(name="Min Amplitude", start=spectrogram.min(), end=spectrogram.max(), step=1, value=spectrogram.min())
max_slider = pn.widgets.FloatSlider(name="Max Amplitude", start=spectrogram.min(), end=spectrogram.max(), step=1, value=spectrogram.max())
gamma_slider = pn.widgets.FloatSlider(name="Gamma", start=0.1, end=5.0, step=0.1, value=1.0)

# --- Reactive function to update image based on controls ---
@pn.depends(min_slider, max_slider, gamma_slider)
def shaded_image(min_val, max_val, gamma):
    # Clip and normalize
    clipped = np.clip(spectrogram, min_val, max_val)
    normed = (clipped - min_val) / max((max_val - min_val), 1e-8)

    # Apply gamma correction
    gamma_corrected = normed ** gamma

    # Create new HoloViews image
    img = hv.Image((x, y, gamma_corrected), ['time', 'frequency'], 'amplitude')
    return hd.datashade(img, cmap='viridis', dynamic=True).opts(height=400, width=800)

# --- Layout ---
layout = pn.Column(
    #"# Live Spectrogram with Contrast and Gamma Correction",
    pn.Row(min_slider, max_slider, gamma_slider),
    shaded_image
)

layout.servable()

layout.show(port=5006, threaded=True, websocket_origin="localhost:5006")
