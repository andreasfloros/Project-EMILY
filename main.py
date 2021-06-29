from scripts.dataset.dataset_generator import *
from scripts.processing.processing_not_streamlined import *
from scripts.processing.processing_streamlined import *
from scripts.training.training_not_streamlined import *
from scripts.training.training_streamlined import *
from scripts.training.shared_model_functions import convert_and_save_model
from scripts.arduino.arduino import *

# pad all strings to the same length so that the entries etc align (require equal spacing for every character)
def pad_to_max(string, end_txt = "", free = 0):
    chars_to_add = 42 - len(string) - free
    end_txt_length = len(end_txt)
    padded_string = string
    for _ in range(chars_to_add - end_txt_length):
        padded_string += " "
    padded_string += end_txt
    return padded_string

def round_to_x(widget, x = 2):
    value = widget.get()
    if round(value, x) != value:
        widget.set(round(value, x))
    return widget.get()


class custom_cmd():

    def __init__(self, logs):
        self.logs = logs

    def write(self, text):
        self.logs.insert(tk.END, text)
        self.logs.see(tk.END)

    def flush(self):
        try:
            self.logs.delete("end-1c linestart", "end")
        except:
            pass

class main_app():

    def __init__(self, root):
        self.prev_data_path = None
        self.data = None
        self.thread = threading.Thread(target = send_to_arduino)
        self.root = root
        self.images = {"browse_button" : tk.PhotoImage(file = os.path.join(wd,"Images","browse_button.png")),
                       "next_button" : tk.PhotoImage(file = os.path.join(wd,"Images","next_button.png")),
                       "back_button" : tk.PhotoImage(file = os.path.join(wd,"Images","back_button.png")),
                       "globe_button" : tk.PhotoImage(file = os.path.join(wd,"Images","globe_button.png")),
                       "arduino_button" : tk.PhotoImage(file = os.path.join(wd,"Images","arduino_button.png")),
                       "home_button" : tk.PhotoImage(file = os.path.join(wd,"Images","home_button.png")),
                       "train_button" : tk.PhotoImage(file = os.path.join(wd,"Images","train_button.png")),
                       "save_button" : tk.PhotoImage(file = os.path.join(wd,"Images","save_button.png")),
                       "load_data" : tk.PhotoImage(file = os.path.join(wd,"Images","load_data.png")),
                       "process_data" : tk.PhotoImage(file = os.path.join(wd,"Images","process_data.png")),
                       "train_model" : tk.PhotoImage(file = os.path.join(wd,"Images","train_model.png")),
                       "upload_model" : tk.PhotoImage(file = os.path.join(wd,"Images","upload_model.png")),
                       "logo" : tk.PhotoImage(file = os.path.join(wd,"Images","logo.png")),
                       "logo_mac" : tk.PhotoImage(file = os.path.join(wd,"Images","logo_mac.png")),
                       "record_button" : tk.PhotoImage(file = os.path.join(wd,"Images","record_button.png"))}

        if os.name == "nt":
            ttk.Style(root).configure(".", background = background_color, foreground = text_color)
            ttk.Style(root).configure("TEntry", foreground = "#000000")
            ttk.Style(root).configure("TSpinbox", foreground = "#000000", selectbackground = "#f8f4f4", selectforeground = "#000000")
            ttk.Style(root).configure("TLabelframe.Label", foreground = text_color)
            ttk.Style(root).configure("menu.TFrame", background = menu_color)
            ttk.Style(root).configure("menu.TLabel", background = menu_color)
            ttk.Style(root).configure("menu.TButton", background = menu_color)
            ttk.Style(root).configure("TButton", foreground = "#000000")

        else:
            ttk.Style(root).configure("menu.TFrame", background = "#ececec")
            ttk.Style(root).configure("menu.TLabel", background = "#ececec")
            ttk.Style(root).configure("menu.TButton", background = "#ececec")
        #matplotlib.rcParams["axes.grid"] = False
        if os.name == "nt":
            matplotlib.rcParams["text.color"] = text_color
            matplotlib.rcParams["axes.labelcolor"] = text_color
            matplotlib.rcParams["xtick.color"] = text_color
            matplotlib.rcParams["ytick.color"] = text_color
        self.background_frame = ttk.Frame(root)
        self.setup_menu_frame()
        self.setup_home_page()
        self.setup_data_page()
        self.setup_processing_page()
        self.setup_training_page()
        self.setup_arduino_page()
        self.background_frame.pack(expand = True, fill = tk.BOTH)
        self.page_dict = {"home_page" : {"geometry" : home_window_size,
                                         "widget" : self.home_page_frame},
                          "data_page" : {"geometry" : data_window_size,
                                         "widget" : self.data_page_frame,
                                         "menu_label" : "Select a dataset",
                                         "back_button" : "Arduino",
                                         "next_button" : "Processing"},
                          "processing_page" : {"geometry" : processing_window_size,
                                               "widget" : self.processing_page_frame,
                                               "menu_label" : "Select processing",
                                               "back_button" : "Data",
                                               "next_button" : "Training"},
                          "training_page" : {"geometry" : training_window_size,
                                             "widget" : self.training_page_frame,
                                             "menu_label" : "Train a model",
                                             "back_button" : "Processing",
                                             "next_button" : "Arduino"},
                          "arduino_page" : {"geometry" : arduino_window_size,
                                            "widget" : self.arduino_page_frame,
                                            "menu_label" : "Upload your model to Arduino",
                                            "back_button" : "Training",
                                            "next_button" : "Data"}}

        self.prev_processing = {"processing_method" : None,
                            "sample_rate" :           None,
                            "expected_duration" :     None,
                            "window_size" :           None,
                            "window_stride" :         None}

    def setup_menu_frame(self):
        self.current_page = "home_page"
        self.menu_frame = ttk.Frame(self.background_frame, style = "menu.TFrame")
        self.menu_label = ttk.Label(self.menu_frame, text = "", style = "menu.TLabel")
        self.menu_next_button = ttk.Button(self.menu_frame, image = self.images["next_button"], style = "menu.TButton", command = self.load_next_page, text = "", compound = tk.RIGHT)
        self.menu_back_button = ttk.Button(self.menu_frame, image = self.images["back_button"], style = "menu.TButton", command = self.load_previous_page, text = "", compound = tk.LEFT)
        self.menu_home_button = ttk.Button(self.menu_frame, image = self.images["home_button"], style = "menu.TButton", command = lambda : self.load_page("home_page"))
        self.menu_frame.pack(expand = False, fill = tk.X, side = tk.TOP)

        self.menu_label.pack(anchor = tk.CENTER)

