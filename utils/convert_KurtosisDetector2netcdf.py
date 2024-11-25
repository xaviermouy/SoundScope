'''
This script takes detection files from the kurtosis detector and converts them
to  nc files compatible with ecosound/SoundScope.

'''

from ecosound.core.annotation import Annotation
from ecosound.core.measurement import Measurement
from ecosound.core.tools import filename_to_datetime, list_files
import os
import pandas as pd
import uuid

## User inputs
detec_files_dir =r'C:\Users\xavier.mouy\Documents\Projects\2024_NERACOOS_Soundscape_GOM\Analysis\data\KurtosisDetector\NEFSC_SBNMS_201910_SB03' # location of the detection files
audio_files_dir =r'F:\NEFSC_SBNMS_201910_SB03\1678008346_48kHz' # Location of the audio files associated with the detections
nc_file_out_dir = r'C:\Users\xavier.mouy\Documents\Projects\2024_NERACOOS_Soundscape_GOM\Analysis\data\KurtosisDetector\NEFSC_SBNMS_201910_SB03' # where the nc files will be created
nc_file_out_name = 'NEFSC_SBNMS_201910_SB03_Kurtosis.nc'
audio_file_extension = '.wav' # extention of the audio files in audio_files_dir

## script

# import detection results
print('Loading detections')
detec = Annotation()
detec.from_raven(detec_files_dir, confidence_header='Kurtosis', recursive=True)

# fill in dataframe
detec.insert_values(
    audio_sampling_frequency=0,
    audio_bit_depth=0,
    UTC_offset=0,
    from_detector=True,
    software_name="Kurtosis-detector",
)

# scale kurtosis values / used as confidence
detec.data.confidence = detec.data.confidence / 100

# update audio files path
print('Updating audio files paths')
detec.update_audio_dir(audio_files_dir)

# check integrity
detec.check_integrity(verbose=True, ignore_frequency_duplicates=True)

# save a nc file:
detec.to_netcdf(os.path.join(nc_file_out_dir, nc_file_out_name))

print('Done')