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
detec_files_dir =r'C:\Users\xavier.mouy\Desktop\test_kurtosis_merge' # location of the detection files
audio_files_dir =r'F:\NEFSC_SBNMS_201910_SB03\1678008346_48kHz' # Location of the audio files associated with the detections
nc_file_out_dir = r'C:\Users\xavier.mouy\Desktop\test_kurtosis_merge' # where the nc files will be created
nc_file_out_name = 'TEST_merged.nc' # name of the nc file taht will be created
audio_file_extension = '.wav' # extention of the audio files in audio_files_dir
merge_time_tolerance_sec = 1 # if >0 merges together detections that are separated in time by lees than merge_time_tolerance_sec (value in seconds)
min_merged_detections_number = 3

## script

# import detection results
print('Loading detections')
detec = Annotation()
detec.from_raven(detec_files_dir, confidence_header='Kurtosis', recursive=True, verbose=True)

# fill in dataframe
detec.insert_values(
    audio_sampling_frequency=0,
    audio_bit_depth=0,
    UTC_offset=0,
    from_detector=True,
    software_name="Kurtosis-detector",
)

# merge consecutive detections
if merge_time_tolerance_sec > 0:
    print('Merging detections')
    n_detec, detec = detec.merge_overlapped(time_tolerance_sec=merge_time_tolerance_sec, confidence_agg='max', min_merged_detections= min_merged_detections_number, inplace=False)
    print('Annotations after merging: ', len(detec))

# scale kurtosis values / used as confidence
detec.data.confidence = detec.data.confidence / 100 # Normalize the kurtosis values from 0 to 1 so it can be sorted in SoundScope => not sure this is the best way to proceed here...

# update audio files path
print('Updating audio files paths')
#detec.update_audio_dir(audio_files_dir)

# check integrity
detec.check_integrity(verbose=True, ignore_frequency_duplicates=True)

# save a nc file:
detec.to_netcdf(os.path.join(nc_file_out_dir, nc_file_out_name))

print('Done')