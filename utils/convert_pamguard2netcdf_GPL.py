# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 21:43:55 2022

@author: xavier.mouy
"""

from ecosound.core.tools import list_files, filename_to_datetime
from ecosound.core.measurement import Measurement
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import uuid
import os
from time import process_time

out_dir = r"C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\annotated"
in_dir = r"C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\annotated"
file_name = "GPL_detections" # don't include the ".sqlite3"
data_folder = r"C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\annotated"
deployment_file = r"C:\Users\xavier.mouy\Documents\GitHub\SoundScope\tmp\deployment_info.csv"

audio_files_ext = ".wav"
sql_table_name = "Generalised_Power_Law_Detector_Detections" #"Dolphin_WMD"
class_name = "GPL"
time_offset = 0


## ############################################################################

start_time = process_time()

partial_sql_load = None  # 1000

# list audio files
files_list = list_files(data_folder, audio_files_ext)
files_list.sort()
files_dates = filename_to_datetime(files_list)

# import sql file from pamguard
conn = sqlite3.connect(os.path.join(in_dir, file_name + ".sqlite3"))
sql_table = pd.read_sql_query(
    "SELECT * FROM " + sql_table_name,
    conn,
)
conn.close()
if partial_sql_load:
    print("Warning! Not all detetions are loaded.")
    sql_table = sql_table.iloc[0:partial_sql_load]


# init annotation obj
annot = Measurement(
    measurer_name="PAMGuard",
    measurer_version="1.0",
    measurements_name=["frequency_bandwidth", "amplitude"],
)

# assign UUIDs
uuids = [0] * len(sql_table)
uuids = [str(uuid.uuid4()) for i in uuids]
annot.data["uuid"] = uuids

time_min_offset = [None] * len(sql_table)
time_max_offset = [None] * len(sql_table)
audio_file_dir = [None] * len(sql_table)
audio_file_name = [None] * len(sql_table)
audio_file_extension = [None] * len(sql_table)
audio_file_start_date = [None] * len(sql_table)
time_min_date = [None] * len(sql_table)
time_max_date = [None] * len(sql_table)
labels = [None] * len(sql_table)

# calculate fs based on detection in middle of table (to avoid  detections at t=0)
tmp_detec = sql_table.iloc[round(len(sql_table)/2)]
fs = tmp_detec["startSample"] / tmp_detec["startSeconds"]

# go through each detections in the table
for idx, detec in sql_table.iterrows():

    # find associated audio file:
    detec_time = datetime.strptime(detec.UTC, "%Y-%m-%d %H:%M:%S.%f")
    time_diff = [detec_time - filedate for filedate in files_dates]
    time_diff = [
        np.nan if i.total_seconds() < 0 else i.total_seconds()
        for i in time_diff
    ]
    file_index = time_diff.index(min(time_diff))
    # calculate detections times, dates, and paths
    try:
        labels[idx]=class_name +'_'+ str(detec["SpeciesCode"])
    except:
        labels[idx] = class_name

    filename = files_list[file_index]
    time_min_offset[idx] = detec["startSeconds"]
    time_max_offset[idx] = time_min_offset[idx] + (detec["duration"] / fs)
    audio_file_dir[idx] = os.path.dirname(filename)
    audio_file_name[idx] = os.path.splitext(os.path.basename(filename))[0]
    audio_file_extension[idx] = os.path.splitext(filename)[1]
    audio_file_start_date[idx] = files_dates[file_index]
    time_min_date[idx] = audio_file_start_date[idx] + pd.to_timedelta(
        time_min_offset[idx], unit="s"
    )
    time_max_date[idx] = audio_file_start_date[idx] + pd.to_timedelta(
        time_max_offset[idx], unit="s"
    )

annot.data["time_min_offset"] = time_min_offset
annot.data["time_max_offset"] = time_max_offset
annot.data["audio_file_dir"] = audio_file_dir
annot.data["audio_file_name"] = audio_file_name
annot.data["audio_file_extension"] = audio_file_extension
annot.data["audio_file_start_date"] = audio_file_start_date
annot.data["time_min_date"] = time_min_date
annot.data["time_max_date"] = time_max_date
annot.data['label_class'] = labels

annot.data["duration"] = (
    annot.data["time_max_offset"] - annot.data["time_min_offset"]
)
annot.insert_values(from_detector=True)
annot.insert_values(audio_sampling_frequency=fs)
#annot.insert_values(label_class=class_name)
annot.insert_values(operator_name="unknown")
annot.insert_values(UTC_offset=0)
annot.insert_values(confidence=1)
annot.insert_values(software_name= sql_table_name)
annot.insert_values(audio_channel=1)
pc_time = [
    datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f") for i in sql_table["PCTime"]
]
annot.data["entry_date"] = pc_time
annot.data["frequency_min"] = sql_table["lowFreq"]
annot.data["frequency_max"] = sql_table["highFreq"]
annot.data["frequency_bandwidth"] = (
    annot.data["frequency_max"] - annot.data["frequency_min"]
)
annot.data["amplitude"] = sql_table["amplitude"]

annot.insert_metadata(deployment_file)
annot.check_integrity()

# Apply time offset
annot.data["time_min_date"] = annot.data["time_min_date"] + timedelta(
    hours=time_offset
)

annot.data["time_max_date"] = annot.data["time_max_date"] + timedelta(
    hours=time_offset
)

annot.insert_values(UTC_offset=-5)

# Save
annot.to_netcdf(os.path.join(out_dir, file_name + "_ecosound_est"))
# annot.to_sqlite(os.path.join(out_dir, "PAMGuard_detections_est"))

end_time = process_time()
print("Elapsed time in seconds:", end_time - start_time)
