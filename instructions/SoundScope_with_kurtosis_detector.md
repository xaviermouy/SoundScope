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
- nc_file_out_name: name of the nectCDF file that will be created. It shoudl end with .nc
- audio_file_extension: extension of teh audio files (typically '.wav'). 

Make sure to have all paths between quortes and preceded by the letter "r" (as shown in section 2. above).

4. Run the script:
- Open terminal in the python environment created above
- run the script:
```
python convert_KurtosisDetector2netcdf.py
```
Note that you might have to add teh path to the script if it is not located in the current directory. The script should create a .nc file with teh name and path that were indicated in the script.


## Load detections in SoundScope
- Open SoundScope
- Load the nc file created in the step above (menu: file > Open File)

if the path of the sound files have chanegd since you created the nc file, update the path in SoundScope using the menu Edit > Change Audio Path.




