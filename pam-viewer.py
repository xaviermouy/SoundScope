#!/usr/bin/python3
# coding: utf-8

# Libraries

import os  # For dealiing with paths and directories mostly.
import panel as pn # Flask like framework with a great library for modular installation of graphical components.
import copy # For use of deep copying. We use it in the creation of active data so that we will unhinder the original object's memory.

from ecosound.core.tools import filename_to_datetime # Ecosound filename to datetime function.
from ecosound.core.measurement import Measurement # Ecosound Measurement class object. Special case of Annotation.
from ecosound.core.annotation import Annotation # Ecosound Annotation class object.
from ecosound.core.audiotools import Sound # Ecosound Sound class object.
from ecosound.core.spectrogram import Spectrogram # Ecosound Spectrogram class object.
from ecosound.visualization.grapher_builder import GrapherFactory # Ecosound GrapherFactory class object.

from dask.distributed import Client # Dask distributed client for parallel computing.

import numpy as np # Numpy library for numerical manipulation in python3.
import pandas as pd # Pandas library for dataframe objects.
import datetime # Datetime library for datetime objects.
import holoviews as hv # Holoviews library for interactive plotting.
import hvplot.pandas # Holoviews plotting library for pandas objects.

import tkinter as tk
import tkinter.filedialog as file_chooser_dialog

from bokeh.models.formatters import DatetimeTickFormatter # Bokeh datetime formatter for plotting.
from matplotlib.cm import Reds, Blues, Greens, viridis, hsv, binary, hot # Matplotlib colormaps.

import matplotlib.pyplot as plt # Matplotlib plot object for plotting.
from playsound import playsound

from matplotlib.figure import Figure
from matplotlib import cm

import warnings # Warnings library for displaying warnings.
from loguru import logger # A great logger option.
import datetime
import aifc
import sounddevice as sd

# Configurations

warnings.filterwarnings('always') # Warning configuration.
np.random.seed(7)
#pn.extension('tabulator', 'terminal','ipywidgets', sizing_mode = 'stretch_width', loading_spinner = 'dots', notifications = True) # Panel extension configuration.
#pn.extension('tabulator', 'terminal', sizing_mode = 'stretch_width', loading_spinner = 'dots', notifications = True) # Panel extension configuration.
pn.extension('tabulator',  sizing_mode = 'stretch_width', loading_spinner = 'dots', notifications = True) # Panel extension configuration.

pn.config.throttled = True # Update only when mouse click release.
pn.extension(loading_spinner='dots', loading_color='lightblue') # Loading spinner, loading_color='#00aa41' .
pn.param.ParamMethod.loading_indicator = True # Indicate to user when a loading session is done.
#pn.extension('ipywidgets')
pn.extension()
# Global variables 

global data_file_name   # path of NetCDF file
data_file_name = ""
global dataset                  # detection/annotation ecosound object from netcdf file
global active_data              # detection/annotation ecosound object displayed (i.e. filtered)
global aggregate_1D             # pandas dataframe with 1D aggregate of detections/annotations
global aggregate_2D             # pandas dataframe with 2D aggregate of detections/annotations
global plot_2D                  # holoviews object with 2D plot
global graph_selection_start    
global graph_selection_end      
global selection_interval
global selected_day
global initial_datetime
global final_datetime
global datetime_range_picker
global dataframe_explorer_widget
global dataframe_explorer_widget_locked
global spectrogram_plot_pane
global spectrogram_metadata_explorer
global selected_sound
global color_map_widget_spectrogram


logger.debug("Initializing variables..") # Log initialization of variables.

# Initialize variables / Parameters.

dataset = None # Initialize dataset object to None.
active_data = Annotation() # Initialize active_data object to Annotation object.
d = pd.DataFrame(0, index=[0], columns=active_data.data) # Initialize pandas dataframe object to 0.
active_data.data = pd.concat([active_data.data,d]) # Concatenate active_data object with pandas dataframe object. TODO: Get more context.

selection_interval = ( None, None)
initial_datetime = ""
final_datetime = ""

# Time aggregate values: mapping of text displayed in widget -> str used by pandas
time_aggregate_mapping_2D = {
#    '5 minutes':  '5Min',
#    '15 minutes': '15Min',
#    '30 minutes': '30Min',
    '1 hour':  '1H',
#    '2 hours': '2H',
#    '3 hours': '3H',
#    '4 hours': '4H',
#    '5 hours': '5H',
#    '6 hours': '6H',
#    '12 hours':'12H',
}

# Colormaps for 2D plot
cmaps_plot2D = { 'viridis': viridis, 'hot': hot, 'binary': binary, 'hsv': hsv, 'Reds': Reds, 'Blues': Blues, 'Greens': Greens }

# init Aggregate_1D
date_today = datetime.date.today()
days = pd.date_range(date_today, date_today + datetime.timedelta(7), freq='D')
data = np.zeros(len(days))
aggregate_1D = pd.DataFrame({'datetime': days, 'value': data})
aggregate_1D = aggregate_1D.set_index('datetime')


