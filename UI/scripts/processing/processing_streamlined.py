from imports import *
from scripts.processing.shared_processing_functions import *



''' The following functions are only used by the streamlined version of the pipeline (using tf.data.Dataset) '''



def get_user_parameters_as_tensors(app):
    # get input values from user, note that window_size and window_stride are now in samples
    processing_method = (app.selected_processing_method.get()).lower()
    expected_duration = float(app.expected_duration_scale.get())
    sample_rate = int(app.selected_sample_rate.get())
    window_size = int((2 ** float(app.window_size_spinbox.get())))
    window_stride = int(sample_rate * float(app.window_stride_scale.get()))
    expected_num_samples_per_track = int(expected_duration * sample_rate)

    processing_method = tf.constant(tf.convert_to_tensor(processing_method))
    sample_rate = tf.constant(tf.convert_to_tensor(sample_rate))
    window_size = tf.constant(tf.convert_to_tensor(window_size))
    window_stride = tf.constant(tf.convert_to_tensor(window_stride))
    expected_num_samples_per_track = tf.constant(tf.convert_to_tensor(expected_num_samples_per_track))

    return processing_method, sample_rate, window_size, window_stride, expected_num_samples_per_track




def get_label_id(file_path, all_labels):

    # get the file path components
    # some_path / cat / 001.wav  ->  [some_path, cat, 001.wav]
    file_path_components = file_path.split(os.path.sep)

    # get the semantic label as the second from the end entry of the file_path
    # [some_path, cat, 001.wav]  ->  cat
    semantic_label_tensor = file_path_components[-2]

    # define the numeric label as the index of the semantic label in the label list
    numeric_label = tf.where(semantic_label_tensor == all_labels)

    # get the numeric label as an integer
    numeric_label = numeric_label[0][0]

    return numeric_label




def get_label_and_features_from_filepath(file_path, processing_method, sample_rate, window_size, window_stride, expected_num_samples_per_track, all_labels):

    # convert the file_path to a string for get_label_id and librosa.load which don't handle tensor inputs
    file_path = tf.compat.as_str_any(file_path.numpy())

    # get the track label
    track_label = get_label_id(file_path, all_labels)


    # load the signal to a numpy array using librosa
    signal, sample_rate = librosa.load(file_path, sr=sample_rate)
    # multiply signal by max value of int16 to replicate Arduino-side processing
    signal *= 3276.7
    # extend(zero-pad) or truncate the signal to ensure it is the expected size
    signal_correct_size = make_track_correct_size(signal, expected_num_samples_per_track)

    # obtain the features of the audio track based on the user parameters
    track_features, feature_map_shape = audio_track_to_features(signal = signal_correct_size,
                                                                processing_method = processing_method,
                                                                window_size = window_size,
                                                                window_stride = window_stride)

    # convert track features to a fixed data type
    track_features = np.float32(track_features)

    # convert the track features, feature map shape, and track label to tensors before returning
    # this is needed because this function is wrapped in tf.py_function and thus expected to return tensors
    track_features = tf.convert_to_tensor(track_features)
    track_label = tf.convert_to_tensor([track_label])
    feature_map_shape = tf.convert_to_tensor(feature_map_shape)

    # return a tuple of the track features, feature map shape, and track label
    return track_features, feature_map_shape, track_label



# get the features and label from a particular file by wrapping the Python processing function in tf.py_function
def tf_get_features_and_label(file, processing_method, sample_rate, window_size, window_stride, expected_num_samples_per_track, all_labels, representative):

    [track_features, feature_map_shape, track_label] = tf.py_function(func = get_label_and_features_from_filepath,
                                                                      inp = [file, processing_method, sample_rate, window_size, window_stride, expected_num_samples_per_track, all_labels],
                                                                      Tout = [tf.float32, tf.int32, tf.int64])

    # we are required to set the shapes of the feature map and the label because tensorflow is
    # unable to infer shapes when using tf.py_function (since is has arbitrary Python logic inside)
    track_features.set_shape(tf.get_static_value(feature_map_shape))
    track_label.set_shape([1,])
    if representative:
        return track_features
    else:
        return track_features, track_label



# this funciton will run three times, one for training files, one for validation files, and one for test files
def preprocess_files(files, app, all_labels, representative = False):
    # get the user parameters as tensors since they need to be tensors to be used as inputs in the py_function wrapper below
    processing_method, sample_rate, window_size, window_stride, expected_num_samples_per_track = get_user_parameters_as_tensors(app)

    # create a Tensorflow dataset from the files passed to this function
    dataset_files = tf.data.Dataset.from_tensor_slices(files)

    # iterate through the dataset and get the features and label for each file
    features_and_maybe_labels = dataset_files.map(lambda file : tf_get_features_and_label(file, processing_method, sample_rate, window_size, window_stride, expected_num_samples_per_track, all_labels, representative = representative))

    print('----------------------- Done extracting features and labels! -----------------------', '\n\n')
    return features_and_maybe_labels