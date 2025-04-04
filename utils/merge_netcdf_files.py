''' 
This script takes all the netCDF files for a deployment and merges them into 
a single master netCDF file that can be used with SoundScope. If audio files
have moved since the detector was run, the middle part of teh script can be
uncommented to also update the audio files path (if the audio_file_dir in the
netCDF file is not valid, SoundScope will not be able to display spectrogram
of the selected detetions).

'''

from ecosound.core.annotation import Annotation
from ecosound.core.measurement import Measurement
import os



# Load all netCDF files
detec_files_dir =r'C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\processing_outputs\WHOI_Galapagos_202305_Caseta\6478\fishsoundfinder'
print('Loading all .nc files in detec_files_dir')
detec = Annotation()
detec.from_netcdf(detec_files_dir, verbose=True)
print(detec.summary())

# # update audio files path:
# audio_files_dir =r'D:\2023_CoralCityCamera\ST43000-67649538'
# print('Updating path of the audio files')
# detec.update_audio_dir(audio_files_dir)

# save master nc file:
print('Saving merged detections to the file detections_dataset.nc')
detec.to_netcdf(os.path.join(detec_files_dir,'detections_dataset.nc'))

print('s')