# HOME PAGE

    def setup_home_page(self):
        self.home_page_frame = ttk.Frame(self.background_frame)
        if os.name == "nt":
            background_label = tk.Label(self.home_page_frame, image = self.images["logo"])
            self.load_data_button = tk.Button(self.home_page_frame, activebackground = background_color, bd = 0, bg = button_color, relief = tk.FLAT, overrelief = tk.FLAT, image = self.images["load_data"], name = "data_page")
            self.process_data_button = tk.Button(self.home_page_frame, activebackground = background_color, bd = 0, bg = button_color, relief = tk.FLAT, overrelief = tk.FLAT, image = self.images["process_data"], name = "processing_page")
            self.train_model_button = tk.Button(self.home_page_frame, activebackground = background_color, bd = 0, bg = button_color, relief = tk.FLAT, overrelief = tk.FLAT, image = self.images["train_model"], name = "training_page")
            self.upload_model_button = tk.Button(self.home_page_frame, activebackground = background_color, bd = 0, bg = button_color, relief = tk.FLAT, overrelief = tk.FLAT, image = self.images["upload_model"], name = "arduino_page")
        else:
            background_label = tk.Label(self.home_page_frame, image = self.images["logo_mac"])
            self.load_data_button = tk.Button(self.home_page_frame, image = self.images["load_data"], name = "data_page")
            self.process_data_button = tk.Button(self.home_page_frame, image = self.images["process_data"], name = "processing_page")
            self.train_model_button = tk.Button(self.home_page_frame, image = self.images["train_model"], name = "training_page")
            self.upload_model_button = tk.Button(self.home_page_frame, image = self.images["upload_model"], name = "arduino_page")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.load_data_button.bind("<ButtonRelease-1>", self.quad_button_callback)
        self.load_data_button.bind("<Enter>", self.show_button_info)
        
        self.process_data_button.bind("<ButtonRelease-1>", self.quad_button_callback)
        self.process_data_button.bind("<Enter>", self.show_button_info)
        
        self.train_model_button.bind("<ButtonRelease-1>", self.quad_button_callback)
        self.train_model_button.bind("<Enter>", self.show_button_info)
        
        self.upload_model_button.bind("<ButtonRelease-1>", self.quad_button_callback)
        self.upload_model_button.bind("<Enter>", self.show_button_info)
        offset = 0.02
        self.load_data_button.place(relx = 0 + offset, rely = 0 + offset, anchor='nw')
        self.process_data_button.place(relx = 1.0 - offset, rely = 0 + offset, anchor='ne')
        self.train_model_button.place(relx = 0 + offset, rely = 1.0 - offset, anchor='sw')
        self.upload_model_button.place(relx = 1.0 - offset, rely = 1.0 - offset, anchor='se')
        self.home_page_frame.pack(fill = tk.BOTH, expand = True)


    def show_button_info(self, event):
        page = str(event.widget).split(".")[-1]
        if page == "data_page":
            label = "Choose a dataset"
        elif page == "processing_page":
            label = "Configure processing"
        elif page == "training_page":
            label = "Train a model"
        else:
            label = "Upload a model"
        self.menu_label.config(text = label)

    def quad_button_callback(self, event):
        x, y = self.home_page_frame.winfo_pointerxy()

        if event.widget == self.home_page_frame.winfo_containing(x, y):
            page = str(event.widget).split(".")[-1]
            self.load_page(page)

