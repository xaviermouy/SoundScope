#!/usr/bin/python3
# coding: utf-8

# Libraries
import time
import os  # For dealiing with paths and directories mostly.
from sys import version
from _version import __version__
import cv2
import numpy as np
import pytz
import panel as pn  # Flask like framework with a great library for modular installation of graphical components.
import copy  # For use of deep copying. We use it in the creation of active data so that we will unhinder the original object's memory.

from distributed.diagnostics.nvml import one_time
from ecosound.core.tools import (
    filename_to_datetime,
)  # Ecosound filename to datetime function.
from ecosound.core.measurement import (
    Measurement,
)  # Ecosound Measurement class object. Special case of Annotation.
from ecosound.core.annotation import Annotation  # Ecosound Annotation class object.
from ecosound.core.audiotools import Sound  # Ecosound Sound class object.
from ecosound.core.spectrogram import Spectrogram  # Ecosound Spectrogram class object.
from ecosound.visualization.grapher_builder import (
    GrapherFactory,
)  # Ecosound GrapherFactory class object.
# from dask.distributed import Client # Dask distributed client for parallel computing.
import numpy as np  # Numpy library for numerical manipulation in python3.
import pandas as pd  # Pandas library for dataframe objects.
import datetime  # Datetime library for datetime objects.
import holoviews as hv  # Holoviews library for interactive plotting.
import hvplot.pandas  # Holoviews plotting library for pandas objects.
import tkinter as tk
import tkinter.filedialog as file_chooser_dialog
import matplotlib
from holoviews.operation import threshold
from numba.cuda import event

matplotlib.use('agg')
from bokeh.models.formatters import (
    DatetimeTickFormatter,
)  # Bokeh datetime formatter for plotting.
# from bokeh.models import CustomJS
# from bokeh.io import curdoc

# import keyboard
# import threading
# import time

from matplotlib.cm import (
    Reds,
    Blues,
    Greens,
    viridis,
    hsv,
    binary,
    hot,
)  # Matplotlib colormaps.
import matplotlib.pyplot as plt  # Matplotlib plot object for plotting.
from matplotlib.figure import Figure
from matplotlib import cm
import warnings  # Warnings library for displaying warnings.
from loguru import logger  # A great logger option.
import datetime
import sounddevice as sd
import logging
from inspect import getmembers, isclass

import panel as pn
from panel.custom import ReactComponent
import param
#from typing import TypedDict, NotRequired
from typing import TypedDict
from typing_extensions import NotRequired

plt.ioff()

def exception_handler(ex):
    logging.error("Error", exc_info=ex)
    pn.state.notifications.error('Error: %s' % ex)

# # Note: this uses TypedDict instead of Pydantic or dataclass because Bokeh/Panel doesn't seem to
# # like serializing custom classes to the frontend (and I can't figure out how to customize that).
# class KeyboardShortcut(TypedDict):
#     name: str
#     key: str
#     altKey: NotRequired[bool]
#     ctrlKey: NotRequired[bool]
#     metaKey: NotRequired[bool]
#     shiftKey: NotRequired[bool]
#
#
# class KeyboardShortcuts(ReactComponent):
#     """
#     Class to install global keyboard shortcuts into a Panel app.
#
#     Pass in shortcuts as a list of KeyboardShortcut dictionaries, and then handle shortcut events in Python
#     by calling `on_msg` on this component. The `name` field of the matching KeyboardShortcut will be sent as the `data`
#     field in the `DataEvent`.
#
#     Example:
#     >>> shortcuts = [
#         KeyboardShortcut(name="save", key="s", ctrlKey=True),
#         KeyboardShortcut(name="print", key="p", ctrlKey=True),
#     ]
#     >>> shortcuts_component = KeyboardShortcuts(shortcuts=shortcuts)
#     >>> def handle_shortcut(event: DataEvent):
#             if event.data == "save":
#                 print("Save shortcut pressed!")
#             elif event.data == "print":
#                 print("Print shortcut pressed!")
#     >>> shortcuts_component.on_msg(handle_shortcut)
#     """
#
#     shortcuts = param.List(class_=dict)
#
#     _esm = """
#     // Hash a shortcut into a string for use in a dictionary key (booleans / null / undefined are coerced into 1 or 0)
#     function hashShortcut({ key, altKey, ctrlKey, metaKey, shiftKey }) {
#       return `${key}.${+!!altKey}.${+!!ctrlKey}.${+!!metaKey}.${+!!shiftKey}`;
#     }
#
#     export function render({ model }) {
#       const [shortcuts] = model.useState("shortcuts");
#
#       const keyedShortcuts = {};
#       for (const shortcut of shortcuts) {
#         keyedShortcuts[hashShortcut(shortcut)] = shortcut.name;
#       }
#
#       function onKeyDown(e) {
#         const name = keyedShortcuts[hashShortcut(e)];
#         if (name) {
#           e.preventDefault();
#           e.stopPropagation();
#           model.send_msg(name);
#           return;
#         }
#       }
#
#       React.useEffect(() => {
#         window.addEventListener('keydown', onKeyDown);
#         return () => {
#           window.removeEventListener('keydown', onKeyDown);
#         };
#       });
#
#       return <></>;
#     }
#     """


pn.extension(exception_handler=exception_handler, notifications=True)
warnings.filterwarnings("always")  # Warning configuration.
np.random.seed(7)
pn.extension(
    "tabulator", sizing_mode="stretch_width", loading_spinner="dots",exception_handler=exception_handler, notifications=True
)  # Panel extension configuration.
pn.extension("modal")
pn.config.throttled = True  # Update only when mouse click release.
pn.extension(
    loading_spinner="dots", loading_color="lightblue"
)  # Loading spinner, loading_color='#00aa41' .
pn.param.ParamMethod.loading_indicator = (
    True  # Indicate to user when a loading session is done.
)
pn.extension()
# Global variables
global data_file_name  # path of NetCDF file
data_file_name = ""
global dataset  # detection/annotation ecosound object from netcdf file
global active_data  # detection/annotation ecosound object displayed (i.e. filtered)
global aggregate_1D  # pandas dataframe with 1D aggregate of detections/annotations
global aggregate_2D  # pandas dataframe with 2D aggregate of detections/annotations
global plot_2D  # holoviews object with 2D plot
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
global frame_dur_widget
global fft_dur_widget
global step_dur_widget
global time_buffer_widget
global frequency_buffer_widget
global recordings_timezone
global analysis_timezone
global TZ_offset

logger.debug("Initializing variables..")  # Log initialization of variables.

# Initialize variables / Parameters.

dataset = None  # Initialize dataset object to None.
active_data = Annotation()  # Initialize active_data object to Annotation object.
d = pd.DataFrame(
    0, index=[0], columns=active_data.data
)  # Initialize pandas dataframe object to 0.
active_data.data = pd.concat(
    [active_data.data, d]
)  # Concatenate active_data object with pandas dataframe object. TODO: Get more context.

selection_interval = (None, None)
initial_datetime = ""
final_datetime = ""

# Time aggregate values: mapping of text displayed in widget -> str used by pandas
time_aggregate_mapping_2D = {
    #    '5 minutes':  '5Min',
    #    '15 minutes': '15Min',
    #    '30 minutes': '30Min',
    "1 hour": "1H",
    #    '2 hours': '2H',
    #    '3 hours': '3H',
    #    '4 hours': '4H',
    #    '5 hours': '5H',
    #    '6 hours': '6H',
    #    '12 hours':'12H',
}

# Colormaps for 2D plot
cmaps_plot2D = {
    "viridis": viridis,
    "hot": hot,
    "binary": binary,
    "hsv": hsv,
    "Reds": Reds,
    "Blues": Blues,
    "Greens": Greens,
}

# init Aggregate_1D
date_today = datetime.date.today()
days = pd.date_range(date_today, date_today + datetime.timedelta(7), freq="D")
data = np.zeros(len(days))
aggregate_1D = pd.DataFrame({"datetime": days, "value": data})
aggregate_1D = aggregate_1D.set_index("datetime")


# init Aggregate_2D
# aggregate_2D = pd.DataFrame({'date1':np.zeros(24),'date2':np.zeros(24),'date3':np.zeros(24)})
aggregate_2D = pd.DataFrame(columns=days, index=range(0, 24))  #
aggregate_2D = aggregate_2D.fillna(
    0
)  # Fill NaN values with 0 for the aggregate_2D object.


# Widgets
global spectro_loading_spinner
spectro_loading_spinner = pn.indicators.LoadingSpinner(value=False, height=50, name=' ')
spectro_loading_spinner.visible=False
audio_files_multi_select = pn.widgets.MultiSelect(
    name="Audio files", value=[], options=[], size=8
)  # Audio files widget object from python3 panel library. This object is a container for audio files. Ref : https://panel.holoviz.org/reference/widgets/MultiSelect.html

# Confidence threshold slider
threshold_widget = pn.widgets.DiscreteSlider(
    name="Confidence threshold", options=list(np.arange(0, 1.01, 0.01)), value=0.5
)  # Slider widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/widgets/DiscreteSlider.html

