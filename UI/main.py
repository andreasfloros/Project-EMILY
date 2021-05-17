import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import font
import os
import sys
#import math

# pad all strings to the same length so that the entries etc align (require equal spacing for every character)
def pad_to_max(string, end_txt = "", free = 0):
    chars_to_add = 42 - len(string) - free
    end_txt_length = len(end_txt)
    padded_string = string
    for _ in range(chars_to_add - end_txt_length):
        padded_string += " "
    padded_string += end_txt
    return padded_string


class main_app():

    def __init__(self, root):
        self.images = {"browse_button" : tk.PhotoImage(file = os.path.join(wd,"Images","browse_button.png")),
                       "next_button" : tk.PhotoImage(file = os.path.join(wd,"Images","next_button.png")),
                       "back_button" : tk.PhotoImage(file = os.path.join(wd,"Images","back_button.png")),
                       "globe_button" : tk.PhotoImage(file = os.path.join(wd,"Images","globe_button.png")),
                       "arduino_button" : tk.PhotoImage(file = os.path.join(wd,"Images","arduino_button.png"))}
        ttk.Style(root).configure(".", background = "#00A3A3", foreground = "#ffffff")
        ttk.Style(root).configure("TCombobox", foreground = "#000000")
        ttk.Style(root).configure("TEntry", foreground = "#000000")
        ttk.Style(root).configure("menu.TFrame", background = "#007575")
        ttk.Style(root).configure("menu.TLabel", background = "#007575")
        ttk.Style(root).configure("menu.TButton", background = "#007575")
        self.background_frame = ttk.Frame(root)
        self.setup_menu_frame()
        self.setup_selection_page()
        self.setup_training_page()
        self.setup_arduino_page()
        self.background_frame.pack(expand = True, fill = tk.BOTH)

    def setup_menu_frame(self):
        self.current_page = "selection_page"
        self.menu_frame = ttk.Frame(self.background_frame, style = "menu.TFrame")
        self.menu_label = ttk.Label(self.menu_frame, text = "Select dataset and processing", style = "menu.TLabel")
        self.menu_next_button = ttk.Button(self.menu_frame, image = self.images["next_button"], style = "menu.TButton", command = self.load_next_page)
        self.menu_back_button = ttk.Button(self.menu_frame, image = self.images["arduino_button"], style = "menu.TButton", command = self.load_previous_page)
        self.menu_frame.pack(expand = False, fill = tk.X, side = tk.TOP)
        self.menu_next_button.pack(side = tk.RIGHT)
        self.menu_back_button.pack(side = tk.LEFT)
        self.menu_label.pack(anchor = tk.CENTER)