# DATA PAGE

    def setup_data_page(self):
        self.data_page_frame = ttk.Frame(self.background_frame)
        self.setup_dataset_source_frame()
        self.setup_browse_dataset_frame()
        self.setup_browse_dataset_global_frame()
        self.setup_browse_dataset_make_frame()
        self.setup_record_dataset_make_frame()
        self.setup_expected_duration_frame()
        self.setup_sample_rate_frame()

# PROCESSING PAGE

    def setup_processing_page(self):
        self.processing_page_frame = ttk.Frame(self.background_frame)

        self.window_size_frame = ttk.Frame(self.processing_page_frame)
        self.window_stride_frame = ttk.Frame(self.processing_page_frame)
        self.setup_processing_method_frame()
        self.setup_window_size_frame()
        self.setup_window_stride_frame()
        self.setup_streamlining_frame()


    def setup_dataset_source_frame(self):
        self.dataset_source_frame = ttk.Frame(self.data_page_frame)
        self.dataset_source_label = ttk.Label(self.dataset_source_frame, text = pad_to_max(" Data mode:", free = 0))
        self.browse_dataset_mode = tk.StringVar()
        self.dataset_source_radio_button_make = ttk.Radiobutton(self.dataset_source_frame, text = "Make ", value = "make", variable = self.browse_dataset_mode, command = self.browse_dataset_change_mode)
        self.dataset_source_radio_button_local = ttk.Radiobutton(self.dataset_source_frame, text = "Local ", value = "local", variable = self.browse_dataset_mode)
        self.dataset_source_radio_button_global = ttk.Radiobutton(self.dataset_source_frame, text = "URL   ", value = "global", variable = self.browse_dataset_mode, command = self.browse_dataset_change_mode)
        self.dataset_source_radio_button_local.invoke()
        self.dataset_source_radio_button_local.config(command = self.browse_dataset_change_mode)
        self.dataset_source_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.dataset_source_label.pack(side = tk.LEFT)
        self.dataset_source_radio_button_local.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.dataset_source_radio_button_global.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.dataset_source_radio_button_make.pack(side = tk.LEFT, fill = tk.X, expand = True)


    def setup_browse_dataset_frame(self):
        self.browse_dataset_frame = ttk.Frame(self.data_page_frame)
        self.browse_dataset_label = ttk.Label(self.browse_dataset_frame, text = pad_to_max(" Browse dataset:", free = 4))
        self.browse_dataset_button = ttk.Button(self.browse_dataset_frame, image = self.images["browse_button"], command = self.browse_dataset_button_callback)
        self.browse_dataset_entry = ttk.Entry(self.browse_dataset_frame, exportselection = 0)
        self.browse_dataset_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.browse_dataset_label.pack(side = tk.LEFT)
        self.browse_dataset_entry.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.browse_dataset_button.pack(side = tk.LEFT)

    def setup_browse_dataset_global_frame(self):
        self.browse_dataset_global_frame = ttk.Frame(self.data_page_frame)
        self.browse_dataset_global_label = ttk.Label(self.browse_dataset_global_frame, text = pad_to_max(" Dataset destination:", free = 4))
        self.browse_dataset_global_button = ttk.Button(self.browse_dataset_global_frame, image = self.images["browse_button"], command = self.browse_dataset_global_button_callback)
        self.browse_dataset_global_entry = ttk.Entry(self.browse_dataset_global_frame, exportselection = 0)
        self.browse_dataset_global_label.pack(side = tk.LEFT)
        self.browse_dataset_global_entry.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.browse_dataset_global_button.pack(side = tk.LEFT)

    def setup_browse_dataset_make_frame(self):
        self.browse_dataset_make_frame = ttk.Frame(self.data_page_frame)
        self.browse_dataset_make_label = ttk.Label(self.browse_dataset_make_frame, text = pad_to_max(" Labels and samples per label:", free = 4))
        self.num_samples_to_make = tk.StringVar(value = "1")
        self.browse_dataset_make_text_box_number = ttk.Spinbox(self.browse_dataset_make_frame, width = 3, from_ = 1, to = 99, textvariable = self.num_samples_to_make, exportselection = 0, increment = 1, state = "readonly")
        self.browse_dataset_make_text_box_label = ttk.Entry(self.browse_dataset_make_frame, exportselection = 0)


        self.browse_dataset_make_label.pack(side = tk.LEFT)
        self.browse_dataset_make_text_box_label.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.browse_dataset_make_text_box_number.pack(side = tk.LEFT)


    def setup_record_dataset_make_frame(self):
        self.record_dataset_make_frame = ttk.Frame(self.data_page_frame)
        self.record_dataset_make_button = ttk.Button(self.record_dataset_make_frame, text="Record", command = self.record_dataset_make_button_callback, compound = tk.LEFT, image = self.images["record_button"])
        self.record_dataset_make_button.pack(side = tk.RIGHT, padx=125)

    def setup_processing_method_frame(self):
        self.processing_method_frame = ttk.Frame(self.processing_page_frame)
        self.processing_method_label = ttk.Label(self.processing_method_frame, text = pad_to_max(" Processing method:", free = 0))
        self.selected_processing_method = tk.StringVar()

        self.processing_method_radio_button_none = ttk.Radiobutton(self.processing_method_frame, text = "AVG ", value = "NONE", variable = self.selected_processing_method, command = self.processing_method_radio_button_callback)
        self.processing_method_radio_button_stft = ttk.Radiobutton(self.processing_method_frame, text = "STFT", value = "STFT", variable = self.selected_processing_method)
        self.processing_method_radio_button_rms = ttk.Radiobutton(self.processing_method_frame, text = "WRMS", value = "RMS", variable = self.selected_processing_method, command = self.processing_method_radio_button_callback)
        self.processing_method_radio_button_stft.invoke()
        self.processing_method_radio_button_stft.config(command = self.processing_method_radio_button_callback)

        self.processing_method_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.processing_method_label.pack(side = tk.LEFT)

        self.processing_method_radio_button_none.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.processing_method_radio_button_stft.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.processing_method_radio_button_rms.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def setup_sample_rate_frame(self):
        self.sample_rate_frame = ttk.Frame(self.data_page_frame)
        self.sample_rate_label = ttk.Label(self.sample_rate_frame, text = pad_to_max(" Sample rate (Hz):", free = -4))
        self.selected_sample_rate = tk.IntVar()
        self.sample_rate_radio_button_16000 = ttk.Radiobutton(self.sample_rate_frame, text = "16000", value = "16000", variable = self.selected_sample_rate)
        self.sample_rate_radio_button_16000.invoke()
        self.sample_rate_radio_button_41667 = ttk.Radiobutton(self.sample_rate_frame, text = "41667", value = "41667", variable = self.selected_sample_rate)
        self.sample_rate_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.sample_rate_label.pack(side = tk.LEFT)
        self.sample_rate_radio_button_16000.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.sample_rate_radio_button_41667.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def setup_expected_duration_frame(self):
        self.expected_duration_frame = ttk.Frame(self.data_page_frame)
        self.expected_duration_label = ttk.Label(self.expected_duration_frame, text = pad_to_max(" Expected duration (s): 1.00", "0.10"))
        self.expected_duration_scale = ttk.Scale(self.expected_duration_frame, from_ = 0.1, to = 2, value = 1, command = self.expected_duration_scale_callback)
        self.expected_duration_label_end = ttk.Label(self.expected_duration_frame, text = "2.00")
        self.expected_duration_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.expected_duration_label.pack(side = tk.LEFT)
        self.expected_duration_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.expected_duration_label_end.pack(side = tk.LEFT)


    def setup_window_size_frame(self):
        self.window_size_label = ttk.Label(self.window_size_frame, text = pad_to_max(" Window size (samples, log2):"))
        self.selected_window_size = tk.StringVar(value = "9")
        self.window_size_spinbox = ttk.Spinbox(self.window_size_frame, width = 3, from_ = 5, to = 12, command = self.window_size_spinbox_callback, textvariable = self.selected_window_size, exportselection = 0, increment = 1, state = "readonly")
        self.sample_rate_radio_button_16000.config(command = self.window_size_spinbox_callback)
        self.sample_rate_radio_button_41667.config(command = self.window_size_spinbox_callback)

        self.window_size_label_end = ttk.Label(self.window_size_frame, text = "(" + str(round((2 ** 9) / self.selected_sample_rate.get(), 3)) + "s)" )
        self.window_size_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.window_size_label.pack(side = tk.LEFT)
        self.window_size_spinbox.pack(side = tk.LEFT, expand = True)

        self.window_size_label_end.pack(side = tk.LEFT, expand = True)

    def setup_window_stride_frame(self):
        self.window_stride_label = ttk.Label(self.window_stride_frame, text = pad_to_max(" Window stride (s): 0.03", "0.01"))
        self.window_stride_scale = ttk.Scale(self.window_stride_frame, from_ = 0.01, to = 0.33, value = 0.03, command = self.window_stride_scale_callback)
        self.window_stride_label_end = ttk.Label(self.window_stride_frame, text = "0.33")
        self.window_stride_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.window_stride_label.pack(side = tk.LEFT)
        self.window_stride_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.window_stride_label_end.pack(side = tk.LEFT)

    def browse_dataset_button_callback(self):
        if self.browse_dataset_mode.get() == "local" or self.browse_dataset_mode.get() == "make":
            data_path = filedialog.askdirectory()
            if data_path != "":
                self.browse_dataset_entry.delete(0, tk.END)
                self.browse_dataset_entry.insert(0, data_path)

    def record_dataset_make_button_callback(self):
        if self.browse_dataset_mode.get() == "make":
            path = self.browse_dataset_entry.get()
            labels = self.browse_dataset_make_text_box_label.get()
            sample_rate = self.selected_sample_rate.get()
            seconds_of_audio = self.expected_duration_scale.get()
            labels = labels.strip().split(",")
            num_recordings = self.browse_dataset_make_text_box_number.get()
            self.thread = threading.Thread(target = run_all, args = (self, path, labels, num_recordings, sample_rate, seconds_of_audio))
            self.thread.setDaemon(True)
            self.thread.start()


    def browse_dataset_global_button_callback(self):
        data = filedialog.askdirectory()
        if data != "":
            self.browse_dataset_global_entry.delete(0, tk.END)
            self.browse_dataset_global_entry.insert(0, data)

    def browse_dataset_change_mode(self):
        if self.browse_dataset_mode.get() == "global":
            self.browse_dataset_button.config(image = self.images["globe_button"])
            self.browse_dataset_make_frame.pack_forget()
            self.record_dataset_make_frame.pack_forget()
            self.expected_duration_frame.pack_forget()
            self.sample_rate_frame.pack_forget()
            self.browse_dataset_label.config(text=pad_to_max(" Dataset URL:", free = 4))
            self.browse_dataset_global_frame.pack(fill = tk.X, side = tk.TOP, expand = True)
            self.expected_duration_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
            self.sample_rate_frame.pack(fill = tk.X, expand = True)

        elif self.browse_dataset_mode.get() == "make":
            self.browse_dataset_button.config(image = self.images["browse_button"])
            self.browse_dataset_global_frame.pack_forget()
            self.browse_dataset_label.config(text=pad_to_max(" Dataset destination:", free = 4))
            self.expected_duration_frame.pack_forget()
            self.sample_rate_frame.pack_forget()
            self.browse_dataset_make_frame.pack(fill = tk.X, side = tk.TOP, expand = True)
            self.record_dataset_make_frame.pack(fill = tk.X, side = tk.TOP, expand = True)
            self.expected_duration_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
            self.sample_rate_frame.pack(fill = tk.X, expand = True)

        else:
            self.browse_dataset_label.config(text=pad_to_max(" Browse dataset:", free = 4))
            self.browse_dataset_button.config(image = self.images["browse_button"])
            self.browse_dataset_global_frame.pack_forget()
            self.browse_dataset_make_frame.pack_forget()
            self.record_dataset_make_frame.pack_forget()

    def processing_method_radio_button_callback(self):
        selection = self.selected_processing_method.get()
        if selection == "STFT" or selection == "RMS":
            self.streamlining_frame.pack_forget()
            self.window_size_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
            self.window_stride_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
            self.streamlining_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        else:
            self.window_size_frame.pack_forget()
            self.window_stride_frame.pack_forget()

    def expected_duration_scale_callback(self, _):
        value = round_to_x(self.expected_duration_scale)
        self.expected_duration_label.config(text = pad_to_max(" Expected duration (s): " + "{:.2f}".format(value), "0.10"))
        value = round(value / 3, 2)
        self.window_stride_scale.config(to = value)
        self.window_stride_label_end.config(text = "{:.2f}".format(value))
        if self.window_stride_scale.get() > value:
            self.window_stride_scale.set(value)

    def window_size_spinbox_callback(self): ###
        value = int(self.window_size_spinbox.get())
        self.window_size_label_end.config(text = "(" + str(round((2 ** value) / self.selected_sample_rate.get(), 3)) + "s)")

    def window_stride_scale_callback(self, _):
        value = round_to_x(self.window_stride_scale)
        self.window_stride_label.config(text = pad_to_max(" Window stride (s): " + "{:.2f}".format(value), "0.01"))

    def setup_streamlining_frame(self):
        self.streamlining_frame = ttk.Frame(self.processing_page_frame)
        self.centered_streamlining_frame = ttk.Frame(self.streamlining_frame)
        self.streamlining = tk.BooleanVar()
        self.streamlining_label = ttk.Label(self.centered_streamlining_frame, text = "Streamlining: ")
        self.streamlining_checkbutton = ttk.Checkbutton(self.centered_streamlining_frame, variable = self.streamlining, takefocus = False)
        self.streamlining_frame.pack(expand = True, fill = tk.X, side = tk.TOP)
        self.streamlining_label.grid(row = 0, column = 0)
        self.streamlining_checkbutton.grid(row = 0, column = 1)
        self.centered_streamlining_frame.pack(anchor = tk.CENTER)