# init Aggregate_2D
#aggregate_2D = pd.DataFrame({'date1':np.zeros(24),'date2':np.zeros(24),'date3':np.zeros(24)})
aggregate_2D = pd.DataFrame(columns= days, index=range(0,24)) # 
aggregate_2D = aggregate_2D.fillna(0) # Fill NaN values with 0 for the aggregate_2D object.


# Widgets 
audio_files_multi_select = pn.widgets.MultiSelect(name='Audio files', value= [], options=[], size=8) # Audio files widget object from python3 panel library. This object is a container for audio files. Ref : https://panel.holoviz.org/reference/widgets/MultiSelect.html

# Confidence threshold slider
threshold_widget = pn.widgets.DiscreteSlider(name='Confidence threshold', options=list(np.arange(0,1.01,0.01)), value=0.5) # Slider widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/widgets/DiscreteSlider.html

# Sound class to display
class_label_widget = pn.widgets.Select(name='Class label', options=[]) # Select widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/widgets/Select.html

# Integration time
#integration_time_widget = pn.widgets.Select(name='Integration time', options=list(time_aggregate_mapping_2D.keys()),height=70, sizing_mode='stretch_width')
integration_time_widget = pn.widgets.Select(name='Integration time', options=list(time_aggregate_mapping_2D.keys()),height=70, width=200, margin = (10,10,10,10))
integration_time_widget.value = integration_time_widget.options[0]

# colormap selectro for 2D plot
color_map_widget_plot2D = pn.widgets.ColorMap(name='Colormap', options = cmaps_plot2D, ncols=1, height=70, width = 250, margin = (10,10,10,60))
color_map_widget_spectrogram = pn.widgets.ColorMap(options = cmaps_plot2D, ncols=1, height=50, width = 200, margin = (30,10,10,10))

file_selector = pn.widgets.FileSelector("~")
file_input = pn.widgets.FileInput(accept=".nc")

# Stream

lineplot_tap = hv.streams.Tap (x = 0, y = 0 )
heatmap_tap = hv.streams.Tap( x = 0, y = 0 ) # Declare Tap stream with heatmap as source and initial values.
histogram_tap = hv.streams.Tap( x = 0, y = 0 ) # Declare Tap stream with histogram as source and initial values.


detec_files_multi_select = pn.widgets.MultiSelect(name='Detections', value= [], options=[], size=8)
#sound_checkbox = pn.widgets.Checkbox(name='Automatically play selected sound', value=False)
file_name_markdown = pn.pane.Markdown("", width=100)


dataframe_explorer_widget = pn.widgets.Tabulator( name = 'Detection Dataframe Window', value = active_data.data, height = 655, disabled = True, selection = [0], pagination = 'remote' )
spectrogram_plot_pane = pn.pane.Matplotlib( name = 'Spectrogram', fixed_aspect = False, height = 565 )
spectrogram_metadata_explorer =  pn.widgets.Tabulator( name = 'Metadata', sizing_mode = 'stretch_width', height = 656, disabled = True, selection = [0], pagination = 'remote', show_index = False)


datetime_range_picker = pn.widgets.DatetimeRangePicker( name='Datetime Range Selection', sizing_mode='stretch_width')
dataframe_explorer_widget_locked = True


def load_dataset(data_file):
    """performs necessary actions to get widgets loaded and variables updated once the .nc file is selected.

    Args:
        data_file (str): A file with a .nc extension strictly speaking however the contents of the .nc will ultimately decide if it is compatible. Certain tables will be expected.

    Raises:
        e: If the contents are not expected some exceptions will be raised since the .nc file extension is not enough to fully vet the import. This function handles this.
    """      
    logger.debug( "Loading .nc file dataset." )  
    global dataset # Globally declares dataset object.
    try:
        
        dataset = Measurement() # Attempt at assigning a Measurement interface (Special case of Annotation object).
        dataset.from_netcdf(data_file)
        success_notification("Dataset successfully loaded!")
        update_class_label_widget()

    except:
        
        try:
            dataset = Annotation() # Attempt at assigning a Annotation (more general purpose) interface.
            dataset.from_netcdf(data_file)  

            success_notification("Dataset successfully loaded!")
            update_class_label_widget()


        except Exception as e:
        
            error_notification("Dataset failed to load!")
            raise e


# Display error notifications
def error_notification(msg_str):
    """Error message implemented as a log and a notification.

    Args:
        msg_str (str): Message to be displayed.
    """    
    logger.warning("Error loading .nc file!") 
    pn.state.notifications.position = 'top-right'
    pn.state.notifications.error(msg_str, duration=3000)  
    


# Display success notifications
def success_notification(msg_str):
    """Success message implemented as a log and a notification.

    Args:
        msg_str (str): Message to be displayed.
    """    
    pn.state.notifications.position = 'top-right'
    pn.state.notifications.success(msg_str, duration=3000)  

def update_datetime_range_picker_widget():
    global datetime_range_picker
    datetime_range_picker.value


# populate/update class label widget
def update_class_label_widget():
    """Updates the class label widget with the labels from the dataset object.
    """    
    logger.info("Updating class label widget")   
    class_label_widget.options = dataset.get_labels_class() 
    class_label_widget.value = class_label_widget.options[0]