# SELECTION PAGE

    def setup_selection_page(self):
        self.selection_page_frame = ttk.Frame(self.background_frame)

        self.setup_browse_dataset_frame()
        self.setup_processing_method_parent_frame()
        self.setup_sample_rate_frame()
        self.setup_expected_duration_frame()
        self.setup_window_size_frame()
        self.setup_window_stride_frame()

        self.selection_page_frame.pack(fill = tk.BOTH , expand = True)
        self.processing_method_combobox.current(0)
        self.sample_rate_combobox.current(0)

    def setup_browse_dataset_frame(self):
        self.browse_dataset_frame = ttk.Frame(self.selection_page_frame)
        self.browse_dataset_label = ttk.Label(self.browse_dataset_frame, text = pad_to_max("Browse dataset:", free = 4))
        self.browse_dataset_mode = "local"
        self.browse_dataset_button = ttk.Button(self.browse_dataset_frame, image = self.images["browse_button"], command = self.browse_dataset_button_callback)
        self.browse_dataset_button.bind("<Button-3>", self.browse_dataset_button_change_mode)
        self.browse_dataset_entry = ttk.Entry(self.browse_dataset_frame)
        self.browse_dataset_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.browse_dataset_label.pack(side = tk.LEFT)
        self.browse_dataset_entry.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.browse_dataset_button.pack(side = tk.LEFT)


    def setup_processing_method_parent_frame(self):
        self.processing_method_parent_frame = ttk.Frame(self.selection_page_frame)
        self.setup_processing_method_frame()
        self.setup_mfcc_coefficients()
        self.processing_method_parent_frame.pack(expand = True, fill = tk.X, side = tk.TOP)

    def setup_processing_method_frame(self):
        self.processing_method_frame = ttk.Frame(self.processing_method_parent_frame)
        self.processing_method_label = ttk.Label(self.processing_method_frame, text = pad_to_max("Processing method:", free = 4))
        self.processing_method_combobox = ttk.Combobox(self.processing_method_frame, state = "readonly", values = ("STFT", "MFCC"))
        self.processing_method_combobox.bind("<<ComboboxSelected>>", self.processing_method_combobox_callback)
        self.processing_method_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.processing_method_label.pack(side = tk.LEFT)
        self.processing_method_combobox.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def setup_mfcc_coefficients(self):
        self.mfcc_coefficients_frame = ttk.Frame(self.processing_method_parent_frame)
        self.mfcc_coefficients_label = ttk.Label(self.mfcc_coefficients_frame, text = pad_to_max("MFCC Coefficients: 13", "1", free = 3))
        self.mfcc_coefficients_scale = ttk.Scale(self.mfcc_coefficients_frame, from_ = 1, to = 32, value = 13, command = self.mfcc_coefficients_scale_callback)
        self.mfcc_coefficients_label_end = ttk.Label(self.mfcc_coefficients_frame, text = "32")
        self.mfcc_coefficients_label.pack(side = tk.LEFT)
        self.mfcc_coefficients_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.mfcc_coefficients_label_end.pack(side = tk.LEFT)

    def setup_sample_rate_frame(self):
        self.sample_rate_frame = ttk.Frame(self.selection_page_frame)
        self.sample_rate_label = ttk.Label(self.sample_rate_frame, text = pad_to_max("Sample rate (Hz):", free = 4))
        self.sample_rate_combobox = ttk.Combobox(self.sample_rate_frame, state = "readonly", values = ("16000", "44100"))
        self.sample_rate_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.sample_rate_label.pack(side = tk.LEFT)
        self.sample_rate_combobox.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def setup_expected_duration_frame(self):
        self.expected_duration_frame = ttk.Frame(self.selection_page_frame)
        self.expected_duration_label = ttk.Label(self.expected_duration_frame, text = pad_to_max("Expected duration (s): 1.00", "0.10"))
        self.expected_duration_scale = ttk.Scale(self.expected_duration_frame, from_ = 0.1, to = 2, value = 1, command = self.expected_duration_scale_callback)
        self.expected_duration_label_end = ttk.Label(self.expected_duration_frame, text = "2.00")
        self.expected_duration_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.expected_duration_label.pack(side = tk.LEFT)
        self.expected_duration_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.expected_duration_label_end.pack(side = tk.LEFT)


    def setup_window_size_frame(self):
        self.window_size_frame = ttk.Frame(self.selection_page_frame)
        self.window_size_label = ttk.Label(self.window_size_frame, text = pad_to_max("Window size (s): 0.50", "0.05"))
        self.window_size_scale = ttk.Scale(self.window_size_frame, from_ = 0.05, to = 1, value = 0.5, command = self.window_size_scale_callback)
        self.window_size_label_end = ttk.Label(self.window_size_frame, text = "1.00")
        self.window_size_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.window_size_label.pack(side = tk.LEFT)
        self.window_size_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.window_size_label_end.pack(side = tk.LEFT)

    def setup_window_stride_frame(self):
        self.window_stride_frame = ttk.Frame(self.selection_page_frame)
        self.window_stride_label = ttk.Label(self.window_stride_frame, text = pad_to_max("Window stride (s): 0.50", "0.05"))
        self.window_stride_scale = ttk.Scale(self.window_stride_frame, from_ = 0.05, to = 1, value = 0.5, command = self.window_stride_scale_callback)
        self.window_stride_label_end = ttk.Label(self.window_stride_frame, text = "1.00")
        self.window_stride_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.window_stride_label.pack(side = tk.LEFT)
        self.window_stride_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.window_stride_label_end.pack(side = tk.LEFT)


    def browse_dataset_button_callback(self):
        if self.browse_dataset_mode == "local":
            data = filedialog.askdirectory()
            self.browse_dataset_entry.delete(0, tk.END)
            self.browse_dataset_entry.insert(0, data)
        else:
            pass

    def browse_dataset_button_change_mode(self, _):
        if self.browse_dataset_mode == "local":
            self.browse_dataset_mode = "global"
            self.browse_dataset_button.config(image = self.images["globe_button"])
        else:
            self.browse_dataset_mode = "local"
            self.browse_dataset_button.config(image = self.images["browse_button"])

    def mfcc_coefficients_scale_callback(self, _):
        value = self.mfcc_coefficients_scale.get()
        if int(value) != value:
            self.mfcc_coefficients_scale.set(round(value))
        self.mfcc_coefficients_label.config(text = pad_to_max("MFCC Coefficients: " + str(round(value)), "1", free = 2))

    def processing_method_combobox_callback(self, _):
        if self.processing_method_combobox.get() == "MFCC":
            self.mfcc_coefficients_frame.pack(expand = True, fill = tk.X, side = tk.BOTTOM)
        else:
            self.mfcc_coefficients_frame.pack_forget()

    def expected_duration_scale_callback(self, _):
        value = self.expected_duration_scale.get()
        # sample_rate = int(self.sample_rate_combobox.get())
        # value = value * sample_rate # in samples
        # value = pow(2, round(math.log2(value))) # nearest power of 2
        self.expected_duration_label.config(text = pad_to_max("Expected duration (s): " + "{:.2f}".format(value), "0.10"))
        self.window_size_scale.config(to = value)
        self.window_size_label_end.config(text = "{:.2f}".format(value))
        self.window_stride_scale.config(to = value)
        self.window_stride_label_end.config(text = "{:.2f}".format(value))
        if self.window_size_scale.get() > value:
            self.window_size_scale.set(value)
        if self.window_stride_scale.get() > value:
            self.window_stride_scale.set(value)

    def window_size_scale_callback(self, _):
        value = self.window_size_scale.get()
        self.window_size_label.config(text = pad_to_max("Window size (s): " + "{:.2f}".format(value), "0.05"))

    def window_stride_scale_callback(self, _):
        value = self.window_stride_scale.get()
        self.window_stride_label.config(text = pad_to_max("Window stride (s): " + "{:.2f}".format(value), "0.05"))