# TRAINING PAGE

    def setup_training_page(self):
        self.real_time_plots = {"training_accuracy" : [],
                                "validation_accuracy" : []}
        self.model = None
        self.training_page_frame = ttk.Frame(self.background_frame)
        self.real_time_plot_frame = ttk.Frame(self.training_page_frame)
        self.real_time_plot_frame.pack()

        self.fig = Figure(figsize = (5, 5), dpi = 100)
        self.ax = self.fig.add_subplot(1, 1, 1)

        if os.name == "nt":
            self.fig.set_facecolor(background_color)
        else:
            self.fig.set_facecolor("#ececec")
        self.ax.set_facecolor("#ffffff")
        self.plot_canvas = FigureCanvasTkAgg(self.fig, self.training_page_frame)
        self.plot_canvas.get_tk_widget().pack(side = tk.LEFT)
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval = 250, blit = False)

        self.setup_training_settings_frame()

    def animate(self, _):
        self.ax.clear()
        length = len(self.real_time_plots["training_accuracy"])
        xaxis = [i for i in range(1,length + 1)]
        self.ax.plot(xaxis, self.real_time_plots["training_accuracy"], label = "Training accuracy")
        self.ax.plot(xaxis, self.real_time_plots["validation_accuracy"], label = "Validation accuracy")
        self.ax.tick_params(top = False, bottom = False, left = False, right = False, labelleft = True, labelbottom = True)
        if length == 0 or length == 1: # temporary
            self.ax.set_xlim([1,2])
            self.ax.set_ylim([0,1])
            self.ax.get_xaxis().set_major_locator(MaxNLocator(integer = True))
            self.ax.legend(loc = "lower right", labelcolor = "#000000")
        else:
            self.ax.set_xlim([1,length])
            self.ax.get_xaxis().set_major_locator(MaxNLocator(integer = True))
            self.ax.legend(loc = "lower right", labelcolor = "#000000")
        self.plot_canvas.draw()

    def setup_training_settings_frame(self):
        self.training_settings_frame = ttk.Frame(self.training_page_frame)

        self.setup_training_parameters_label_frame()
        self.setup_model_results_label_frame()

        self.training_settings_frame.pack(side = tk.RIGHT, expand = True, fil = tk.BOTH)

    def setup_training_parameters_label_frame(self):
        self.training_parameters_label_frame = ttk.LabelFrame(self.training_settings_frame, text = "Training parameters")
        self.setup_validation_split_frame()
        self.setup_test_split_frame()
        self.setup_model_architecture_frame()
        self.setup_batch_size_frame()
        self.setup_epochs_frame()
        self.train_button = ttk.Button(self.training_parameters_label_frame, image = self.images["train_button"], text = "Train", compound = tk.LEFT, command = self.train_button_callback)
        self.train_button.pack(side = tk.TOP, anchor = tk.CENTER)
        self.training_parameters_label_frame.pack(side = tk.TOP, expand = True, fill = tk.X)

    def train_button_callback(self):
        if not self.thread.is_alive():
            if not self.model is None:
                self.real_time_plots["training_accuracy"] = []
                self.real_time_plots["validation_accuracy"] = []
                self.model = None
            self.menu_label.configure(text = "Training...")

            if self.streamlining.get():
                self.thread = threading.Thread(target = preprocess_data_and_train_model, args = (self, ))
            else:
                self.thread = threading.Thread(target = train_model, args = (self, ))

            self.thread.setDaemon(True)
            self.thread.start()

    def setup_model_architecture_frame(self):
        self.model_architecture_frame = ttk.Frame(self.training_parameters_label_frame)
        self.model_architecture_label = ttk.Label(self.model_architecture_frame, text = pad_to_max("Model architecture:", free = 12))
        self.selected_model_architecture = tk.StringVar()
        self.model_architecture_radio_button_dense = ttk.Radiobutton(self.model_architecture_frame, text = "DENSE", value = "DENSE", variable = self.selected_model_architecture)
        self.model_architecture_radio_button_conv = ttk.Radiobutton(self.model_architecture_frame, text = "CONV", value = "CONV", variable = self.selected_model_architecture)
        self.model_architecture_radio_button_conv.invoke()
        self.model_architecture_label.pack(side = tk.LEFT)
        self.model_architecture_radio_button_dense.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.model_architecture_radio_button_conv.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.model_architecture_frame.pack(expand = True, fill = tk.X, side = tk.TOP)

    def setup_validation_split_frame(self):
        self.validation_split_frame = ttk.Frame(self.training_parameters_label_frame)
        self.validation_split_label = ttk.Label(self.validation_split_frame, text = pad_to_max("Validation split: 0.20", "0.01", free = 12))
        self.validation_split_scale = ttk.Scale(self.validation_split_frame, from_ = 0.01, to = 0.49, command = self.validation_split_scale_callback)
        self.validation_split_label_end = ttk.Label(self.validation_split_frame, text = "0.49")
        self.validation_split_label.pack(side = tk.LEFT)
        self.validation_split_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.validation_split_label_end.pack(side = tk.LEFT)
        self.validation_split_frame.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.validation_split_scale.set(0.2)

    def validation_split_scale_callback(self, _):
        value = round_to_x(self.validation_split_scale)
        self.validation_split_label.config(text = pad_to_max("Validation split: " + "{:.2f}".format(value), "0.01", free = 12))

    def setup_test_split_frame(self):
        self.test_split_frame = ttk.Frame(self.training_parameters_label_frame)
        self.test_split_label = ttk.Label(self.test_split_frame, text = pad_to_max("Test split: 0.25", "0.01", free = 12))
        self.test_split_scale = ttk.Scale(self.test_split_frame, from_ = 0.01, to = 0.49, command = self.test_split_scale_callback)
        self.test_split_label_end = ttk.Label(self.test_split_frame, text = "0.49")
        self.test_split_label.pack(side = tk.LEFT)
        self.test_split_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.test_split_label_end.pack(side = tk.LEFT)
        self.test_split_frame.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.test_split_scale.set(0.25)

    def test_split_scale_callback(self, _):
        value = round_to_x(self.test_split_scale)
        self.test_split_label.config(text = pad_to_max("Test split: " + "{:.2f}".format(value), "0.01", free = 12))

    def setup_batch_size_frame(self):
        self.batch_size_frame = ttk.Frame(self.training_parameters_label_frame)
        self.batch_size_label = ttk.Label(self.batch_size_frame, text = pad_to_max("Batch size: 32", "4", free = 12))
        self.batch_size_scale = ttk.Scale(self.batch_size_frame, from_ = 4, to = 128, command = self.batch_size_scale_callback)
        self.batch_size_scale.set(32)
        self.batch_size_label_end = ttk.Label(self.batch_size_frame, text = "128 ")
        self.batch_size_label.pack(side = tk.LEFT)
        self.batch_size_scale.pack(side = tk.LEFT, fill = tk.X, expand = True)
        self.batch_size_label_end.pack(side = tk.LEFT)
        self.batch_size_frame.pack(side = tk.TOP, expand = True, fill = tk.X)

    def batch_size_scale_callback(self, _):
        value = round_to_x(self.batch_size_scale, x = 0)
        self.batch_size_label.config(text = pad_to_max("Batch size: " + str(round(value)), "4", free = 12))

    def setup_epochs_frame(self):
        self.epochs_frame = ttk.Frame(self.training_parameters_label_frame)
        self.epochs_label = ttk.Label(self.epochs_frame, text = pad_to_max("Epochs: 20", "5", free = 12))
        self.epochs_scale = ttk.Scale(self.epochs_frame, from_ = 5, to = 128, command = self.epochs_scale_callback)
        self.epochs_scale.set(20)
        self.epochs_label_end = ttk.Label(self.epochs_frame, text = "128 ")
        self.epochs_label.pack(side = tk.LEFT)
        self.epochs_scale.pack(side = tk.LEFT, expand = True, fill = tk.X)
        self.epochs_label_end.pack(side = tk.LEFT)
        self.epochs_frame.pack(side = tk.TOP, fill = tk.X, expand = True)


    def epochs_scale_callback(self, _):
        value = round_to_x(self.epochs_scale, x = 0)
        self.epochs_label.config(text = pad_to_max("Epochs: " + str(round(value)), "5", free = 12))


    def setup_model_results_label_frame(self):
        self.model_results_label_frame = ttk.LabelFrame(self.training_settings_frame, text = "Model results")
        self.time_per_epoch = ttk.Label(self.model_results_label_frame, text = "Time per epoch (s):")
        self.test_accuracy_label = ttk.Label(self.model_results_label_frame, text = "Test accuracy:")
        self.test_loss_label = ttk.Label(self.model_results_label_frame, text = "Test loss:")
        self.time_per_epoch.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.test_accuracy_label.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.test_loss_label.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.model_results_label_frame.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.convert_and_save_button = ttk.Button(self.model_results_label_frame, image = self.images["save_button"], text = "Convert & save model", compound = tk.LEFT, command = self.convert_and_save_button_callback)
        self.convert_and_save_button.pack(side = tk.TOP, anchor = tk.CENTER)

    def convert_and_save_button_callback(self):
        if not self.model is None and not self.thread.is_alive():
            save_path = filedialog.asksaveasfilename(defaultextension = ".h")
            if save_path != "":
                self.thread = threading.Thread(target = convert_and_save_model, args = (self, save_path))
                self.thread.setDaemon(True)
                self.thread.start()