# calculate 2D aggregate of detections/annotations
def calculate_2D_aggregates(active_data, agg_interval):
    """This function calculates the 2D aggregate of detections/annotations.

    Args:
        active_data (pd.DataFrame): The active_data object is the filtered dataset.
        agg_interval (_type_): The time interval for the aggregate.
    """
    logger.info("Calculating 2D aggregates..")       
    if dataset is not None:
       global aggregate_2D
       aggregate_2D = active_data.calc_time_aggregate_2D(integration_time = agg_interval)
       aggregate_2D.index = [x.hour for x in aggregate_2D.index]


# calculate 1D aggregate of detections/annotations
def calculate_1D_aggregates(active_data):
    """This function calculates the 1D aggregate of detections/annotations.

    Args:
        active_data (Annotation): The active_data object is the filtered dataset.
    """    
    logger.info("Calculating 1D aggregates..")         
    if dataset is not None:
       global aggregate_1D   
       aggregate_1D = active_data.calc_time_aggregate_1D(integration_time = '1D')



def update_active_data(widget_name):
    """Updates the active_data object with the settings from the widgets.

    Args:
        widget_name (str): A name which the function will use to specify which widget is being updated.
    """
    
    logger.debug("Updating active data. Invoked through the " + widget_name.strip() + " widget.") # Log event of updating active data.
    
    global active_data
    global data_file_name
    global selection_interval
    global initial_datetime
    global final_datetime

    if len(list(data_file_name)) > 0:
        
        logger.debug("Updating active data object..")

        # load widget settings
        conf_threshold = threshold_widget.value
        agg_interval = time_aggregate_mapping_2D[integration_time_widget.value]
        class_label = class_label_widget.value

        # Copy dataset to active data
        
        active_data = copy.deepcopy( dataset )
        
        # Filter
        
        active_data.filter('confidence>='+str(conf_threshold), inplace=True) # Results are greater than or equal to.
        active_data.filter('label_class=="'+class_label+'"', inplace=True) # It seems to select something by default.
        
        # create data aggregates
        # calculate_1D_aggregates( active_data )
        # calculate_2D_aggregates( active_data, agg_interval)
        
        # notification
        success_notification("New settings have been successfully applied to the "+widget_name.strip()+"!")
    
    

@pn.depends(class_label_widget, threshold_widget)
def create_1D_plot(class_label_widget, threshold_widget):
    """Creates a 1D plot object with the active_data object and depends on the class_label_widget and threshold_widget.

    Args:
        class_label_widget (str): _description_
        threshold_widget (float): 

    Returns:
        pd.DataFrame: A pandas dataframe object.
    """    
    logger.info("Creating 1D plot object..")    
    
    global aggregate_1D
    global data_file_name
    global active_data
    
    
    if len(list(data_file_name)) > 0:
        
        update_active_data("1D plot")
            
        calculate_1D_aggregates( active_data )
        
        dateformatter = DatetimeTickFormatter(days='%d %B %Y')
        bin_count = int(str(active_data.data['date'].max() - active_data.data['date'].min()).split(" ")[0])
        plot = pd.DataFrame(active_data.data).hvplot.hist('date', hover_color = "pink", nonselection_color = "light_blue", selection_color = "red", height=580, bin_range=(pd.Timestamp(active_data.data['date'].min()), pd.Timestamp(active_data.data['date'].max())),  bins = bin_count ) # This is where the histogram is created.
        lineplot_tap.source = plot 
        return plot

        
@pn.depends(class_label_widget, threshold_widget, color_map_widget_plot2D)
def create_2D_plot(class_label_widget, threshold_widget, color_map_widget_plot2D):
    """Creates a 2D plot object with the active_data object and depends on the class_label_widget and threshold_widget.

    Args:
        class_label_widget (pn.WidgetBox): A widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html
        threshold_widget (pn.WidgetBox): A slider widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/widgets/DiscreteSlider.html
        color_map_widget_plot2D (pn.widgets.ColorMap): A color map widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/widgets/ColorMap.html

    Returns:
        _type_: _description_
    """    
    global data_file_name
    
    if len(list(data_file_name)) > 0:
        
        logger.info("Creating 2D plot object..")
    
        global aggregate_2D

        agg_interval = time_aggregate_mapping_2D[integration_time_widget.value]

        try:
            
            update_active_data("2D plot")    
            
            calculate_2D_aggregates(active_data, agg_interval)
            
        except: 
        
            print('s')
        
        
        print(color_map_widget_plot2D)
        image_plot = aggregate_2D.hvplot.heatmap(
            x = 'columns',
            y = 'index',
            title = 'Hourly detections', 
            xlabel = 'Date',
            ylabel ='Hour of the day',
            

            selection_color = "red",
            
            #cmap ='rainbow', 
            cmap = color_map_widget_plot2D.name,
            #cmap = color_map_widget_plot2D,
            xaxis ='bottom',
            #xformatter=dateformatter,        
            rot = 70,
            width = 900, height = 500).opts(
                       
                fontsize={'title': 10, 'xticks': 10, 'yticks': 10},
                tools = ['tap', 'hover'],
                responsive = True,
                nonselection_alpha = 1,
                selection_alpha = 1,        
                #autorange="y",
            )   
        heatmap_tap.source = image_plot # Set the source of the heatmap tap object to the image plot.

        return image_plot # Return the image plot.



