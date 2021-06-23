from imports import *


# This function is used by both the streamlined and non-streamlined versions of the pipeline
# ============================================================================================================================
def download_and_extract_dataset(dataset_url, dataset_root_dir):
    # create directory audio_data at location DATASET_ROOT_DIR
    if dataset_url[-4:] == ".zip":
        format = ".zip"
    elif dataset_url[-7:] == ".tar.gz":
        format = ".tar.gz"
    else:
        raise Exception("Invalid URL: Not a .zip or .tar format") # wrap load_data with a try and except and change the menu label to the error message on exception
    dataset_name = dataset_url.split("/")[-1]
    save_path = os.path.join(dataset_root_dir,dataset_name)
    try:
        os.mkdir(save_path)
    except:
        raise Exception("Chosen folder already exists") # should probably create different directory (name_1, name_2 etc)
    target_path = os.path.join(save_path,dataset_name)

    try:
        response = requests.get(dataset_url, stream=True)
    except:
        raise Exception("Failed to extract files")

    if response.status_code == 200:
        with open(target_path, 'wb') as f:
            f.write(response.raw.read())
    else:
        raise Exception("Download failed")
    try:
        if format == ".tar.gz":
            tar = tarfile.open(target_path, "r:gz")
            tar.extractall(path = save_path)
            tar.close()
        elif format == ".zip":
            with zipfile.ZipFile(target_path,"r") as zip_ref:
                zip_ref.extractall(path = save_path)
    except:
        raise Exception("Failed to extract files")
# ============================================================================================================================



# The following functions are only used by the NON-streamlined version of the pipeline
# ============================================================================================================================
def prepare_datasets(data, test_size, validation_size):
  print('Splitting dataset into training, validation, and test splits')

  X = np.array(data["features"])
  y = np.array(data["labels"])
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = test_size)
  X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size = validation_size)
  return X_train, X_validation, X_test, y_train, y_validation, y_test
# ============================================================================================================================




# The following functions are only used by the streamlined version of the pipeline (using tf.data.Dataset)
# ============================================================================================================================
def get_all_labels(app):
    # get the user-selected path to the dataset root directory
    dataset_path = app.browse_dataset_entry.get()

    # get all the labels as the names of all the subdirectories
    all_labels = []
    all_subfolders_paths = [f.path for f in os.scandir(dataset_path) if f.is_dir()]

    for subfolder_path in all_subfolders_paths:
        word_label = (subfolder_path.split(os.path.sep))[-1]
        all_labels.append(word_label)

    print('all_labels:', all_labels, '\n\n')
    app.all_labels = all_labels
    all_labels = tf.convert_to_tensor(all_labels)

    return all_labels




def get_filelist_from_dataset(app):
    data_mode = app.browse_dataset_mode.get()
    if data_mode == 'local':
        dataset_root_path = app.browse_dataset_entry.get()
    elif data_mode == 'make':
        dataset_root_path = app.browse_dataset_entry.get()
    else: # global
        dataset_url = app.browse_dataset_entry.get()
        dataset_root_path = app.browse_dataset_global_entry.get()
        download_and_extract_dataset(app, dataset_url, dataset_root_path)

    filenames = tf.io.gfile.glob(str(dataset_root_path) + '/*/*')
    filenames = tf.random.shuffle(filenames)
    filenames = filenames.numpy()
    filenames = tf.convert_to_tensor(filenames)
    num_of_tracks = len(filenames)

    print('\n')
    print('Total number of samples:', num_of_tracks)

    return filenames, num_of_tracks




def split_datasets(app):
    validation_split = app.validation_split_scale.get()
    test_split = app.test_split_scale.get()
    train_split = 1 - validation_split - test_split

    # get shuffled list of all tracks
    file_list, num_of_tracks = get_filelist_from_dataset(app)

    train_files_end = int(num_of_tracks * train_split)
    val_files_end = int(num_of_tracks * (train_split + validation_split))

    train_files = file_list[: train_files_end]
    val_files = file_list[train_files_end : val_files_end]
    test_files = file_list[val_files_end :]

    print('Number of training files: ', len(train_files))
    print('Number of validation files: ', len(val_files))
    print('Number of testing files: ', len(test_files))

    return train_files, val_files, test_files




def plot_example_feature_map(example_feature_map, reshape_shape):
    example_feature_map = np.reshape(example_feature_map, reshape_shape)
    log_spec = np.log(example_feature_map.T)
    height = log_spec.shape[0]
    width = log_spec.shape[1]
    X = np.linspace(0, np.size(example_feature_map), num=width, dtype=int)
    Y = range(height)
    plt.pcolormesh(X, Y, log_spec)
    plt.show()




def representative_dataset(dataset):
  for data in dataset.batch(1).take(100):
    yield [tf.dtypes.cast(data, tf.float32)]
# ============================================================================================================================