# Confidence threshold slider
dpi_widget = pn.widgets.DiscreteSlider(
    name="DPI", options=list(np.arange(10, 500, 5)), value=100
)  #

# Sound class to display
class_label_widget = pn.widgets.Select(
    name="Class label", options=[]
)  # Select widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/widgets/Select.html

analysis_timezone_text = pn.pane.Markdown("", sizing_mode='stretch_width')

# Integration time
# integration_time_widget = pn.widgets.Select(name='Integration time', options=list(time_aggregate_mapping_2D.keys()),height=70, sizing_mode='stretch_width')
integration_time_widget = pn.widgets.Select(
    name="Integration time",
    options=list(time_aggregate_mapping_2D.keys()),
    height=70,
    width=200,
    margin=(10, 10, 10, 10),
)
integration_time_widget.value = integration_time_widget.options[0]

# colormap selectro for 2D plot
color_map_widget_plot2D = pn.widgets.ColorMap(
    #name="Colormap",
    options=cmaps_plot2D,
    align=('center'),
    ncols=1,
    height=30,
    width=250,
    margin=(0, 0, 0, 20),
)
# color_map_widget_spectrogram = pn.widgets.ColorMap(options = cmaps_plot2D, ncols=1, height=50, width = 200, margin = (30,10,10,10))
color_map_widget_spectrogram = pn.widgets.ColorMap(
    name="Colormap",
    value=cmaps_plot2D["binary"],
    options=cmaps_plot2D,
    ncols=1,
)

file_selector = pn.widgets.FileSelector("~")
file_input = pn.widgets.FileInput(accept=".nc")

# Spectrogram widgets
frame_dur_widget = pn.widgets.FloatInput(
    name="Frame length (s)", value=0.03, step=0.01, start=0.0001, end=10
)
fft_dur_widget = pn.widgets.FloatInput(
    name="FFT length (s)", value=0.08, step=0.01, start=0.0001, end=10
)
step_dur_widget = pn.widgets.FloatInput(
    name="Step (s)", value=0.01, step=0.01, start=0.001, end=10
)
time_buffer_widget = pn.widgets.FloatInput(
    name="Time buffer (s)", value=2, step=1, start=0, end=500
)

frequency_bounds_mode_widget = pn.widgets.Switch(
    name="Use fixed frequency bounds",
    value=True,  # Default to adaptive (False = adaptive, True = fixed)
    width=30,
    #margin=(10, 10, 10, 10)
)

frequency_buffer_widget = pn.widgets.FloatInput(
    name="Frequency buffer (Hz)", value=100, step=1, start=0, end=10000
)

frequency_min_widget = pn.widgets.FloatInput(
    name="Frequency min. (Hz)", value=0, step=1, start=0, end=500000
)

frequency_max_widget = pn.widgets.FloatInput(
    name="Frequency max. (Hz)", value=1000, step=1, start=0, end=500000
)
frequency_mode_widget = pn.widgets.StaticText(
    name="",
    value="<b>Frequency limits mode ",
    sizing_mode="stretch_width"
)

frequency_mode_status_widget = pn.widgets.StaticText(
    name="",
    value=" Frequency limits: ADAPTIVE",
    #sizing_mode="stretch_width"
)

# Callback function to handle the switch toggle
def toggle_frequency_bounds_mode(event):
    if frequency_bounds_mode_widget.value:  # Fixed mode
        # Disable adaptive buffer
        frequency_buffer_widget.visible= True
        # Enable fixed bounds widgets
        frequency_min_widget.visible = False
        frequency_max_widget.visible = False
        frequency_mode_status_widget.value = " Frequency limits: ADAPTIVE"
        # sizing_mode="stretch_width"

    else:  # Adaptive mode
        # Enable adaptive buffer
        frequency_buffer_widget.visible = False
        # Disable fixed bounds widgets
        frequency_min_widget.visible = True
        frequency_max_widget.visible = True
        frequency_mode_status_widget.value = " Frequency limits: FIXED"

# Watch for changes in the switch
frequency_bounds_mode_widget.param.watch(toggle_frequency_bounds_mode, 'value')

# Initialize the widget states based on default switch value
toggle_frequency_bounds_mode(None)

# Stream
lineplot_tap = hv.streams.Tap(x=0, y=0)
heatmap_tap = hv.streams.Tap(
    x=0, y=0
)  # Declare Tap stream with heatmap as source and initial values.
histogram_tap = hv.streams.Tap(
    x=0, y=0
)  # Declare Tap stream with histogram as source and initial values.


detec_files_multi_select = pn.widgets.MultiSelect(
    name="Detections", value=[], options=[], size=8
)
# sound_checkbox = pn.widgets.Checkbox(name='Automatically play selected sound', value=False)
file_name_markdown = pn.pane.Markdown("", width=100)

dataframe_explorer_widget = pn.widgets.Tabulator(
    name="Detection Dataframe Window",
    selectable=1,
    value=active_data.data,
    height=655,
    disabled=True,
    selection=[0],
    pagination="remote",
)
#spectrogram_plot_pane = pn.pane.Matplotlib(name="Spectrogram", fixed_aspect=False, height=565,dpi=80)
spectrogram_plot_pane = pn.pane.PNG('images/SoundScopeWelcome.png',height=565,)
spectrogram_metadata_explorer = pn.widgets.Tabulator(
    name="Metadata",
    sizing_mode="stretch_width",
    height=656,
    disabled=True,
    selection=[0],
    pagination="remote",
    page_size=50,
    show_index=False,
)

datetime_range_picker = pn.widgets.DatetimeRangePicker(
    name="Datetime Range Selection", sizing_mode="stretch_width"
)
dataframe_explorer_widget_locked = True

def rasterize_and_save(fname, rasterize_list=None, fig=None, dpi=None,
                       savefig_kw={}):
    """Save a figure with raster and vector components
    This function lets you specify which objects to rasterize at the export
    stage, rather than within each plotting call. Rasterizing certain
    components of a complex figure can significantly reduce file size.
    https://brushingupscience.wordpress.com/2017/05/09/vector-and-raster-in-one-with-matplotlib/
    Inputs
    ------
    fname : str
        Output filename with extension
    rasterize_list : list (or object)
        List of objects to rasterize (or a single object to rasterize)
    fig : matplotlib figure object
        Defaults to current figure
    dpi : int
        Resolution (dots per inch) for rasterizing
    savefig_kw : dict
        Extra keywords to pass to matplotlib.pyplot.savefig
    If rasterize_list is not specified, then all contour, pcolor, and
    collects objects (e.g., ``scatter, fill_between`` etc) will be
    rasterized
    Note: does not work correctly with round=True in Basemap
    Example
    -------
    Rasterize the contour, pcolor, and scatter plots, but not the line
    >>> import matplotlib.pyplot as plt
    >>> from numpy.random import random
    >>> X, Y, Z = random((9, 9)), random((9, 9)), random((9, 9))
    >>> fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(ncols=2, nrows=2)
    >>> cax1 = ax1.contourf(Z)
    >>> cax2 = ax2.scatter(X, Y, s=Z)
    >>> cax3 = ax3.pcolormesh(Z)
    >>> cax4 = ax4.plot(Z[:, 0])
    >>> rasterize_list = [cax1, cax2, cax3]
    >>> rasterize_and_save('out.svg', rasterize_list, fig=fig, dpi=300)
    """

    # Behave like pyplot and act on current figure if no figure is specified
    fig = plt.gcf() if fig is None else fig

    # Need to set_rasterization_zorder in order for rasterizing to work
    zorder = -5  # Somewhat arbitrary, just ensuring less than 0

    if rasterize_list is None:
        # Have a guess at stuff that should be rasterised
        types_to_raster = ['QuadMesh', 'Contour', 'collections']
        rasterize_list = []

        print("""
        No rasterize_list specified, so the following objects will
        be rasterized: """)
        # Get all axes, and then get objects within axes
        for ax in fig.get_axes():
            for item in ax.get_children():
                if any(x in str(item) for x in types_to_raster):
                    rasterize_list.append(item)
        print('\n'.join([str(x) for x in rasterize_list]))
    else:
        # Allow rasterize_list to be input as an object to rasterize
        if type(rasterize_list) != list:
            rasterize_list = [rasterize_list]

    for item in rasterize_list:

        # Whether or not plot is a contour plot is important
        is_contour = (isinstance(item, matplotlib.contour.QuadContourSet) or
                      isinstance(item, matplotlib.tri.TriContourSet))

        # Whether or not collection of lines
        # This is commented as we seldom want to rasterize lines
        # is_lines = isinstance(item, matplotlib.collections.LineCollection)

        # Whether or not current item is list of patches
        all_patch_types = tuple(
            x[1] for x in getmembers(matplotlib.patches, isclass))
        try:
            is_patch_list = isinstance(item[0], all_patch_types)
        except TypeError:
            is_patch_list = False

        # Convert to rasterized mode and then change zorder properties
        if is_contour:
            curr_ax = item.ax.axes
            curr_ax.set_rasterization_zorder(zorder)
            # For contour plots, need to set each part of the contour
            # collection individually
            for contour_level in item.collections:
                contour_level.set_zorder(zorder - 1)
                contour_level.set_rasterized(True)
        elif is_patch_list:
            # For list of patches, need to set zorder for each patch
            for patch in item:
                curr_ax = patch.axes
                curr_ax.set_rasterization_zorder(zorder)
                patch.set_zorder(zorder - 1)
                patch.set_rasterized(True)
        else:
            # For all other objects, we can just do it all at once
            curr_ax = item.axes
            curr_ax.set_rasterization_zorder(zorder)
            item.set_rasterized(True)
            item.set_zorder(zorder - 1)

    # dpi is a savefig keyword argument, but treat it as special since it is
    # important to this function
    if dpi is not None:
        savefig_kw['dpi'] = dpi

    # Save resulting figure
    fig.savefig(fname, **savefig_kw,transparent=False)