def find_audio_files(date_query,audio_files,bin_duration_sec=3600):
    """_summary_

    Args:
        date_query (_type_): _description_
        audio_files (_type_): _description_
        bin_duration_sec (int, optional): _description_. Defaults to 3600.

    Returns:
        _type_: _description_
    """    
    logger.debug("Finding audio files..")
    start_time= date_query
    end_time= start_time+np.timedelta64(bin_duration_sec, 's')
    files_list=audio_files[(audio_files['start_date'] > start_time) & (audio_files['start_date'] < end_time)]
    return list(files_list['file_name'].values)    


## 1D plot functionalities

lineplot_tap = hv.streams.Tap(x=0,y=0)
def get_lineplot_tap_date():
    """_summary_

    Returns:
        _type_: _description_
    """    
    logger.debug("Getting lineplot tap dates..")
    lineplot_tap_date = pd.Series(lineplot_tap.x).round('h')
    return lineplot_tap_date.values[0]

def get_files_dates(indir, file_ext ='.wav'):
    """_summary_

    Args:
        indir (_type_): _description_
        file_ext (str, optional): _description_. Defaults to '.wav'.

    Returns:
        pd.DataFrame: A pandas dataframe object with the file names and dates of the audio files.
    """    
    logger.debug("Getting file dates..")
    files_name = []
    files_date = []
    files = os.listdir(indir)
    for file in files:
        if os.path.isfile(os.path.join(indir,file)): # if file exists
            _, ext = os.path.splitext(file)
            if ext == file_ext: # list audio files only
                files_name.append(file)
    # retrieve dates from file names
    files_date = filename_to_datetime(files_name)
    files_list = pd.DataFrame({'file_name': files_name, 'start_date':files_date})
    return files_list



def callback_lineplot_selection(*events):
    """_summary_
    """    
    logger.debug(*events) # Log events.
    for event in events: # For each event.
        if (event.name == 'x') or (event.name == 'y'): # If the event is an x or y event.
            if event.new: # If the event is new.
                logger.debug(event.new.x) # Log the new x value.
                audio_files_multi_select.options = find_audio_files(get_lineplot_tap_date(), audio_files) # Set the options of the audio_files_multi_select object to the list of audio files.
                if audio_files_multi_select.options: # If there are audio files.
                    audio_files_multi_select.value = [audio_files_multi_select.options[0]]                    
                    #selection_multi_select.name = 'Selected points (' + str(len(selection_multi_select.options)) + ')'



def get_histogram_tap_date():
    """Get 

    Returns:
        _type_: _description_
    """    
    logger.info("Getting histogram tap date..")
    histogram_tap_date = histogram_tap
    return histogram_tap_date


def callback_heatmap_selection(*events):
    """_summary_

    Returns:
        _type_: _description_
    """    

    
    global HH
    global heatmap_tap_date
    global selection_interval
    global initial_datetime
    global final_datetime

    """
    Need to get an array of datetime objects for a selected day. We need the boundary conditions for the selected hour as a list or tuple.
    """
    
    
    selected_year = str(events[0][2].x).split("T")[0].split("-")[0] # This will happen when histogram cell is clicked.
    selected_month = str(events[0][2].x).split("T")[0].split("-")[1]
    selected_day = str(events[0][2].x).split("T")[0].split("-")[2]
    
    
    selected_hour = str(events[0][2].y).split(".")[0]
    selected_minute = str(events[0][2].y).split(".")[1]
    base_ten_minute = float("0." + str(events[0][2].y).split(".")[1])
    base_ten_time = float(selected_hour + "." + selected_minute)
    
    logger.debug( "selectied hour : " + str(selected_hour) )
    
    if len(selected_hour.split("-")) > 1: # Negative.
        
        if int(selected_hour) == 0:
            
            if float(base_ten_minute) < 0.5: # Bottom of the zeroth cell.

                selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 0, 0)
                selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 59, 59, 999999)
            
    
    if len(selected_hour.split("-")) == 1: # Positive or Zero.
        
        if int(selected_hour) == 0:
            
                
            if float(base_ten_minute) < 0.5: # Top of the zeroth cell.

                selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 0, 0)
                selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 59, 59, 999999)
                    
            if float(base_ten_minute) >= 0.5: # Bottom of first cell.
                    
                selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour) + 1, 0, 0)
                selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour) + 1, 59, 59, 999999)
                
        
            
        elif int(selected_hour) == 23:
            
            if float(base_ten_minute) < 0.5: # Bottom of selected_hour cell.

                selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 0, 0)
                selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 59, 59, 999999)
                    
            if float(base_ten_minute) >= 0.5: # Bottom of cell above.
                    
                pass # No cell is clicked
            
        else:
            
            if float(base_ten_minute) < 0.5: # Bottom of selected_hour cell.

                selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 0, 0)
                selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour), 59, 59, 999999)
                    
            if float(base_ten_minute) >= 0.5: # Bottom of cell above.
                    
                selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour) + 1, 0, 0)
                selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), int(selected_hour) + 1, 59, 59, 999999)
            
          
   
    
    
    logger.debug( "selection_time_initial : " + str(selection_time_initial) )
    logger.debug( "selection_time_final : " + str(selection_time_final) )
    
    
    selection_interval = ( selection_time_initial, selection_time_final )
    initial_datetime = selection_time_initial.strftime('%Y-%m-%d %H:%M:%S.%f')
    final_datetime = selection_time_final.strftime('%Y-%m-%d %H:%M:%S.%f')
    
    logger.debug( "datetime_interval : " + str(selection_interval) )
    
    datetime_range_picker.value = selection_interval
    


