# Kurtosis detector

The kurtosis detector is a generic detector that detects impulsive signals in a given frequency band. It is used for example to detect haddock sounds, humpback whale negaptclicks and pile driving sounds.The detector saves resulst as Raven tables. These instructions show how to convert these detection results into a format that SoundScope can use.

## Setting up the python environment
1. Create a python environment with python 3.10 (e.g. using Anaconda)
2. install the library ecosound
```
pip install ecosound
```

## Convert Raven tables to ecosound NetCDF files
The kurtosis detections are saved a Raven tables. So the outputs nee to be converted to the netCDF fiel format (.nc) that ecosound and SoundScope use. 

1. Download the convertion script from the SoundScope github page here (under the "utils" directory): [convert_KurtosisDetector2netcdf.py](https://github.com/xaviermouy/SoundScope/blob/main/utils/convert_KurtosisDetector2netcdf.py) 
2. Edit the first few lines under the "user inputs" section
```python
## User inputs
detec_files_dir =r'C:\Users\xavier.mouy\Documents\Projects\2024_NERACOOS_Soundscape_GOM\Analysis\data\KurtosisDetector\NEFSC_SBNMS_201910_SB03' # location of the detection files
audio_files_dir =r'F:\NEFSC_SBNMS_201910_SB03\1678008346_48kHz' # Location of the audio files associated with the detections
nc_file_out_dir = r'C:\Users\xavier.mouy\Documents\Projects\2024_NERACOOS_Soundscape_GOM\Analysis\data\KurtosisDetector\NEFSC_SBNMS_201910_SB03' # where the nc files will be created
nc_file_out_name = 'NEFSC_SBNMS_201910_SB03_Kurtosis.nc'
audio_file_extension = '.wav' # extention of the audio files in audio_files_dir
```
3. Update the following variables with the appropraiet information:
- detec_files_dir: Path of the folder where the detections from the kurtosis detector are (i.e. Raven tabel files - .txt)
- audio_files_dir: Path of the folder where the audio files associated with the detctions are
- nc_file_out_dir: Path of the folder where the SoundScope compatible netCDF file with the detections



## Load detections in SoundScope