def update_analysis_timezone_text(analysis_timezone):
    #analysis_timezone_text.object = f"Time zone of analysis: UTC {analysis_timezone}"
    #analysis_timezone_text.object =r"<p style = 'text-align:right;'>Time zone of analysis: UTC " + str(analysis_timezone) + "</p>"
    analysis_timezone_text.object = r"<p style = 'text-align:right;'><font size=3px'>Time zone of analysis: UTC " + str(analysis_timezone) + "</font color></p>"
    #analysis_timezone_text.object = "<right># Time zone of analysis: UTC " + str(analysis_timezone) + "</right>"


def apply_time_offset(dataset, time_offset_hours):
    dataset.data.time_min_date = dataset.data.time_min_date + pd.Timedelta(time_offset_hours, unit='h')
    dataset.data.time_max_date = dataset.data.time_max_date + pd.Timedelta(time_offset_hours, unit='h')
    dataset.data.date = dataset.data.date + pd.Timedelta(time_offset_hours, unit='h')
    return dataset

def load_dataset(data_file):
    """performs necessary actions to get widgets loaded and variables updated once the .nc file is selected.

    Args:
        data_file (str): A file with a .nc extension strictly speaking however the contents of the .nc will ultimately decide if it is compatible. Certain tables will be expected.

    Raises:
        e: If the contents are not expected some exceptions will be raised since the .nc file extension is not enough to fully vet the import. This function handles this.
    """
    logger.debug("Loading .nc file dataset.")
    global dataset  # Globally declares dataset object.
    global recordings_timezone
    global analysis_timezone
    global TZ_offset

    TZ_offset = analysis_timezone - recordings_timezone # time offset
    try:
        dataset = Measurement()  # Attempt at assigning a Measurement interface (Special case of Annotation object).
        dataset.from_netcdf(data_file)
        success_notification("Dataset successfully loaded!")
        # apply time zone offset
        dataset = apply_time_offset(dataset, TZ_offset)
        # update class labels in widget
        update_class_label_widget()

    except:
        try:
            dataset = (
                Annotation()
            )  # Attempt at assigning a Annotation (more general purpose) interface.
            dataset.from_netcdf(data_file)
            success_notification("Dataset loaded!")
            # apply time zone offset
            dataset = apply_time_offset(dataset, TZ_offset)
            # update class labels in widget
            update_class_label_widget()
            # update text with analysis time zone
            update_analysis_timezone_text(analysis_timezone)

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
    pn.state.notifications.position = "top-right"
    pn.state.notifications.error(msg_str, duration=3000)


# Display success notifications
def success_notification(msg_str):
    """Success message implemented as a log and a notification.

    Args:
        msg_str (str): Message to be displayed.
    """
    pn.state.notifications.position = "top-right"
    pn.state.notifications.success(msg_str, duration=3000)


def update_datetime_range_picker_widget():
    global datetime_range_picker
    datetime_range_picker.value

# populate/update class label widget
def update_class_label_widget():
    """Updates the class label widget with the labels from the dataset object."""
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
        aggregate_2D = active_data.calc_time_aggregate_2D(integration_time=agg_interval)
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
        aggregate_1D = active_data.calc_time_aggregate_1D(integration_time="1D")

def update_active_data(widget_name):
    """Updates the active_data object with the settings from the widgets.

    Args:
        widget_name (str): A name which the function will use to specify which widget is being updated.
    """

    logger.debug(
        "Updating active data. Invoked through the " + widget_name.strip() + " widget."
    )  # Log event of updating active data.

    global active_data
    global data_file_name
    global selection_interval
    global initial_datetime
    global final_datetime
    global datetime_range_picker
    global dataframe_explorer_widget

    if len(list(data_file_name)) > 0:
        logger.debug("Updating active data object..")

        # load widget settings
        conf_threshold = threshold_widget.value
        agg_interval = time_aggregate_mapping_2D[integration_time_widget.value]
        class_label = class_label_widget.value

        # Copy dataset to active data
        active_data = copy.deepcopy(dataset)

        # Filter
        active_data.filter(
            "confidence>=" + str(conf_threshold), inplace=True
        )  # Results are greater than or equal to.
        active_data.filter(
            'label_class=="' + class_label + '"', inplace=True
        )  # It seems to select something by default.

        # create data aggregates
        # calculate_1D_aggregates( active_data )
        # calculate_2D_aggregates( active_data, agg_interval)

        # reset time filter
        datetime_range_picker.value = (
            dataset.data["date"].min(),
            dataset.data["date"].max(),
        )
        dataframe_explorer_widget.selection = [0]
        # load_dataframe_explorer_widget(datetime_range_picker)

        # notification
        success_notification(
            "New settings have been successfully applied to the "
            + widget_name.strip()
            + "!"
        )


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

        calculate_1D_aggregates(active_data)

        # hist = hv.Histogram(df_weekly.hvplot.bar(x='time', y='days_above_midpoint')).opts(title='Days Above Midpoint',
        #                                                                                  xformatter=formatter,
        #                                                                                  width=700)
        # to fix with date format, check this => https://discourse.holoviz.org/t/workaround-for-date-based-histogram-tick-labels/788

        dateformatter = DatetimeTickFormatter(days="%d %B %Y")
        plot = aggregate_1D.hvplot(
            # kind='step',
            kind="bar",
            tools=["tap"],  # , 'box_select', 'lasso_select'],
            # active_tools = ['tap'],
            width=900,
            height=600,
            rot=70,
            # xformatter=dateformatter,
            title="Daily detections",
            xlabel="Date",
            ylabel="Detections",
            grid=True,
            fontsize={"title": 10, "xticks": 10, "yticks": 10},
        ).opts(active_tools=["wheel_zoom"], nonselection_alpha=0.5)

        # plot = hv.Histogram(
        #     aggregate_1D.hvplot(
        #             #kind='step',
        #             kind='bar',
        #             tools=['tap'],#, 'box_select', 'lasso_select'],
        #             #active_tools = ['tap'],
        #             #width=900,
        #             #height=600,
        #             #rot=70,
        #     )).opts(
        #     title='Daily detections',
        #     xlabel='Date',
        #     ylabel='Detections',
        #     xformatter=dateformatter,
        #     width=900,
        #     height=600,
        #     #active_tools=['tap'],
        # )

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
            print("s")

        print(color_map_widget_plot2D)
        image_plot = aggregate_2D.hvplot.heatmap(
            x="columns",
            y="index",
            title="Hourly detections",
            xlabel="Date",
            ylabel="Hour of the day",
            selection_color="red",
            # cmap ='rainbow',
            cmap=color_map_widget_plot2D.name,
            # cmap = color_map_widget_plot2D,
            xaxis="bottom",
            # xformatter=dateformatter,
            rot=70,
            width=900,
            height=500,
        ).opts(
            fontsize={"title": 10, "xticks": 10, "yticks": 10},
            tools=["tap", "hover"],
            responsive=True,
            nonselection_alpha=0.5,
            selection_alpha=1,
            # autorange="y",
        )
        heatmap_tap.source = (
            image_plot  # Set the source of the heatmap tap object to the image plot.
        )

        return image_plot  # Return the image plot.


def find_audio_files(date_query, audio_files, bin_duration_sec=3600):
    """_summary_

    Args:
        date_query (_type_): _description_
        audio_files (_type_): _description_
        bin_duration_sec (int, optional): _description_. Defaults to 3600.

    Returns:
        _type_: _description_
    """
    logger.debug("Finding audio files..")
    start_time = date_query
    end_time = start_time + np.timedelta64(bin_duration_sec, "s")
    files_list = audio_files[
        (audio_files["start_date"] > start_time)
        & (audio_files["start_date"] < end_time)
    ]
    return list(files_list["file_name"].values)


## 1D plot functionalities


# lineplot_tap = hv.streams.Tap(x=0,y=0)
def get_lineplot_tap_date():
    """_summary_

    Returns:
        _type_: _description_
    """
    logger.debug("Getting lineplot tap dates..")
    lineplot_tap_date = pd.Series(lineplot_tap.x).round("h")
    return lineplot_tap_date.values[0]