def callback_histogram_selection(*events):
    """_summary_

    Returns:
        _type_: _description_
    """
    

    global HH
    global histogram_tap_date
    global selected_day
    global selection_interval
    global initial_datetime
    global final_datetime
    global datetime_range_picker
    

    logger.debug(events)
    
    selected_year = str(events[0][2].x).split("T")[0].split("-")[0] # This will happen when histogram cell is clicked.
    selected_month = str(events[0][2].x).split("T")[0].split("-")[1]
    selected_day = str(events[0][2].x).split("T")[0].split("-")[2]
    
    
    selection_time_initial = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), 0, 0, 0)
    selection_time_final = datetime.datetime(int(selected_year), int(selected_month), int(selected_day), 23, 59, 59, 999999)
    
    
    #logger.debug( "selection_time_initial : " + str(selection_time_initial) )
    #logger.debug( "selection_time_final : " + str(selection_time_final) )
    
    
    selection_interval = ( selection_time_initial, selection_time_final )
    initial_datetime = selection_time_initial.strftime('%Y-%m-%d %H:%M:%S.%f')
    final_datetime = selection_time_final.strftime('%Y-%m-%d %H:%M:%S.%f')
    
    datetime_range_picker.value = selection_interval
    
    """
    Need to operate on active date.
    """
    



def show_file_selector(event):
    """This function just opens the file explorer widget implemented as a panel modal.

    Args:
        event (_type_): _description_
    """    
    #logger.debug(event) # Log event.
    global data_file_name
    global datetime_range_picker  # Declare datetime_range_picker as a global so it can handle the datetime_range_picker object.
    global dataset  # Declare dataset as a global so it can handle the dataset object.
    global dataframe_explorer_widget_locked
    
    settings_widgetbox.disabled = False
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    data_file_name = tk.filedialog.askopenfilename(multiple=True)
    data_file_name = list(data_file_name)
  
    logger.debug("A .nc file selection event has taken place.") # Log event of file selection.
    
    if len(data_file_name) > 1: # If more than one file is selected.
        
        logger.warning("Multiple files selected. Please select only one .nc file") # Log warning.
        
    else: # If only one file is selected.
            
            
        if len(data_file_name) > 0:
            
            data_file_name = str(data_file_name[0]) # Assign the path of the .nc file to the global variable.    
            print(data_file_name)
            file_extension = data_file_name.split(".")[-1] # Get the file extension of the selected file.

            if file_extension == "nc": # If the file extension is .nc then continue.
                
                #template.close_modal() # Close the modal object from panel template object.
                
                logger.info("Loading the selected file(s) : " + data_file_name ) # Log the file path.
                dataframe_explorer_widget_locked = False
                load_dataset(data_file_name) # Load the dataset object with the .nc file.
                update_active_data("Initial")
                show_datetime_range_picker() # Show the datetime range slider.
                #load_dataframe_explorer_widget(class_label_widget, threshold_widget, datetime_range_picker) # Load the dataframe explorer widget with the active_data object.

                
                template.close_modal() # Close the modal object from panel template object.
            
            else:
                
                logger.warning("The data format of the file selected is not supported. Please select a .nc file.") # Log warning.

            
            logger.debug("Loading date range picker...") # Log event of loading the date range slider.
    
            if 'date' in active_data.data.columns: # If the date column is in the active_data object.
                
                datetime_range_picker.value = (dataset.data['date'].min(), dataset.data['date'].max())
            

        