# ARDUINO PAGE

    def setup_arduino_page(self):
        self.arduino_page_frame = ttk.Frame(self.background_frame)
        self.setup_arduino_settings_frame()

        self.arduino_cmd = ttk.Frame(self.arduino_page_frame)
        self.logs = tk.Text(self.arduino_cmd, bg = "#000000", fg = "#ffffff", exportselection = 0, font = ("Courier",8))
        self.logs.bind("<Key>", lambda _ : "break")
        self.logs.pack(expand = True, fill = tk.BOTH)
        self.arduino_cmd.pack(side = tk.TOP, expand = True, fill = tk.BOTH)
        self.cmd = custom_cmd(self.logs)
        sys.stdout = self.cmd # COMMENT THIS LINE IF YOU WANT CMD OUTSIDE OF THE UI


    def setup_arduino_settings_frame(self):
        self.arduino_settings_frame = ttk.Frame(self.arduino_page_frame)
        self.arduino_settings_frame.pack(side = tk.TOP, expand = True, fill = tk.X)
        self.centered_arduino_settings_frame = ttk.Frame(self.arduino_settings_frame)
        self.browse_model_label = ttk.Label(self.centered_arduino_settings_frame, text = "Browse model: ")
        self.browse_model_entry = ttk.Entry(self.centered_arduino_settings_frame, exportselection = 0, width = 50)
        self.browse_model_button = ttk.Button(self.centered_arduino_settings_frame, image = self.images["browse_button"], command = self.browse_model_button_callback)
        self.convert_and_upload_model_button = ttk.Button(self.centered_arduino_settings_frame, image = self.images["arduino_button"], text = "Upload model", compound = tk.LEFT, command = self.upload_model_button_callback)
        self.convert_and_upload_model_button.pack(side = tk.RIGHT, padx = 2)
        self.browse_model_label.pack(side = tk.LEFT)
        self.browse_model_entry.pack(side = tk.LEFT)
        self.browse_model_button.pack(side = tk.LEFT)
        self.centered_arduino_settings_frame.pack(anchor = tk.CENTER)

    def upload_model_button_callback(self):
        self.thread = threading.Thread(target = send_to_arduino, args = (self, ))
        self.thread.setDaemon(True)
        self.thread.start()

    def browse_model_button_callback(self):
        file_path = filedialog.askopenfilename()
        if file_path != "":
            self.browse_model_entry.delete(0, tk.END)
            self.browse_model_entry.insert(0, file_path)