def get_files_dates(indir, file_ext=".wav"):
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
        if os.path.isfile(os.path.join(indir, file)):  # if file exists
            _, ext = os.path.splitext(file)
            if ext == file_ext:  # list audio files only
                files_name.append(file)
    # retrieve dates from file names
    files_date = filename_to_datetime(files_name)
    files_list = pd.DataFrame({"file_name": files_name, "start_date": files_date})
    return files_list


def callback_lineplot_selection(*events):
    """_summary_"""
    logger.debug(*events)  # Log events.
    for event in events:  # For each event.
        if (event.name == "x") or (
            event.name == "y"
        ):  # If the event is an x or y event.
            if event.new:  # If the event is new.
                logger.debug(event.new.x)  # Log the new x value.
                audio_files_multi_select.options = find_audio_files(
                    get_lineplot_tap_date(), audio_files
                )  # Set the options of the audio_files_multi_select object to the list of audio files.
                if audio_files_multi_select.options:  # If there are audio files.
                    audio_files_multi_select.value = [
                        audio_files_multi_select.options[0]
                    ]
                    # selection_multi_select.name = 'Selected points (' + str(len(selection_multi_select.options)) + ')'


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
    try:
        selected_year = (
            str(events[0][2].x).split("T")[0].split("-")[0]
        )  # This will happen when histogram cell is clicked.
        selected_month = str(events[0][2].x).split("T")[0].split("-")[1]
        selected_day = str(events[0][2].x).split("T")[0].split("-")[2]

        selected_hour = str(events[0][2].y).split(".")[0]
        selected_minute = str(events[0][2].y).split(".")[1]
        base_ten_minute = float("0." + str(events[0][2].y).split(".")[1])
        base_ten_time = float(selected_hour + "." + selected_minute)

        logger.debug("selectied hour : " + str(selected_hour))

        if len(selected_hour.split("-")) > 1:  # Negative.
            if int(selected_hour) == 0:
                if float(base_ten_minute) < 0.5:  # Bottom of the zeroth cell.
                    selection_time_initial = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        0,
                        0,
                    )
                    selection_time_final = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        59,
                        59,
                        999999,
                    )

        if len(selected_hour.split("-")) == 1:  # Positive or Zero.
            if int(selected_hour) == 0:
                if float(base_ten_minute) < 0.5:  # Top of the zeroth cell.
                    selection_time_initial = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        0,
                        0,
                    )
                    selection_time_final = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        59,
                        59,
                        999999,
                    )

                if float(base_ten_minute) >= 0.5:  # Bottom of first cell.
                    selection_time_initial = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour) + 1,
                        0,
                        0,
                    )
                    selection_time_final = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour) + 1,
                        59,
                        59,
                        999999,
                    )

            elif int(selected_hour) == 23:
                if float(base_ten_minute) < 0.5:  # Bottom of selected_hour cell.
                    selection_time_initial = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        0,
                        0,
                    )
                    selection_time_final = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        59,
                        59,
                        999999,
                    )

                if float(base_ten_minute) >= 0.5:  # Bottom of cell above.
                    pass  # No cell is clicked

            else:
                if float(base_ten_minute) < 0.5:  # Bottom of selected_hour cell.
                    selection_time_initial = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        0,
                        0,
                    )
                    selection_time_final = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour),
                        59,
                        59,
                        999999,
                    )

                if float(base_ten_minute) >= 0.5:  # Bottom of cell above.
                    selection_time_initial = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour) + 1,
                        0,
                        0,
                    )
                    selection_time_final = datetime.datetime(
                        int(selected_year),
                        int(selected_month),
                        int(selected_day),
                        int(selected_hour) + 1,
                        59,
                        59,
                        999999,
                    )

        logger.debug("selection_time_initial : " + str(selection_time_initial))
        logger.debug("selection_time_final : " + str(selection_time_final))

        selection_interval = (selection_time_initial, selection_time_final)
        initial_datetime = selection_time_initial.strftime("%Y-%m-%d %H:%M:%S.%f")
        final_datetime = selection_time_final.strftime("%Y-%m-%d %H:%M:%S.%f")

        logger.debug("datetime_interval : " + str(selection_interval))

        datetime_range_picker.value = selection_interval
    except:
        logger.error("Please click inside the heatmap. This is a patch made for soundscope.")

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

    try:
        logger.debug(events)
        # Define day selected. Since bars are center on each need to adjust teh selection if user click on the left side
        # (i.e. first half) of the bar
        if pd.to_datetime(events[0][2].x).hour > 12:
            selection_time_initial = pd.to_datetime(events[0][2].x).date() + pd.Timedelta(days=1)
        else:
            selection_time_initial = pd.to_datetime(events[0][2].x).date()
        selection_time_final = selection_time_initial + pd.Timedelta(days=1)
        logger.debug( "selection_time_initial : " + str(selection_time_initial) )
        logger.debug( "selection_time_final : " + str(selection_time_final) )
        selection_interval = (selection_time_initial, selection_time_final)
        initial_datetime = selection_time_initial.strftime("%Y-%m-%d %H:%M:%S.%f")
        final_datetime = selection_time_final.strftime("%Y-%m-%d %H:%M:%S.%f")
        datetime_range_picker.value = selection_interval
    except:
        pass

def show_time_zone_configuration_modal(event):
    template.open_modal()

def close_time_zone_configuration_modal(event):
    global data_file_name
    global recordings_timezone
    global analysis_timezone

    # get time zones values as global variables
    recordings_timezone = timezone_audio_recording_select.value
    analysis_timezone = timezone_analysis_recording_select.value

    load_dataset(
        data_file_name
    )  # Load the dataset object with the .nc file.
    update_active_data("Initial data load event complete!")  # Update the active data object with the settings from the widgets.
    show_datetime_range_picker()  # Show the datetime range slider.
    # load_dataframe_explorer_widget(class_label_widget, threshold_widget, datetime_range_picker) # Load the dataframe explorer widget with the active_data object.

    # Close the modal object from panel template object.

    # TODO : Add the pleliminary time zone selection widget modal code here.
    # Show the time zone configuration modal.
    
    template.close_modal()

def show_save_file_dialog(filename=None, extension=None):
    """This function just opens the file explorer widget implemented as a panel modal.

    Args:
        event (_type_): _description_
    """
    settings_widgetbox.disabled = False
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)

    # Ensure the extension starts with a dot
    if extension and not extension.startswith("."):
        extension = f".{extension}"

    outfilename = tk.filedialog.asksaveasfilename(
        confirmoverwrite=True,
        initialfile=filename,
        defaultextension=extension,  # Automatically appends the extension
        filetypes=[(f"{extension.upper()} Files", f"*{extension}"), ("All Files", "*.*")],
    )
    return outfilename

def show_select_dir_dialog():
    """This function just opens the directory explorer widget implemented as a panel modal.

    Args:
        event (_type_): _description_
    """
    settings_widgetbox.disabled = False
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)

    outdirname = tk.filedialog.askdirectory()
    return outdirname

def show_file_selector(event):
    """This function just opens the file explorer widget implemented as a panel modal.

    Args:
        event (_type_): _description_
    """
    # logger.debug(event) # Log event.
    global data_file_name
    global datetime_range_picker  # Declare datetime_range_picker as a global so it can handle the datetime_range_picker object.
    global dataset  # Declare dataset as a global so it can handle the dataset object.
    global dataframe_explorer_widget_locked

    settings_widgetbox.disabled = False
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    data_file_name = tk.filedialog.askopenfilename(multiple=True)
    data_file_name = list(data_file_name)

    logger.debug(
        "A .nc file selection event has taken place."
    )  # Log event of file selection.

    if len(data_file_name) > 1:  # If more than one file is selected.
        logger.warning(
            "Multiple files selected. Please select only one .nc file"
        )  # Log warning.

    else:  # If only one file is selected.
        if len(data_file_name) > 0:
            data_file_name = str(
                data_file_name[0]
            )  # Assign the path of the .nc file to the global variable.
            print(data_file_name)
            file_extension = data_file_name.split(".")[
                -1
            ]  # Get the file extension of the selected file.

            if file_extension == "nc":  # If the file extension is .nc then continue.
                # template.close_modal() # Close the modal object from panel template object.

                logger.info(
                    "Loading the selected file(s) : " + data_file_name
                )  # Log the file path.
                dataframe_explorer_widget_locked = False

                show_time_zone_configuration_modal(event)
            else:
                logger.warning(
                    "The data format of the file selected is not supported. Please select a .nc file."
                )  # Log warning.

            logger.debug(
                "Loading date range picker..."
            )  # Log event of loading the date range slider.

            if (
                "date" in active_data.data.columns
            ):  # If the date column is in the active_data object.
                datetime_range_picker.value = (
                    dataset.data["date"].min(),
                    dataset.data["date"].max(),
                )