# Spectrogram
def spectrogram_plot(index = None):
    """The purpose of this function is to load the spectrogram plot pane. The plot depends on the index and play_sound widgets for interactivity.

    Args:
        index (int): The index represents the index of active_data.data.
        play_sound (boolean): There is a checkbox widget that is responsible for this boolean value.

    Returns:
        pn.pane.Matplotlib: Returns a Matplotlib pane object with the spectrogram plot.
    """    
    logger.debug("Loading spectrogram plot") # Log event of a spectrogram plot being loaded.
    
    global spectrogram_plot_pane # Global variable for the spectrogram plot pane.
    global spectrogram_metadata_explorer
    global selected_sound
    global color_map_widget_spectrogram
    
    if (type(index)==int) and (dataset is not None): # If there is an index value associated with a detection event.
        
        frame = 0.03 #3000
        nfft = 0.08 # 4096
        step = 0.01 # 5
        window_type = 'hann'
        time_buffer = 2
        frequency_buffer = 100
        palet = 'Blues' # 'binary'
        
        data_selection = active_data.data.loc[index]
        
        
        data_selection_df = data_selection.to_frame()
        
        
        # initialize list of lists
        data = [['date', str(data_selection_df.loc['date'][index])], 
                ['uuid', str(data_selection_df.loc['uuid'][index])], 
                ['from_detector', str(data_selection_df.loc['from_detector'][index])],
                ['software_name', str(data_selection_df.loc['software_name'][index])], 
                ['software_version', str(data_selection_df.loc['software_version'][index])],
                ['operator_name', str(data_selection_df.loc['operator_name'][index])], 
                ['UTC_offset', str(data_selection_df.loc['UTC_offset'][index])],
                ['entry_date', str(data_selection_df.loc['entry_date'][index])], 
                ['audio_channel', str(data_selection_df.loc['audio_channel'][index])],
                ['audio_file_name', str(data_selection_df.loc['audio_file_name'][index])], 
                ['audio_file_dir', str(data_selection_df.loc['audio_file_dir'][index])],
                ['audio_file_extension', str(data_selection_df.loc['audio_file_extension'][index])], 
                ['audio_file_start_date', str(data_selection_df.loc['audio_file_start_date'][index])],
                ['audio_sampling_frequency', str(data_selection_df.loc['audio_sampling_frequency'][index])], 
                ['audio_bit_depth', str(data_selection_df.loc['audio_bit_depth'][index])],
                ['mooring_platform_name', str(data_selection_df.loc['mooring_platform_name'][index])], 
                ['recorder_type', str(data_selection_df.loc['recorder_type'][index])],
                ['recorder_SN', str(data_selection_df.loc['recorder_SN'][index])], 
                ['hydrophone_model', str(data_selection_df.loc['hydrophone_model'][index])],
                ['hydrophone_SN', str(data_selection_df.loc['hydrophone_SN'][index])], 
                ['hydrophone_depth', str(data_selection_df.loc['hydrophone_depth'][index])],
                ['location_name', str(data_selection_df.loc['location_name'][index])], 
                ['location_lat', str(data_selection_df.loc['location_lat'][index])],
                ['location_lon', str(data_selection_df.loc['location_lon'][index])], 
                ['location_water_depth', str(data_selection_df.loc['location_water_depth'][index])],
                ['deployment_ID', str(data_selection_df.loc['deployment_ID'][index])], 
                ['frequency_min', str(data_selection_df.loc['frequency_min'][index])],
                ['frequency_max', str(data_selection_df.loc['frequency_max'][index])], 
                ['time_min_offset', str(data_selection_df.loc['time_min_offset'][index])],
                ['time_max_offset', str(data_selection_df.loc['time_max_offset'][index])], 
                ['time_min_date', str(data_selection_df.loc['time_min_date'][index])],
                ['time_max_date', str(data_selection_df.loc['time_max_date'][index])], 
                ['duration', str(data_selection_df.loc['duration'][index])],
                ['label_class', str(data_selection_df.loc['label_class'][index])], 
                ['label_subclass', str(data_selection_df.loc['label_subclass'][index])],
                ['confidence', str(data_selection_df.loc['confidence'][index])]]
        
        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=['Label', 'Data'])
        

        
        
        spectrogram_metadata_explorer.layout = 'fit_columns'
        spectrogram_metadata_explorer.value = df
        
        
        
        wavfilename = os.path.join(data_selection.audio_file_dir, data_selection.audio_file_name + data_selection.audio_file_extension)
        logger.debug(wavfilename)

        
        t1 = data_selection.time_min_offset - time_buffer
        t2 = data_selection.time_max_offset + time_buffer
             
        # load audio data
        sound = Sound(wavfilename)
        selected_sound = sound
        
        if t1 < 0:
            t1=0
        if t2 > sound.file_duration_sec:
            t2 = sound.file_duration_sec
        
        sound.read(channel=data_selection.audio_channel -1, chunk=[t1, t2], unit='sec', detrend=True)

        
        spectro = Spectrogram(frame, window_type, nfft, step, sound.waveform_sampling_frequency, unit='sec')
        spectro.compute(sound, dB=True, use_dask=False, dask_chunks=40)
    
        annot = Annotation() # Create an Annotation object.
        annot.data = pd.concat([annot.data, pd.DataFrame({'time_min_offset': [time_buffer],
                                                          'time_max_offset': [time_buffer + data_selection.duration],
                                                          'frequency_min': [data_selection.frequency_min],
                                                          'frequency_max': [data_selection.frequency_max],
                                                          'duration':[data_selection.duration] })], ignore_index=True) # Concatenate the Annotation object with a pandas dataframe object.
        
        
        
                       
        # Plot
        fmax = data_selection.frequency_max + frequency_buffer 
        fmin = data_selection.frequency_min - frequency_buffer
        if fmin <0:
            fmin=0
        graph = GrapherFactory('SoundPlotter', title=str(index) + ': ' +data_selection.label_class + ' - ' +data_selection.label_subclass, frequency_max=fmax, frequency_min=fmin) # Create a GrapherFactory object.
        graph.add_data(spectro) # Add the spectrogram object to the graph object.
        graph.add_annotation(annot, panel=0, color='black', label='Detections') # Add the Annotation object to the graph object.

        graph.colormap = color_map_widget_spectrogram.value_name 
        
        fig, ax = graph.show(display=False) # Create a figure and axes object.
        fig.set_size_inches(14, 8) # Set the size of the figure.
        
        spectrogram_plot_pane.param.trigger("object")
        spectrogram_plot_pane.object = fig

    

    else:
        pass
        #spectrogram_plot_pane.param.trigger("object")
        #spectrogram_plot_pane.object = test_matplotlib()
        #return spectrogram_plot_pane
    