# PAGE LOADING

    def load_next_page(self):
        if self.thread.is_alive():
            return
        if self.current_page == "data_page":
            self.load_page("processing_page")
        elif self.current_page == "processing_page": # send selections to ml script here
            if self.streamlining.get() or (self.get_curr_data_path() == self.prev_data_path and self.processing_is_consistent()):
                self.load_page("training_page")
            else:
                self.thread = threading.Thread(target = load_data, args = (self,))
                self.thread.setDaemon(True)
                self.thread.start()

        elif self.current_page == "training_page":
            self.load_page("arduino_page")
        elif self.current_page == "arduino_page":
            self.load_page("data_page")

    def load_previous_page(self):
        if self.thread.is_alive():
            return
        if self.current_page == "data_page":
            self.load_page("arduino_page")
        elif self.current_page == "processing_page":
            self.load_page("data_page")
        elif self.current_page == "training_page":
            self.load_page("processing_page")
        elif self.current_page == "arduino_page":
            if self.streamlining.get() or (self.get_curr_data_path() == self.prev_data_path and self.processing_is_consistent()):
                self.load_page("training_page")
            else:
                self.thread = threading.Thread(target = load_data, args = (self,))
                self.thread.setDaemon(True)
                self.thread.start()

    def unload_pages(self):
        self.home_page_frame.pack_forget()
        self.data_page_frame.pack_forget()
        self.processing_page_frame.pack_forget()
        self.training_page_frame.pack_forget()
        self.arduino_page_frame.pack_forget()

    def load_menu(self, back = True, next = True, home = True, label = True):
        self.menu_next_button.pack_forget()
        self.menu_home_button.pack_forget()
        self.menu_back_button.pack_forget()
        self.menu_label.pack_forget()
        if next == True:
            self.menu_next_button.pack(side = tk.RIGHT)
        if home == True:
            self.menu_home_button.pack(side = tk.RIGHT)
        if back == True:
            self.menu_back_button.pack(side = tk.LEFT)
        if label == True:
            self.menu_label.pack(anchor = tk.CENTER)

    def load_page(self, page, force = False): # code is a bit messy here
        if not force:
            if self.thread.is_alive():
                return
            if page == "processing_page" or page == "training_page":
                if page == "training_page" and self.prev_data_path != self.get_curr_data_path() and not self.streamlining.get() and not self.processing_is_consistent():
                    self.thread = threading.Thread(target = load_data, args = (self,))
                    self.thread.setDaemon(True)
                    self.thread.start()
                    return
                if self.browse_dataset_entry.get() == "":
                    self.menu_label.configure(text = "Dataset source not selected")
                    return
                if self.browse_dataset_mode.get() == "global" and self.browse_dataset_global_entry.get() == "":
                    self.menu_label.configure(text = "Dataset destination not selected")
                    return

        self.current_page = page
        self.root.geometry(self.page_dict[page]["geometry"])
        self.unload_pages()
        self.page_dict[page]["widget"].pack(fill = tk.BOTH, expand = True)
        if page == "home_page":
            self.load_menu(back = False, next = False, home = False)
            self.menu_label.configure(text = "")
        else:
            self.load_menu()
            self.menu_label.configure(text = self.page_dict[page]["menu_label"])
            self.menu_back_button.config(text = self.page_dict[page]["back_button"])
            self.menu_next_button.config(text = self.page_dict[page]["next_button"])

    def get_curr_data_path(self):
        if self.browse_dataset_mode.get() == "local" or self.browse_dataset_mode.get() == "make":
            return app.browse_dataset_entry.get()
        elif self.browse_dataset_mode.get() == "global":
            return app.browse_dataset_global_entry.get()

    def processing_is_consistent(self):
        if self.selected_processing_method.get() != self.prev_processing["processing_method"] \
           or self.selected_sample_rate.get() != self.prev_processing["sample_rate"] \
           or self.expected_duration_scale.get() != self.prev_processing["expected_duration"]:
            return False
        if self.selected_processing_method.get() == "NONE":
            return True
        else:
            return (self.window_size_spinbox.get() == self.prev_processing["window_size"] and self.window_stride_scale.get() == self.prev_processing["window_stride"])

if __name__ == "__main__":
    root = tk.Tk()
    # change font to monospace
    font.nametofont("TkDefaultFont").config(family = "Courier", size = 11)
    #root.option_add("*Font", font.nametofont("TkFixedFont"))
    matplotlib.rc("font", family = "Courier New")
    root.title("MLEcosystem")
    root.geometry(home_window_size)
    root.resizable(False, False)
    app = main_app(root)
    root.mainloop()