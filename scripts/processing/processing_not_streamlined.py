from imports import *
from scripts.dataset.dataset_functions import download_and_extract_dataset
from scripts.processing.shared_processing_functions import *



''' The following functions are only used by the non-streamlined version of the pipeline '''



def preprocess_entire_dataset(app):

  data_mode = app.browse_dataset_mode.get()

  if data_mode == 'local':
    dataset_path = app.browse_dataset_entry.get()
  elif data_mode == 'make':
    dataset_path = app.browse_dataset_entry.get()
    dataset_path = dataset_path.replace("/", "\\")

  else: # global
    dataset_url = app.browse_dataset_entry.get()
    dataset_path = app.browse_dataset_global_entry.get()
    download_and_extract_dataset(dataset_url, dataset_path)
    dataset_path = os.path.join(dataset_path,dataset_url.split("/")[-1])


  # get input values from user, note that window_size and window_stride are now in samples
  processing_method = (app.selected_processing_method.get()).lower()
  expected_duration = float(app.expected_duration_scale.get())
  sample_rate = int(app.selected_sample_rate.get())
  window_size = int((2 ** float(app.window_size_spinbox.get())))
  window_stride = int(sample_rate * float(app.window_stride_scale.get()))
  expected_num_samples_per_track = int(expected_duration * sample_rate)

  print_processing_selections(app)

  # dictionary to later be converted to final json file
  data = {
      'mapping' : [],
      'features' : [],
      'labels' : [],
  }


  # we will iterate this for each of the visited sub-directorie in order to
  # give a different label for each of them
  visited_directory_index = 0

  # iterate through all subfolders
  for dirpath, dirnames, filenames in os.walk(dataset_path):
    # ensure we are not at the dataset root directory
    # since os.walk provides this directory as well
    if dirpath is not dataset_path:
    # if dirpath == os.path.join(dataset_path, 'yes') or dirpath == os.path.join(dataset_path, 'no') or dirpath == os.path.join(dataset_path, 'bed') or dirpath == os.path.join(dataset_path, '_background_noise_'):
    # if dirpath == os.path.join(dataset_path, 'yes') or dirpath == os.path.join(dataset_path, 'no'):
      # obtain word labels
      dirpath_components = dirpath.split(os.path.sep) # audio_data/left => ['audio_data', 'left']
      word_label = dirpath_components[-1]
      data['mapping'].append(word_label)
      print('Processing {}'.format(word_label))

      # access and process files for current word
      for file_name in filenames:

        # load audio file
        file_path = os.path.join(dirpath, file_name)
        try:
          signal, sample_rate = librosa.load(file_path, sr=sample_rate)
          signal *= 3276.7
        except:
          continue

        # extend or cut signal to be equal to the expected size
        signal_correct_size = make_track_correct_size(signal, expected_num_samples_per_track)

        # obtain the features of the audio track using the function defined above
        track_features, feature_map_shape = audio_track_to_features(signal = signal_correct_size,
                                                                    processing_method = processing_method,
                                                                    window_size = window_size,
                                                                    window_stride = window_stride)

        # append the audio track features to the features field of the dictionary
        data['features'].append(track_features.tolist())

        # append the current directory index as the label of this track
        data['labels'].append(visited_directory_index)
        # print('file_path: {}'.format(file_path))

      # iterate the index before visiting the next directory
      visited_directory_index = visited_directory_index + 1

  print('\n')
  print('Semantic labels: {}'.format(data['mapping']))
  print('Numeric labels: {}'.format(set(data['labels'])))
  # print('Reshape shape: {}'.format(data['reshape_shape']))
  print('\n')

  return data




def load_data(app):

  try:
    msg_box = app.menu_label
    msg_box.configure(text = "Attempting to load dataset...")
    acc_box = app.test_accuracy_label
    acc_box.configure(text = "Test accuracy:")
    loss_box = app.test_loss_label
    loss_box.configure(text = "Test loss:")

    # create data dictionary with the entire dataset processed
    data = preprocess_entire_dataset(app)


    # if there are no labels give an error and return without training
    if len(data["labels"]) == 0:
      msg_box.configure(text = "Failed to load dataset")
      return

    app.all_labels = np.array(data["mapping"])

    app.data = data
    if app.browse_dataset_mode.get() == "local" or app.browse_dataset_mode.get() == 'make':
        app.prev_data_path = app.browse_dataset_entry.get()
    else:
        app.prev_data_path = app.browse_dataset_global_entry.get()

    app.prev_processing = {"processing_method" : app.selected_processing_method.get(),
                           "sample_rate" : app.selected_sample_rate.get(),
                           "expected_duration" : app.expected_duration_scale.get(),
                           "window_size" : app.window_size_spinbox.get(),
                           "window_stride" : app.window_stride_scale.get()}


    app.load_page("training_page", force = True)

  except Exception as exception:
    app.menu_label.configure(text = str(exception))
    # error_popup(str(exception))
# ============================================================================================================================