def test_matplotlib():
    df = pd.DataFrame({"a": [0, 0, 1, 1], "b": [0, 1, 3, 2]})
    s = df[df['a'] == 1]['b']
    fig, ax = plt.subplots()
    #fig.set_size_inches(14, 4) # Set the size of the figure.
    fig.tight_layout()
    s.plot(ax=ax)
    plt.close(fig)
    return fig


#@pn.depends()
def show_datetime_range_picker():
    """_summary_

    Returns:
        _type_: _description_
    """    
    global datetime_range_picker # Declare datetime_range_picker as a global so it can handle the datetime_range_picker object.
    logger.debug("Loading date range picker...") # Log event of loading the date range slider.
    
    if 'date' in active_data.data.columns: # If the date column is in the active_data object.
        
        
        datetime_range_picker.value = (active_data.data['date'].min(), active_data.data['date'].max())
        return datetime_range_picker # Return the DatetimeRangePicker object.
    
    else:
        
        return datetime_range_picker # Return the DatetimeRangePicker object.
    
@pn.depends(class_label_widget, threshold_widget, datetime_range_picker)
def load_dataframe_explorer_widget(class_label_widget, threshold_widget, datetime_range_picker):
    """The purpose of this function it to load the active_data Annotation dataframe element into the DataFrame explorer widget.

    Returns:
        pn.widgets.Tabulator: Returns a Tabulator DataFrame explorer widget with (updated) active_data available. 
    """    
    
    global active_data # Declare active_data as a global so it can handle the active_data object.
    global dataset # Declare dataset as a global so it can handle the dataset object.
    global data_file_name # Declare data_file_name as a global so it can handle the data_file_name object.
    global dataframe_explorer_widget # Declare dataframe_explorer_widget as a global so it can handle the dataframe_explorer_widget object.
    global selection_interval # Declare selection_interval as a global so it can handle the selection_interval object.
    global initial_datetime
    global final_datetime   
    global dataframe_explorer_widget_locked
    
    if len(list(data_file_name)) > 0: # If the data_file_name object is not empty.
    
        logger.debug("Loading 'active_data' dataframe explorer widget..") # Log event of loading the dataframe explorer widget.
        
        subselection = copy.deepcopy(active_data)

        if (not dataframe_explorer_widget_locked) & (datetime_range_picker is not None):    
            
            initial_datetime = datetime_range_picker[0].strftime('%Y-%m-%d %H:%M:%S.%f')
            final_datetime = datetime_range_picker[1].strftime('%Y-%m-%d %H:%M:%S.%f')
            subselection.filter('date >= "'+initial_datetime+'" and date <= "'+final_datetime+'"', inplace=True ) #TODO : This is not right.
            #subselection = active_data.data[['date', 'confidence', 'label_class', 'audio_file_dir', 'audio_file_name', 'hydrophone_SN']]     
            
            if not subselection.data.empty:
            #dataframe_explorer_widget.value = subselection.data[['date', 'confidence', 'label_class', 'audio_file_dir', 'audio_file_name', 'hydrophone_SN']]
            
                try:
                    
                    dataframe_explorer_widget.value = subselection.data[['label_class','date','confidence']]
                    return dataframe_explorer_widget
                
                except IndexError:
                    return None
            
  
def click_dataframe_explorer_widget(event = None):
    global color_map_widget_spectrogram
    
    try:
        
        selected_raw_index = int(dataframe_explorer_widget.value.iloc[dataframe_explorer_widget.selection[0]].name)
        print(f'Index of the detection selected: {selected_raw_index}')
        print('s')
        spectrogram_plot(index = selected_raw_index)
    
    except IndexError:
        #dataframe_explorer_widget.selection = []
        spe
        return None

         
def play_selected_sound(event):
    global selected_sound
    try:
        sd.play(selected_sound.waveform/max(selected_sound.waveform), selected_sound.waveform_sampling_frequency)
    except NameError:
        pass    
    else:
        pass

def stop_selected_sound(event = None):
    try:
        sd.stop()
    except NameError:
        pass    
    else:
        pass

