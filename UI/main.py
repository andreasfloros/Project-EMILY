import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import font
import os
import sys

# pad all strings to the same length so that the entries etc align (require equal spacing for every character)
def pad_to_max(string, zero = False):
    chars_to_add = 24 - len(string) #len("Expected duration (s): 0") - len(string)
    padded_string = string
    for _ in range(chars_to_add - 1):
        padded_string += " "
    if zero == True:
        padded_string += "0"
    else:
        padded_string += " "
    return padded_string


class main_app():

    def __init__(self, root):
        self.images = {"browse_button" : tk.PhotoImage(file = os.path.join(wd,"Images","browse_button.png"))}
        self.background_frame = ttk.Frame(root)
        self.setup_title_frame()
        self.setup_selection_area()
        self.background_frame.pack(expand = True, fill = tk.BOTH)


    def setup_selection_area(self):
        self.selection_area_frame_label = ttk.LabelFrame(self.background_frame, text = "Select dataset and processing")

        self.setup_browse_frame()
        self.setup_processing_method_frame()
        self.setup_sample_rate_frame()
        self.setup_expected_duration_frame()
        self.setup_window_size_frame()
        self.setup_window_stride_frame()

        self.selection_area_frame_label.pack(anchor = "nw", expand = True)
        self.processing_method_combobox.current(0)
        self.sample_rate_combobox.current(0)
        self.expected_duration_scale.set(1)


    def setup_title_frame(self):
        self.title_frame = ttk.Frame(self.background_frame)
        self.title_label = ttk.Label(self.title_frame, text = "ML Platform for Arduino Nano 33 BLE Sense")
        self.title_frame.pack(expand = False, fill = tk.X, side = tk.TOP)
        self.title_label.pack(anchor = tk.CENTER)

    def setup_browse_frame(self):
        self.browse_frame = ttk.Frame(self.selection_area_frame_label)
        self.browse_label = ttk.Label(self.browse_frame, text = pad_to_max("Browse dataset:"))
        self.browse_button = ttk.Button(self.browse_frame, image = self.images["browse_button"], command = self.browse_button_callback)
        self.browse_entry = ttk.Entry(self.browse_frame)
        self.browse_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.browse_label.pack(side = tk.LEFT)
        self.browse_entry.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.browse_button.pack(side = tk.LEFT)


    def setup_processing_method_frame(self):
        self.processing_method_frame = ttk.Frame(self.selection_area_frame_label)
        self.processing_method_label = ttk.Label(self.processing_method_frame, text = pad_to_max("Processing method:"))
        self.processing_method_combobox = ttk.Combobox(self.processing_method_frame, state = "readonly", values = ("STFT", "MFCC"))
        self.processing_method_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.processing_method_label.pack(side = tk.LEFT)
        self.processing_method_combobox.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def setup_sample_rate_frame(self):
        self.sample_rate_frame = ttk.Frame(self.selection_area_frame_label)
        self.sample_rate_label = ttk.Label(self.sample_rate_frame, text = pad_to_max("Sample rate:"))
        self.sample_rate_combobox = ttk.Combobox(self.sample_rate_frame, state = "readonly", values = ("16kHz", "44.1kHz"))
        self.sample_rate_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.sample_rate_label.pack(side = tk.LEFT)
        self.sample_rate_combobox.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def setup_expected_duration_frame(self):
        self.expected_duration_frame = ttk.Frame(self.selection_area_frame_label)
        self.expected_duration_label = ttk.Label(self.expected_duration_frame, text = "Expected duration (s): 0")
        self.expected_duration_scale = ttk.Scale(self.expected_duration_frame, from_ = 0, to = 2, command = self.expected_duration_scale_callback)
        self.expected_duration_label_end = ttk.Label(self.expected_duration_frame, text = "2.0")
        self.expected_duration_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.expected_duration_label.pack(side = tk.LEFT)
        self.expected_duration_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.expected_duration_label_end.pack(side = tk.LEFT)


    def setup_window_size_frame(self):
        self.window_size_frame = ttk.Frame(self.selection_area_frame_label)
        self.window_size_label = ttk.Label(self.window_size_frame, text = pad_to_max("Window size (s):", True))
        self.window_size_scale = ttk.Scale(self.window_size_frame, from_ = 0, to = 1)
        self.window_size_label_end = ttk.Label(self.window_size_frame, text = "1")
        self.window_size_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.window_size_label.pack(side = tk.LEFT)
        self.window_size_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.window_size_label_end.pack(side = tk.LEFT)

    def setup_window_stride_frame(self):
        self.window_stride_frame = ttk.Frame(self.selection_area_frame_label)
        self.window_stride_label = ttk.Label(self.window_stride_frame, text = pad_to_max("Window stride (s):", True))
        self.window_stride_scale = ttk.Scale(self.window_stride_frame, from_ = 0, to = 1)
        self.window_stride_label_end = ttk.Label(self.window_stride_frame, text = "1")
        self.window_stride_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.window_stride_label.pack(side = tk.LEFT)
        self.window_stride_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.window_stride_label_end.pack(side = tk.LEFT)


    def browse_button_callback(self):
        data = filedialog.askdirectory()
        self.browse_entry.delete(0, tk.END)
        self.browse_entry.insert(0, data)

    def expected_duration_scale_callback(self, _):
        new_end = self.expected_duration_scale.get()
        self.window_size_scale.config(to = new_end)
        self.window_size_label_end.config(text = "{:.1f}".format(new_end))
        self.window_stride_scale.config(to = new_end)
        self.window_stride_label_end.config(text = "{:.1f}".format(new_end))
        self.window_size_scale.set(new_end)
        self.window_stride_scale.set(new_end)

    

if __name__ == "__main__":
    # wd is sys._MEIPASS for exe
    try:
        wd = sys._MEIPASS
    except AttributeError:
        wd = os.getcwd()
    root = tk.Tk()
    # change font to monospace
    font.nametofont("TkDefaultFont").config(family = "consolas")
    #root.option_add("*Font", font.nametofont("TkFixedFont"))
    root.option_add("*TCombobox.Justify", "center")
    root.option_add("*TCombobox*Listbox.Justify", "center")
    root.title("ARM - ML - Embedded")
    root.geometry("720x720")
    app = main_app(root) 

    root.mainloop()
