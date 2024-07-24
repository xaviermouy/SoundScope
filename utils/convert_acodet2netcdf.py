''' 
This script takes detection files from ACODET (Vincent's humpback detector) and converts them
to  nc files compatible with ecosound/SoundScope.

'''

from ecosound.core.annotation import Annotation
from ecosound.core.measurement import Measurement
from ecosound.core.tools import filename_to_datetime, list_files
import os
import pandas as pd
import uuid

## User inputs
detec_files_dir =r'.\PassiveAcoustics\DETECTOR_OUTPUT\PYTHON_HUMPBACK\Raw\NEFSC_GOM_202112_MONHEGAN\thresh_0.5\NEFSC_GOM_202112_MONHEGAN_ST\5418_48kHz_UTC' # location of the ACODET detection files
audio_files_dir =r'.\PassiveAcoustics\BOTTOM_MOUNTED\NEFSC_GOM\NEFSC_GOM_202112_MONHEGAN\NEFSC_GOM_202112_MONHEGAN_ST\5418_48kHz_UTC' # Location of the audio files associated with the detections
nc_files_out_dir = r'C:\Users\xavier.mouy\Desktop\test' # where the nc files will be created
audio_file_extension = '.wav' # extention of the audio files in audio_files_dir
audio_channel = 1 # channel of the audio file
class_label = 'HB' # detection label to use in SoundScope
detector_suffix='_annot_Humpback_20221130.txt' # suffic of teh ACODET detection files. This should be always stay the same (I think).

## script
detec_files = list_files(detec_files_dir, detector_suffix)
for detec_file in detec_files:

    # find name of audio file
    file_string = os.path.split(detec_file)[1]
    pos_detector_suffix = file_string.find(detector_suffix)
    audio_file_name = file_string[0:pos_detector_suffix]

    # load detection data
    file_data = Annotation._import_csv_files(detec_file)
    columns = file_data.columns.to_list()

    # create an empty ecosound Annotation object
    detec = Annotation()
    data = detec.data

    # fill in dataframe
    data.time_min_offset = file_data['Begin Time (s)']
    data.time_max_offset = file_data['End Time (s)']
    data.frequency_max = file_data['High Freq (Hz)']
    data.frequency_min = file_data['Low Freq (Hz)']
    data.confidence = file_data['Prediction/Comments']
    data.audio_file_name = audio_file_name
    data.audio_file_dir = audio_files_dir
    data.audio_file_extension = audio_file_extension
    file_timestamp = filename_to_datetime(audio_file_name + audio_file_extension)
    data.audio_file_start_date = file_timestamp[0]
    data.audio_channel = audio_channel
    data.time_min_date = pd.to_datetime(data["audio_file_start_date"] + pd.to_timedelta(data["time_min_offset"], unit="s"))
    data.time_max_date = pd.to_datetime(data["audio_file_start_date"] + pd.to_timedelta(data["time_max_offset"], unit="s"))
    data.label_class = class_label
    data.from_detector = True
    data.software_name = "ocodet"
    data.uuid = data.apply(lambda _: str(uuid.uuid4()), axis=1)
    data.duration = data["time_max_offset"] - data["time_min_offset"]
    data.audio_sampling_frequency = -1
    data.audio_bit_depth = -1

    # update data in the ecosound Annotation object and check for errors
    detec.data = data
    detec.check_integrity(verbose=True, ignore_frequency_duplicates=True)

    # save a nc file:
    detec.to_netcdf(os.path.join(nc_files_out_dir,audio_file_name+audio_file_extension+'.nc'))