@pn.depends(class_label_widget, threshold_widget)
def load_detections(class_label_widget, threshold_widget): 
    """The purpose of this function is to load the detections widget. 
    These detections are filtered because they come through the active_data object.
    These detections are also ordered by confidence; Highest to lowest.

    Args:
        active_data (Annotation): Filtered dataset.
    """    
    global active_data # Declare active_data as a global so it can handle the active_data object.
    global detec_files_multi_select # Declare detec_files_multi_select as a global so it can handle the detec_files_multi_select object.
    logger.debug("Loading detection by ascending order..") # Log event of loading the detections widget.
    detec_list_index = list( active_data.data["confidence"].sort_values(ascending = False)) # Create a list of detections sorted by confidence; Highest to lowest.
    
    detec_files_multi_select.options = detec_list_index # Set the options of the detec_files_multi_select object to the list of detections sorted by confidence; Highest to lowest.
    detec_files_multi_select.value = [detec_files_multi_select.options[0]] # Set the value of the detec_files_multi_select object to the first detection in the list of detections sorted by confidence; Highest to lowest.
    detec_files_multi_select.name = 'Detections (' + str(len(active_data)) + ')' # Set detections label showing the quantity of detections per active_data.


watcher_heatmap = heatmap_tap.param.watch(callback_heatmap_selection, ['x','y'], onlychanged = False) # Watcher for heatmap tap events.
#watcher_histogram = histogram_tap.param.watch(callback_histogram_selection, ['x','y'], onlychanged = False) # Watcher for heatmap tap events.

dataframe_explorer_widget.on_click(click_dataframe_explorer_widget)





watcher_lineplot = lineplot_tap.param.watch(callback_histogram_selection, ['x','y'], onlychanged = False )



# Panel Template

template = pn.template.BootstrapTemplate( title = 'SoundScope',logo='SoundScopeLogo.png' ) # Basic 'Bootstrap' template object for python3 Panel lib. Ref : https://panel.holoviz.org/reference/templates/Bootstrap.html


# Buttons

select_file_button = pn.widgets.Button(name = "Select file", button_type = 'primary') # This button is responsible for opening the file selector.
play_sound_button = pn.widgets.Button(icon='player-play', name='Play', button_type='primary', icon_size='2em', width = 200, height = 50, margin = (30,10,10,75))
stop_sound_button = pn.widgets.Button(icon='player-stop', name='Stop', button_type='primary', icon_size='2em', width = 200, height = 50, margin = (30,10,10,10))

# Widget boxes
file_selection_label_widget = pn.widgets.StaticText(name='NetCDF file', value='Please select a file', sizing_mode='stretch_width') # Text with file selected.
openfile_widgetbox = pn.WidgetBox( file_selection_label_widget, select_file_button, margin = (10,10), sizing_mode = 'stretch_width' ) # Widget object from python3 panel library. This object is a container for file selection related widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html
settings_widgetbox = pn.WidgetBox( class_label_widget, threshold_widget, disabled = False, margin=(10,10), sizing_mode = 'stretch_width' ) # Widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html

detec_files_multi_select = pn.widgets.MultiSelect(name='Detections', value= [], options=[], size=8)
file_name_markdown = pn.pane.Markdown("", width=100)

# Side panel
template.sidebar.append( pn.Column( openfile_widgetbox, settings_widgetbox ) ) # Appends the openfile_widgetbox and settings_widgetbox to the sidebar object from panel template object.

# Main page
top_panel_tabs = pn.Tabs( ('Hourly Detections', pn.WidgetBox(pn.Column(pn.Row(color_map_widget_plot2D, integration_time_widget),create_2D_plot), disabled = False, margin=(10,10), sizing_mode = 'stretch_width' )))
top_panel_tabs.append(('Daily Detections', pn.WidgetBox( create_1D_plot, disabled = False, margin=(10,10), sizing_mode = 'stretch_width' ) )) # This is one place active data is updated.
top_panel_tabs.append(('Custom Dates Selection', datetime_range_picker))

spectrogram_tabs = pn.Tabs(( 'Spectrogram', pn.WidgetBox( pn.Column( pn.Row(play_sound_button, stop_sound_button, color_map_widget_spectrogram), spectrogram_plot_pane), disabled = False, margin=(10,10))))
spectrogram_tabs.append(( 'Metadata', pn.WidgetBox( spectrogram_metadata_explorer, disabled = True, margin=(10,10), sizing_mode = 'stretch_width' )))

#bottom_panel = pn.Row(spectrogram_tabs,pn.WidgetBox( load_dataframe_explorer_widget, disabled = False, margin=(45,10,10,10), sizing_mode = 'stretch_both' ))
bottom_panel = pn.Row(spectrogram_tabs,pn.WidgetBox( load_dataframe_explorer_widget, disabled = False, margin=(45,10,10,10), width=515))

template.main.append(pn.Column(top_panel_tabs,bottom_panel))



# Modal

#template.modal.append( file_selector ) # Appends file selector to model object.
#template.modal.append( load_button ) # Appends load button to model object.
select_file_button.on_click( show_file_selector ) # Defines the action of the select_file_button object which is a file selection module.
play_sound_button.on_click( play_selected_sound )
#load_button.on_click( get_selection ) # 
stop_sound_button.on_click( stop_selected_sound )

#template.modal[0].value = [""]

# Serve Application

logger.debug("Serving Panel Template..")

template.servable()
template.show()