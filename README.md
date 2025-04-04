<p align="center">
	<img src="/images/SoundScopeWelcome.png" width="300" />
</p>

# What is SoundScope ?
SoundScope is a python-based software that facilitates the visualization and manual verification of detections from automatic whale and fish sound detectors (or any other sound detectors). 
It allows to display and navigate through detections time series, filter and sort by classification confidence, and dynamically produce spectrograms of the detections. SoundScope was initially
created in the [Juanes Lab](https://juaneslab.weebly.com/) at the University of Victoria and is currently being developped at the [Passive Acoustic Branch of NOAA's Northeast Fisheries Science Center](https://www.fisheries.noaa.gov/new-england-mid-atlantic/endangered-species-conservation/passive-acoustic-research-northeast#:~:text=We%20use%20passive%20acoustic%20technologies,affected%20by%20human%2Dmade%20sounds). 

SoundScope is still under heavy development. Please don't hesitate to reach out if you want to use it or want to help with the development. 

[![Youtube link](https://img.youtube.com/vi/80ZeSBCuZ4U/0.jpg)](https://www.youtube.com/watch?v=80ZeSBCuZ4U)

# How to use it ?

There are 2 ways to use SoundScope:

### Download the latest binary 
This is the easiest way as it does not require to install anything. The binaries are uploaded in this Google folder: [SoundScope binaries](https://whoi-my.sharepoint.com/:f:/g/personal/xavier_mouy_whoi_edu/EtRGhOyVbSJMiLBs0DetDyEBRdaVMQP_BdA4Yoeb_if65w?e=WdTdzE)
Download the latest zip file, unzip it, and double click on soundscope.exe to launch the application.

### Clone the Github repository
This is more involved as it requires to install python and required python libraries. For instructions see the "Development notes" section below. 

# Input data format:
Currently, SoundScope uses netCDF files as input. The data format in the ndtCDF files follows the structure of the [Annotation](https://github.com/xaviermouy/ecosound/blob/master/ecosound/core/annotation.py) and [Measurement](https://github.com/xaviermouy/ecosound/blob/master/ecosound/core/measurement.py) objects defined by the [ecosound](https://github.com/xaviermouy/ecosound) library. 
More documentation describing how to create these netCDF files will be added in the near future. In the meantime, you can have a look at the script [convert_acodet2netcdf.py](https://github.com/xaviermouy/SoundScope/blob/main/utils/convert_acodet2netcdf.py) in the "utils" folder which converts outputs from the [ACODET detector](https://github.com/vskode/acodet) to the SoundScope format.

An example of netCDF file can be found in the folder [here](https://drive.google.com/drive/folders/1UCbsveXWZnqgaYKTtJ3XdINJCT15SGun?usp=drive_link). 
You can open it directly in SoundScope. Note that it will allow you to play around with the detection plots, but will not be able to display the spectrogram of selected detections because it won't have access to the original audio data.

To examine the structure of the netCDF file you can open it in python with ecosound:

```python
from ecosound.core.annotation import Annotation

annot = Annotation()
annot.from_netcdf(r'.\SoundScope_data_examples\SoundScape_detections_example.nc')

# all the detection data and metadate are in the pandas dataframe in annot.data
print(annot.data)

``` 
The code above requires to have ecosound installed. To install ecosound use the command: **pip install ecosound**

# Found a bug or want new features?

### Bugs:
If you found a bug please add an entry to the [issues list](https://github.com/xaviermouy/SoundScope/issues) with the label "**bug**". Please include as much information as possible.

### New features:
If you want new functionalities to be added to SoundScope, add an entry to the [issues list](https://github.com/xaviermouy/SoundScope/issues) with the label "**enhancement**". Use the
thumbs-up emoji (👍) to boost the priority of a new features.

# Versions

### version 20250404
- Enforced including files extensions when saving csv or wav files
- Dates and times in the exported csv now follwoing ISO 8601 standard with time zone designator.

### version 20250122
- Improved loading time for spectrograms
- Added loading spinner for the spectrogram calculation
- Added breakdown of spectrogram creation/loading times in the command window to help identify possible bottlenecks.

### version 20241202
- Added capability to download daily and hourly detection summary as csv file (issue #14)
- Added capability to download audio clip of the selected detection
- Fixed bug where the first detection clicked in the table returned an error
- Showing time zone of the analysis in the main interface (top right)
- Added error notifications in main interface to help the user identify issues

### version 20241107
- Upgraded to python 3.10
- Upgraded to panel 1.5.3
- Fixed instabilities with selections the calendar plots
- Increased maximum allowed time offset in spectrogram to 500 seconds
- Added time zone support

### version 20241107
- Initial release


# Development notes

## Python version:
python 3.10

## Build development environment with requirements.txt:

    $ pip install -r requirements.txt

## Run SoundScope

- Run soundscope:

    $ panel serve soundscope.py --show --autoreload

- or just..

    $ python soundscope.py

## Create a binary file (.exe)

- Make sure to work with the binary branch which contains extra code to optimize the binaries.

1.) Install pyinstaller:

    $ pip install pyinstaller

2.) Compile code in Windows: 

In a terminal change to current directory to the sounscope folder using the cd command. Then type

   $ pyinstaller -i images\SoundScopeLogo.png --collect-all holoviews --collect-all distributed --collect-all param --hidden-import matplotlib.backends.backend_agg .\soundscope.py

or 

   $ pyinstaller .\soundscope.spec

3.) Copy over the images directory to the dist folder.

    $ mv images dist/images