def display_welome_picture():
    global spectrogram_plot_pane
    import matplotlib.image as mpimg
    # import matplotlib.pyplot as plt

    img = mpimg.imread("images/SoundScopeWelcome.png")
    # imgplot = plt.imshow(img)

    # fig, ax = graph.show(display=False)  # Create a figure and axes object.
    # fig.set_size_inches(14, 8)  # Set the size of the figure.
    fig, ax = plt.subplots()
    ax.imshow(img, aspect="1.5")
    ax.axis("off")
    # ax.set_aspect('equal', adjustable='box')
    spectrogram_plot_pane.param.trigger("object")
    spectrogram_plot_pane.object = fig


# Spectrogram
#@pn.io.profile('Spectrogram', engine='snakeviz')
def spectrogram_plot(index=None):
    """The purpose of this function is to load the spectrogram plot pane. The plot depends on the index and play_sound widgets for interactivity.

    Args:
        index (int): The index represents the index of active_data.data.
        play_sound (boolean): There is a checkbox widget that is responsible for this boolean value.

    Returns:
        pn.pane.Matplotlib: Returns a Matplotlib pane object with the spectrogram plot.
    """
    logger.debug(
        "Loading spectrogram plot"
    )  # Log event of a spectrogram plot being loaded.
    start_time = time.perf_counter()  # start timer
    spectro_loading_spinner.value=True
    spectro_loading_spinner.name = 'Calculating spectrogram...'
    spectro_loading_spinner.visible=True
    global spectrogram_plot_pane  # Global variable for the spectrogram plot pane.
    global spectrogram_metadata_explorer
    global selected_sound
    global color_map_widget_spectrogram

    global frame_dur_widget
    global fft_dur_widget
    global step_dur_widget
    global time_buffer_widget
    global frequency_buffer_widget
    global dpi_widget

    global frequency_buffer_widget
    global frequency_min_widget
    global frequency_max_widget
    global frequency_bounds_mode_widget


    if (type(index) == int) and (
        dataset is not None
    ):

        frame = frame_dur_widget.value  # 3000
        nfft = fft_dur_widget.value  # 4096
        step = step_dur_widget.value  # 5
        window_type = "hann"
        time_buffer = time_buffer_widget.value
        frequency_buffer = frequency_buffer_widget.value
        data_selection = active_data.data.loc[index]
        data_selection_df = data_selection.to_frame()
        dpi = dpi_widget.value

        # initialize list of lists
        data = [
            ["date", str(data_selection_df.loc["date"][index])],
            ["uuid", str(data_selection_df.loc["uuid"][index])],
            ["from_detector", str(data_selection_df.loc["from_detector"][index])],
            ["software_name", str(data_selection_df.loc["software_name"][index])],
            ["software_version", str(data_selection_df.loc["software_version"][index])],
            ["operator_name", str(data_selection_df.loc["operator_name"][index])],
            ["UTC_offset", str(data_selection_df.loc["UTC_offset"][index])],
            ["entry_date", str(data_selection_df.loc["entry_date"][index])],
            ["audio_channel", str(data_selection_df.loc["audio_channel"][index])],
            ["audio_file_name", str(data_selection_df.loc["audio_file_name"][index])],
            ["audio_file_dir", str(data_selection_df.loc["audio_file_dir"][index])],
            [
                "audio_file_extension",
                str(data_selection_df.loc["audio_file_extension"][index]),
            ],
            [
                "audio_file_start_date",
                str(data_selection_df.loc["audio_file_start_date"][index]),
            ],
            [
                "audio_sampling_frequency",
                str(data_selection_df.loc["audio_sampling_frequency"][index]),
            ],
            ["audio_bit_depth", str(data_selection_df.loc["audio_bit_depth"][index])],
            [
                "mooring_platform_name",
                str(data_selection_df.loc["mooring_platform_name"][index]),
            ],
            ["recorder_type", str(data_selection_df.loc["recorder_type"][index])],
            ["recorder_SN", str(data_selection_df.loc["recorder_SN"][index])],
            ["hydrophone_model", str(data_selection_df.loc["hydrophone_model"][index])],
            ["hydrophone_SN", str(data_selection_df.loc["hydrophone_SN"][index])],
            ["hydrophone_depth", str(data_selection_df.loc["hydrophone_depth"][index])],
            ["location_name", str(data_selection_df.loc["location_name"][index])],
            ["location_lat", str(data_selection_df.loc["location_lat"][index])],
            ["location_lon", str(data_selection_df.loc["location_lon"][index])],
            [
                "location_water_depth",
                str(data_selection_df.loc["location_water_depth"][index]),
            ],
            ["deployment_ID", str(data_selection_df.loc["deployment_ID"][index])],
            ["frequency_min", str(data_selection_df.loc["frequency_min"][index])],
            ["frequency_max", str(data_selection_df.loc["frequency_max"][index])],
            ["time_min_offset", str(data_selection_df.loc["time_min_offset"][index])],
            ["time_max_offset", str(data_selection_df.loc["time_max_offset"][index])],
            ["time_min_date", str(data_selection_df.loc["time_min_date"][index])],
            ["time_max_date", str(data_selection_df.loc["time_max_date"][index])],
            ["duration", str(data_selection_df.loc["duration"][index])],
            ["label_class", str(data_selection_df.loc["label_class"][index])],
            ["label_subclass", str(data_selection_df.loc["label_subclass"][index])],
            ["confidence", str(data_selection_df.loc["confidence"][index])],
        ]

        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=["Label", "Data"])
        spectrogram_metadata_explorer.disabled = False
        spectrogram_metadata_explorer.layout = "fit_columns"
        try:
            spectrogram_metadata_explorer.value = df
        except:
            spectrogram_metadata_explorer.value = df
        wavfilename = os.path.join(
            data_selection.audio_file_dir,
            data_selection.audio_file_name + data_selection.audio_file_extension,
        )
        logger.debug(wavfilename)
        t1 = data_selection.time_min_offset - time_buffer
        t2 = data_selection.time_max_offset + time_buffer
        end_time = time.perf_counter() # end timer
        elapsed_time = end_time - start_time
        print(f"Elapsed time spectro init: {elapsed_time:.2f} seconds")

        # load audio data
        start_time = time.perf_counter() # start timer
        sound = Sound(wavfilename)
        selected_sound = sound
        if t1 < 0:
            t1 = 0
        if t2 > sound.file_duration_sec:
            t2 = sound.file_duration_sec
        sound.read(
            channel=data_selection.audio_channel - 1,
            chunk=[t1, t2],
            unit="sec",
            detrend=True,
        )
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Elapsed time load data: {elapsed_time:.2f} seconds")

        # decimate audio data
        start_time = time.perf_counter()  # start timer
        new_fs = 2.5*(data_selection.frequency_max + frequency_buffer)
        sound.decimate(new_fs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Elapsed time decinate data: {elapsed_time:.2f} seconds")

        # compute spectrogram
        start_time = time.perf_counter() # start timer
        spectro = Spectrogram(
            frame,
            window_type,
            nfft,
            step,
            sound.waveform_sampling_frequency,
            unit="sec",
        )
        spectro.compute(sound, dB=True, use_dask=False, dask_chunks=40)
        end_time = time.perf_counter() # end timer
        elapsed_time = end_time - start_time
        print(f"Elapsed time compute spectro: {elapsed_time:.2f} seconds")

        annot = Annotation()  # Create an Annotation object.
        annot.data = pd.concat(
            [
                annot.data,
                pd.DataFrame(
                    {
                        "time_min_offset": [time_buffer],
                        "time_max_offset": [time_buffer + data_selection.duration],
                        "frequency_min": [data_selection.frequency_min],
                        "frequency_max": [data_selection.frequency_max],
                        "duration": [data_selection.duration],
                    }
                ),
            ],
            ignore_index=True,
        )  # Concatenate the Annotation object with a pandas dataframe object.

        # PLot spectrogram
        start_time = time.perf_counter() # start timer

        if frequency_bounds_mode_widget.value:  #  Adaptive mode
            frequency_buffer = frequency_buffer_widget.value
            fmax = data_selection.frequency_max + frequency_buffer
            fmin = data_selection.frequency_min - frequency_buffer
        else:  # Fixed mode
            fmax = frequency_max_widget.value
            fmin = frequency_min_widget.value
        if fmin < 0:
            fmin = 0

        graph = GrapherFactory(
            "SoundPlotter",
            title=str(index)
            + ": "
            + data_selection.label_class
            + " - "
            + data_selection.label_subclass,
            frequency_max=fmax,
            frequency_min=fmin,
        )  # Create a GrapherFactory object.
        graph.add_data(spectro)  # Add the spectrogram object to the graph object.
        graph.add_annotation(
            annot, panel=0, color="black", label="Detections"
        )  # Add the Annotation object to the graph object.
        graph.colormap = color_map_widget_spectrogram.value_name
        fig, ax = graph.show(display=False)
        end_time = time.perf_counter() # end timer
        elapsed_time = end_time - start_time
        print(f"Elapsed time create spectro plot: {elapsed_time:.2f} seconds")

        # Save spetro as png
        start_time = time.perf_counter() # start timer
        filename='selection_spectro' + '.jpg'
        rasterize_and_save(filename,[ax], fig=fig, dpi=dpi)
        # ax.set_rasterized(True)
        # ax.set_rasterization_zorder(0)
        # #plt.draw()
        # fig.savefig(
        #     filename,
        #     transparent=False,
        #     bbox_inches="tight",
        #     dpi=100,
        # )
        #fig.canvas.draw()
        #image = np.array(fig.canvas.renderer.buffer_rgba())
        #cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGBA2BGR))
        end_time = time.perf_counter() # end timer
        elapsed_time = end_time - start_time
        print(f"Elapsed time saving spectro plot to png: {elapsed_time:.2f} seconds")

        #graph.to_file('test' + ".png")
        #fig, ax = graph.show(display=False)  # Create a figure and axes object.
        #fig.set_size_inches(14, 8)  # Set the size of the figure.
        # # debug
        # end_time = time.perf_counter()
        # elapsed_time = end_time - start_time
        # print(f"Elapsed time create spectro plot: {elapsed_time:.2f} seconds")

        # Display spectro in UI
        start_time = time.perf_counter() # start timer
        spectrogram_plot_pane.object = 'selection_spectro.jpg'
        spectrogram_plot_pane.param.trigger("object")
        end_time = time.perf_counter() # end timer
        elapsed_time = end_time - start_time
        print(f"Elapsed time display spectro: {elapsed_time:.2f} seconds")
        spectro_loading_spinner.value = False
        spectro_loading_spinner.name = ''
        spectro_loading_spinner.visible=False

    else:
        pass
        # spectrogram_plot_pane.param.trigger("object")
        # spectrogram_plot_pane.object = test_matplotlib()
        # return
        spectro_loading_spinner.value = False
        spectro_loading_spinner.name = ''
        spectro_loading_spinner.visible=False

def test_matplotlib():
    df = pd.DataFrame({"a": [0, 0, 1, 1], "b": [0, 1, 3, 2]})
    s = df[df["a"] == 1]["b"]
    fig, ax = plt.subplots()
    # fig.set_size_inches(14, 4) # Set the size of the figure.
    fig.tight_layout()
    s.plot(ax=ax)
    plt.close(fig)
    return fig


# @pn.depends()
def show_datetime_range_picker():
    """_summary_

    Returns:
        _type_: _description_
    """
    global datetime_range_picker  # Declare datetime_range_picker as a global so it can handle the datetime_range_picker object.
    logger.debug(
        "Loading date range picker..."
    )  # Log event of loading the date range slider.

    if (
        "date" in active_data.data.columns
    ):  # If the date column is in the active_data object.
        datetime_range_picker.value = (
            active_data.data["date"].min(),
            active_data.data["date"].max(),
        )
        return datetime_range_picker  # Return the DatetimeRangePicker object.

    else:
        return datetime_range_picker  # Return the DatetimeRangePicker object.


@pn.depends(class_label_widget, threshold_widget, datetime_range_picker)
def load_dataframe_explorer_widget(
    class_label_widget, threshold_widget, datetime_range_picker
):
    # @pn.depends(datetime_range_picker)
    # def load_dataframe_explorer_widget(datetime_range_picker):
    """The purpose of this function it to load the active_data Annotation dataframe element into the DataFrame explorer widget.

    Returns:
        pn.widgets.Tabulator: Returns a Tabulator DataFrame explorer widget with (updated) active_data available.
    """

    global active_data  # Declare active_data as a global so it can handle the active_data object.
    global dataset  # Declare dataset as a global so it can handle the dataset object.
    global data_file_name  # Declare data_file_name as a global so it can handle the data_file_name object.
    global dataframe_explorer_widget  # Declare dataframe_explorer_widget as a global so it can handle the dataframe_explorer_widget object.
    global selection_interval  # Declare selection_interval as a global so it can handle the selection_interval object.
    global initial_datetime
    global final_datetime
    global dataframe_explorer_widget_locked

    if len(list(data_file_name)) > 0:  # If the data_file_name object is not empty.
        logger.debug(
            "Loading 'active_data' dataframe explorer widget.."
        )  # Log event of loading the dataframe explorer widget.

        subselection = copy.deepcopy(active_data)

        if (not dataframe_explorer_widget_locked) & (datetime_range_picker is not None):
            initial_datetime = datetime_range_picker[0].strftime("%Y-%m-%d %H:%M:%S.%f")
            final_datetime = datetime_range_picker[1].strftime("%Y-%m-%d %H:%M:%S.%f")
            subselection.filter(
                'date >= "'
                + initial_datetime
                + '" and date <= "'
                + final_datetime
                + '"',
                inplace=True,
            )  # TODO : This is not right.
            # subselection = active_data.data[['date', 'confidence', 'label_class', 'audio_file_dir', 'audio_file_name', 'hydrophone_SN']]

            if not subselection.data.empty:
                # dataframe_explorer_widget.value = subselection.data[['date', 'confidence', 'label_class', 'audio_file_dir', 'audio_file_name', 'hydrophone_SN']]

                try:
                    dataframe_explorer_widget.value = subselection.data[
                        ["label_class", "date", "confidence"]
                    ]

                    return dataframe_explorer_widget

                except IndexError:
                    return None


def click_dataframe_explorer_widget(event=None):
    global color_map_widget_spectrogram

    try:
        if len(dataframe_explorer_widget.selection) == 0:
            dataframe_explorer_widget.selection = [0]

        selected_raw_index = int(
            dataframe_explorer_widget.value.iloc[
                dataframe_explorer_widget.selection[0]
            ].name
        )
        print(f"Index of the detection selected: {selected_raw_index}")
        print("s")
        spectrogram_plot(index=selected_raw_index)

    except IndexError:
        # dataframe_explorer_widget.selection = []
        return None

def save_hourly_csv_file(event=None):
    filename = show_save_file_dialog(filename='hourly_detection_summary.csv', extension='.csv')
    aggregate_1H = active_data.calc_time_aggregate_1D(integration_time='1H')
    start_time_an = aggregate_1H.index
    end_time_an = start_time_an + pd.Timedelta(1,unit='h')
    start_time_rec = start_time_an - pd.Timedelta(TZ_offset,unit='h')
    end_time_rec = start_time_rec + pd.Timedelta(1,unit='h')
    n_detections = list(aggregate_1H.values[:,0])

    # add time zones
    offset_an = pytz.FixedOffset(analysis_timezone * 60)
    offset_rec = pytz.FixedOffset(recordings_timezone * 60)
    start_time_an = start_time_an.tz_localize(offset_an)
    end_time_an = end_time_an.tz_localize(offset_an)
    start_time_rec = start_time_rec.tz_localize(offset_rec)
    end_time_rec = end_time_rec.tz_localize(offset_rec)

    df = pd.DataFrame({'Start time (recordings time zone)':start_time_rec,
                       'End time (recordings time zone)': end_time_rec,
                       'Start time (analysis time zone)': start_time_an,
                       'End time (analysis time zone)': end_time_an,
                       'Number of detections': n_detections,
                       })
    df["Manual_Review"] = ""
    df["Comments"] = ""
    preamble1 = f"SoundScope version: {__version__} \n"
    preamble2 = f"Originator: {os.getlogin()} \n"
    preamble3 = f"Creation date: {datetime.datetime.now().strftime('%Y%m%dT%H%M%S')} \n"
    preamble4 = f"Time zone of recordings: UTC{recordings_timezone} \n"
    preamble5 = f"Time zone of analysis: UTC{analysis_timezone} \n"
    preamble6 = f"Confidence threshold: {threshold_widget.value} \n"
    preamble7 = f"Class label: {class_label_widget.value} \n"
    preamble = preamble1+preamble2+preamble3+preamble4+preamble5+preamble6+preamble7
    with open(filename, 'w') as f:
        f.write(preamble)
        df.to_csv(f, date_format='%Y%m%dT%H%M%S%z',index=False,lineterminator='\n')
    success_notification("CSV file saved")

def save_daily_csv_file(event=None):
    filename = show_save_file_dialog(filename='daily_detection_summary.csv', extension='.csv')
    #aggregate_1H = active_data.calc_time_aggregate_1D(integration_time='1H')
    start_time_an = aggregate_1D.index
    end_time_an = start_time_an + pd.Timedelta(24,unit='h')
    start_time_rec = start_time_an - pd.Timedelta(TZ_offset,unit='h')
    end_time_rec = start_time_rec + pd.Timedelta(24,unit='h')
    n_detections = list(aggregate_1D.values[:,0])

    # add time zones
    offset_an = pytz.FixedOffset(analysis_timezone * 60)
    offset_rec = pytz.FixedOffset(recordings_timezone * 60)
    start_time_an = start_time_an.tz_localize(offset_an)
    end_time_an = end_time_an.tz_localize(offset_an)
    start_time_rec = start_time_rec.tz_localize(offset_rec)
    end_time_rec = end_time_rec.tz_localize(offset_rec)

    df = pd.DataFrame({'Start time (recordings time zone)':start_time_rec,
                       'End time (recordings time zone)': end_time_rec,
                       'Start time (analysis time zone)': start_time_an,
                       'End time (analysis time zone)': end_time_an,
                       'Number of detections': n_detections,
                       })
    df["Manual_Review"] = ""
    df["Comments"] = ""
    preamble1 = f"SoundScope version: {__version__} \n"
    preamble2 = f"Originator: {os.getlogin()} \n"
    preamble3 = f"Creation date: {datetime.datetime.now().strftime('%Y%m%dT%H%M%S')} \n"
    preamble4 = f"Time zone of recordings: UTC{recordings_timezone} \n"
    preamble5 = f"Time zone of analysis: UTC{analysis_timezone} \n"
    preamble6 = f"Confidence threshold: {threshold_widget.value} \n"
    preamble7 = f"Class label: {class_label_widget.value} \n"
    preamble = preamble1+preamble2+preamble3+preamble4+preamble5+preamble6+preamble7
    with open(filename, 'w') as f:
        f.write(preamble)
        df.to_csv(f, date_format='%Y%m%dT%H%M%S%z',index=False,lineterminator='\n')
    success_notification("CSV file saved")

def play_selected_sound(event):
    global selected_sound
    try:
        sd.play(
            selected_sound.waveform / max(selected_sound.waveform),
            selected_sound.waveform_sampling_frequency,
        )
    except NameError:
        pass
    else:
        pass

def download_selected_sound(event):
    #global selected_sound
    filename_tmp = class_label_widget.value + '_' + selected_sound.file_name + '_chan-' + str(selected_sound.channel_selected) + '_deltatime-' + str(
        round(selected_sound.waveform_start_sample / selected_sound.waveform_sampling_frequency, 3))+'.wav'
    filename = show_save_file_dialog(filename=filename_tmp, extension='.wav')
    selected_sound._waveform = selected_sound.waveform / max(selected_sound.waveform)
    selected_sound.write(filename)
    success_notification('Audio clip saved successfully')

def stop_selected_sound(event=None):
    try:
        sd.stop()
    except NameError:
        pass
    else:
        pass

def select_next_detec(event=None):
    selected = dataframe_explorer_widget.selection
    if selected:
        next_index = (selected[0] + 1) #% len(df)
    else:
        next_index = 0
    dataframe_explorer_widget.selection = [next_index]
    click_dataframe_explorer_widget()

def select_previous_detec(event=None):
    selected = dataframe_explorer_widget.selection
    if selected:
        next_index = (selected[0] - 1) #% len(df)
    else:
        next_index = 0
    dataframe_explorer_widget.selection = [next_index]
    click_dataframe_explorer_widget()


@pn.depends(class_label_widget, threshold_widget)
def load_detections(class_label_widget, threshold_widget):
    """The purpose of this function is to load the detections widget.
    These detections are filtered because they come through the active_data object.
    These detections are also ordered by confidence; Highest to lowest.

    Args:
        active_data (Annotation): Filtered dataset.
    """
    global active_data  # Declare active_data as a global so it can handle the active_data object.
    global detec_files_multi_select  # Declare detec_files_multi_select as a global so it can handle the detec_files_multi_select object.
    logger.debug(
        "Loading detection by ascending order.."
    )  # Log event of loading the detections widget.
    detec_list_index = list(
        active_data.data["confidence"].sort_values(ascending=False)
    )  # Create a list of detections sorted by confidence; Highest to lowest.

    detec_files_multi_select.options = detec_list_index  # Set the options of the detec_files_multi_select object to the list of detections sorted by confidence; Highest to lowest.
    detec_files_multi_select.value = [
        detec_files_multi_select.options[0]
    ]  # Set the value of the detec_files_multi_select object to the first detection in the list of detections sorted by confidence; Highest to lowest.
    detec_files_multi_select.name = (
        "Detections (" + str(len(active_data)) + ")"
    )  # Set detections label showing the quantity of detections per active_data.

def save_nc_file(event):
    #global selected_sound
    filename_tmp = data_file_name
    filename = show_save_file_dialog(filename=filename_tmp, extension='.nc')
    dataset.to_netcdf(filename)
    success_notification('File saved successfully')

def update_audio_path(event):
    global dataset
    global active_data
    dir = show_select_dir_dialog()
    dataset.insert_values(audio_file_dir=dir)
    active_data.insert_values(audio_file_dir=dir)
    success_notification('Audio path successfully updated')

watcher_heatmap = heatmap_tap.param.watch(
    callback_heatmap_selection, ["x", "y"], onlychanged=False
)  # Watcher for heatmap tap events.
# watcher_histogram = histogram_tap.param.watch(callback_histogram_selection, ['x','y'], onlychanged = False) # Watcher for heatmap tap events.

dataframe_explorer_widget.on_click(click_dataframe_explorer_widget)


watcher_lineplot = lineplot_tap.param.watch(
    callback_histogram_selection, ["x", "y"], onlychanged=False
)


# Panel Template
#  Adjust Modal window size
RAW_CSS = """
@media (min-width: 576px) {
  .modal-dialog {
    max-width: 600px;
  }
}
"""
timezone_img = pn.pane.Image("images/time-zone_con_by_awicon.png",width=220)
template = pn.template.BootstrapTemplate(
    title="SoundScope", logo="images/SoundScopeLogo.png", favicon="images/favicon.ico",raw_css=[RAW_CSS]
)  # Basic 'Bootstrap' template object for python3 Panel lib. Ref : https://panel.holoviz.org/reference/templates/Bootstrap.html

timezone_audio_recording_select = pn.widgets.Select(
    name="Recordings time zone", options={"Select time offset from UTC": False, "-12": -12, "-11": -11, "-10": -10, "-9": -9, "-8": -8, "-7": -7, "-6": -6, "-5": -5, "-4": -4, "-3": -3, "-2": -2, "-1": -1, "0": 0, "+1": 1, "+2": 2, "+3": 3, "+4": 4, "+5": 5, "+6": 6, "+7": 7, "+8": 8, "+9": 9, "+10": 10, "+11": 11, "+12": 12, "+13": 13, "+14": 14}, width=250, height=50, margin = 15, align='center'
)
timezone_analysis_recording_select = pn.widgets.Select(
        name="Analysis time zone", options={"Select time offset from UTC": False, "-12": -12, "-11": -11, "-10": -10, "-9": -9, "-8": -8, "-7": -7, "-6": -6, "-5": -5, "-4": -4, "-3": -3, "-2": -2, "-1": -1, "0": 0, "+1": 1, "+2": 2, "+3": 3, "+4": 4, "+5": 5, "+6": 6, "+7": 7, "+8": 8, "+9": 9, "+10": 10, "+11": 11, "+12": 12, "+13": 13, "+14": 14}, width=250, height=50, margin = 15, align='center'

)
modal_load_button = pn.widgets.Button(name="Ok", button_type="primary", width=250, height=40, margin = 17, align='center')
#template.modal.append("# Define time zones")
template.modal.append(
    pn.Column(
"<center> <font size='6'> <b> Define time zones </b> </font> </center>",
    pn.Row(
    timezone_img,
            pn.Column(
                timezone_audio_recording_select,
                timezone_analysis_recording_select,
                modal_load_button,
            ),
    ),
    )
)


# template.modal.append(
#     pn.Row(
#         timezone_img,
#         pn.WidgetBox(
#             pn.Column(
# "# Define time zones",
#
#             pn.Column(
#                 timezone_audio_recording_select,
#                 timezone_analysis_recording_select,
#                 modal_load_button,
#             ),
#         ),
#             align='center',
#             width=300,
#         ),
#     )
# )

modal_load_button.on_click(close_time_zone_configuration_modal)


select_file_button = pn.widgets.Button(
    name="Select file", button_type="primary", sizing_mode="stretch_width"
)  # This button is responsible for opening the file selector.
# play_sound_button = pn.widgets.Button(icon='player-play', name='Play', button_type='primary', icon_size='2em', width = 200, height = 50, margin = (30,10,10,75))
# stop_sound_button = pn.widgets.Button(icon='player-stop', name='Stop', button_type='primary', icon_size='2em', width = 200, height = 50, margin = (30,10,10,10))
play_sound_button = pn.widgets.Button(
    icon="player-play",
    name="Play",
    button_type="primary",
    icon_size="2em",
    width=50,
    height=50,
    sizing_mode='fixed',
)

stop_sound_button = pn.widgets.Button(
    icon="player-stop",
    name="Stop",
    button_type="primary",
    icon_size="2em",
    width=50,
    height=50,
)
previous_detec_button = pn.widgets.Button(
    icon="chevron-left",
    name="Previous",
    button_type="primary",
    icon_size="2em",
    width=75,
    height=50,
)
next_detec_button = pn.widgets.Button(
    icon="chevron-right",
    name="Next",
    button_type="primary",
    icon_size="2em",
    width=80,
    height=50,
)

download_sound_button = pn.widgets.Button(
    icon="download",
    name="Download",
    button_type="primary",
    icon_size="2em",
    width=80,
    height=50,
)

download_csv_hourly_button = pn.widgets.Button(
    icon="file-type-csv",
    button_style='outline',
    name="",
    button_type="light",
    align=('end','end'),
    icon_size="2em",
    width=20,
    #height=20,
)
download_csv_daily_button = pn.widgets.Button(
    icon="file-type-csv",
    button_style='outline',
    name="",
    button_type="light",
    align=('end','end'),
    icon_size="2em",
    width=20,
    #height=20,
)



# next_detec_button._id = 'my-button'  # Assign a unique ID

apply_spectro_settings_button = pn.widgets.Button(
    name="Apply", button_type="primary"
)  # This button is responsible for opening the file selector.

# Widget boxes
file_selection_label_widget = pn.widgets.StaticText(
    name="NetCDF file", value="Please select a file", sizing_mode="stretch_width"
)  # Text with file selected.
# openfile_widgetbox = pn.WidgetBox( file_selection_label_widget, select_file_button, margin = (10,10), sizing_mode = 'stretch_width' ) # Widget object from python3 panel library. This object is a container for file selection related widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html
openfile_widgetbox = pn.WidgetBox(
    file_selection_label_widget, select_file_button, sizing_mode="stretch_width"
)  # Widget object from python3 panel library. This object is a container for file selection related widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html
# filters_label_widget = pn.widgets.StaticText(name='Filters', value='', sizing_mode='stretch_width') # Text with file selected.
settings_widgetbox = pn.WidgetBox(
    class_label_widget,
    threshold_widget,
    disabled=False,
    margin=(10, 10),
    sizing_mode="stretch_width",
)  # Widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html
# spectro_settings_label_widget = pn.widgets.StaticText(name='Spectrogram settings', value='', sizing_mode='stretch_width') # Text with file selected.


resolution_settings_group = pn.Card(
    frame_dur_widget,
    fft_dur_widget,
    step_dur_widget,
    title="Resolution",
    sizing_mode="stretch_width",
    collapsible=False,
    header_background='#DEE2E6',
)

rendering_settings_group = pn.Card(
    dpi_widget,
    color_map_widget_spectrogram,
    title="Rendering",
    sizing_mode="stretch_width",
    collapsible=False,
    header_background='#DEE2E6',
)

limits_settings_group = pn.Card(
    time_buffer_widget,
    pn.Row(frequency_bounds_mode_widget, frequency_mode_status_widget),
    frequency_min_widget,  # Add fixed min frequency
    frequency_max_widget,  # Add fixed max frequency
    frequency_buffer_widget,  # Keep existing adaptive buffer
    title="Boundaries",
    sizing_mode="stretch_width",
    collapsible=False,
    header_background='#DEE2E6',
)

spectro_settings_widgetbox = pn.WidgetBox(
    resolution_settings_group,
    limits_settings_group,
    rendering_settings_group,
    apply_spectro_settings_button,
    disabled=False,
    margin=(10, 10),
    sizing_mode="stretch_width",
)  # Widget object from python3 panel library. This object is a container for settings widgets. Ref : https://panel.holoviz.org/reference/layouts/WidgetBox.html
# playback_widgetbox = pn.WidgetBox(play_sound_button, stop_sound_button, sizing_mode = 'stretch_width' )

# accordion = pn.Accordion(('Filters',settings_widgetbox),('Spectrogram settings',spectro_settings_widgetbox),('Playback',playback_widgetbox))
accordion = pn.Accordion(
    ("Filters", settings_widgetbox),
    ("Spectrogram settings", spectro_settings_widgetbox),
)

detec_files_multi_select = pn.widgets.MultiSelect(
    name="Detections", value=[], options=[], size=8
)
file_name_markdown = pn.pane.Markdown("", width=100)


# menu bar
file_items = ["Open file", "Save as"]
edit_items = ["Change audio path"]
menu_file_widget = pn.widgets.MenuButton(name="File", icon="file", items=file_items, height=40, width=90, button_style='outline', button_type="light", margin=0)
menu_edit_widget = pn.widgets.MenuButton(name="Edit", icon='edit', items=edit_items, height=40, width=90, button_style='outline', button_type="light", margin=0)
top_menu = pn.Row(
    menu_file_widget,
    menu_edit_widget,
    styles={"border-bottom": "1px solid black"}
    )

def top_menu_file_actions(item):
    if menu_file_widget.clicked == 'Open file':
        show_file_selector(event)
    elif menu_file_widget.clicked == 'Save as':
        save_nc_file(event)

def top_menu_edit_actions(item):
    if menu_edit_widget.clicked == 'Change audio path':
        update_audio_path(event)

menu_file_widget.on_click(top_menu_file_actions)
menu_edit_widget.on_click(top_menu_edit_actions)



#  ## Keyboard shortcuts  #########################################
# #def handle_shortcut(event: DataEvent):
# def handle_shortcut(event):
#     if event.data == "save":
#         print("Save shortcut pressed!")
#     elif event.data == "print":
#         print("Print shortcut pressed!")
#
# shortcuts = [
#     KeyboardShortcut(name="save", key="s", ctrlKey=True),
#     KeyboardShortcut(name="print", key="p", ctrlKey=True),
# ]
#
# shortcuts_component = KeyboardShortcuts(shortcuts=shortcuts)
# shortcuts_component.on_msg(handle_shortcut)

################################################################

#analysis_timezone_text = pn.pane.Markdown(f"Time zone of analysis: UTC {analysis_timezone} ", sizing_mode='stretch_width')
# Side panel
template.sidebar.append(
    pn.Column(top_menu,accordion)
    #pn.Column(top_menu,openfile_widgetbox, accordion)
)  # Appends the openfile_widgetbox and settings_widgetbox to the sidebar object from panel template object.
# template.sidebar.append( pn.Column(file_selection_label_widget,select_file_button,accordion ) ) # Appends the openfile_widgetbox and settings_widgetbox to the sidebar object from panel template object.

# Main page
top_panel_tabs = pn.Tabs(
    (
        "Hourly Detections",
        pn.WidgetBox(
            pn.Column(
                #pn.Row(color_map_widget_plot2D, integration_time_widget, download_csv_hourly_button), create_2D_plot
                pn.Row(download_csv_hourly_button,color_map_widget_plot2D,analysis_timezone_text,align=('end','end')), create_2D_plot
            ),
            disabled=False,
            margin=(10, 10),
            sizing_mode="stretch_width",
        ),
    )
)
top_panel_tabs.append(
    (
        "Daily Detections",
        pn.WidgetBox(
            pn.Column(
                pn.Row( download_csv_daily_button,analysis_timezone_text), create_1D_plot
            ),
            disabled=False,
            margin=(10, 10),
            sizing_mode="stretch_width",
        ),
    )
)  # This is one place active data is updated.
top_panel_tabs.append(("Custom Dates Selection", datetime_range_picker))

spectrogram_tabs = pn.Tabs(
    (
        "Spectrogram",
        pn.WidgetBox(
            pn.Column(
                spectrogram_plot_pane, pn.Row(play_sound_button, stop_sound_button,download_sound_button,previous_detec_button,next_detec_button, pn.Spacer(styles=dict(background='white'), width=50),spectro_loading_spinner)
            ),
            disabled=False,
            margin=(10, 10),
        ),
    )
)
spectrogram_tabs.append(
    (
        "Metadata",
        pn.WidgetBox(
            spectrogram_metadata_explorer,
            disabled=True,
            margin=(10, 10),
            sizing_mode="stretch_width",
        ),
    )
)

# bottom_panel = pn.Row(spectrogram_tabs,pn.WidgetBox( load_dataframe_explorer_widget, disabled = False, margin=(45,10,10,10), sizing_mode = 'stretch_both' ))
bottom_panel = pn.Row(
    spectrogram_tabs,
    pn.WidgetBox(
        load_dataframe_explorer_widget,
        disabled=False,
        margin=(45, 10, 10, 10),
        width=515,
    ),
)

# for javascript code
# Create an HTML pane to inject the JavaScript
#js_pane = pn.pane.HTML(js_code, width=0, height=0, sizing_mode='fixed')

template.main.append(pn.Column(top_panel_tabs, bottom_panel))
#keyboard_shortcuts = KeyboardShortcutHandler()
#template.main.append(pn.Column(top_panel_tabs, bottom_panel, keyboard_shortcuts.get_widget()))
#eetemplate.main.append(shortcuts)

# Modal
download_csv_hourly_button.on_click(save_hourly_csv_file)  #
download_csv_daily_button.on_click(save_daily_csv_file)  #

select_file_button.on_click(
    show_file_selector
)  # Defines the action of the select_file_button object which is a file selection module.
play_sound_button.on_click(play_selected_sound)
# load_button.on_click( get_selection ) #
stop_sound_button.on_click(stop_selected_sound)
download_sound_button.on_click(download_selected_sound)
apply_spectro_settings_button.on_click(click_dataframe_explorer_widget)

next_detec_button.on_click(select_next_detec)
previous_detec_button.on_click(select_previous_detec)

#next_detec_button.js_on_load(code=js_code)

#display_welome_picture()

# Serve Application
logger.debug("Serving Panel Template..")
template.servable()
template.show(port=5006, threaded=True, websocket_origin="localhost:5006")