# TRAINING PAGE

    def setup_training_page(self):
        pass

# ARDUINO PAGE

    def setup_arduino_page(self):
        pass

    def load_next_page(self):
        if self.current_page == "selection_page": # send selections to ml script here
            self.selection_page_frame.pack_forget()
            pass
            self.current_page = "training_page"
            self.menu_label.configure(text = "Train a model")
        elif self.current_page == "training_page":
            pass
            pass
            self.current_page = "arduino_page"
            self.menu_label.configure(text = "Upload your model to Arduino")
        else:
            pass
            self.selection_page_frame.pack(fill = tk.BOTH, expand = True)
            self.current_page = "selection_page"
            self.menu_label.configure(text = "Select dataset and processing")

    def load_previous_page(self):
        if self.current_page == "selection_page":
            self.selection_page_frame.pack_forget()
            pass
            self.current_page = "arduino_page"
            self.menu_label.configure(text = "Upload your model to Arduino")
        elif self.current_page == "training_page":
            pass
            self.selection_page_frame.pack(fill = tk.BOTH, expand = True)
            self.current_page = "selection_page"
            self.menu_label.configure(text = "Select dataset and processing")
        else:
            pass
            pass
            self.current_page = "training_page"
            self.menu_label.configure(text = "Train a model")


    

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
    root.geometry("520x240")
    root.resizable(False, False)
    app = main_app(root) 

    root.mainloop()
