from imports import *
from scripts.dataset.dataset_functions import representative_dataset


'''The following functions are used by both the streamlined and non-streamlined versions of the pipeline'''

def print_training_selections(app):
    print('\n')
    print('|--------------------Training Selections--------------------|')
    print('| model_architecture: {}'.format(app.selected_model_architecture.get()))
    print('| validation_split: {}'.format(app.validation_split_scale.get()))
    print('| test_split: {}'.format(app.test_split_scale.get()))
    print('| batch_size: {}'.format(int(app.batch_size_scale.get())))
    print('| epoch_number: {}'.format(int(app.epochs_scale.get())))
    print('|-----------------------------------------------------------|')
    print('\n')




def build_conv_model(input_shape, number_of_classes):

    model = Sequential()


    model.add(InputLayer(input_shape=input_shape))


    # 1st conv layer
    model.add(Conv2D(4, (3, 3), activation='relu', padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))


    # 2nd conv layer
    model.add(Conv2D(8, (3, 3), activation='relu', padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))


    # 3rd conv layer
    model.add(Conv2D(16, (3, 3), activation='relu', padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))


    # 4th conv layer
    model.add(Conv2D(16, (3, 3), activation='relu', padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))


    # flatten output and feed it into dense layer
    model.add(Flatten())
    model.add(Dense(10))
    model.add(Dropout(0.3))


    # output layer
    model.add(Dense(number_of_classes, activation='softmax'))

    return model




def build_dense_model(input_shape, output_dim):
  model = Sequential()
  model.add(Flatten(input_shape = input_shape))
  model.add(Dense(16, activation = "relu"))
  model.add(Dense(32, activation = "relu"))
  model.add(Dense(64, activation = "relu"))
  model.add(Dense(output_dim, activation = "softmax")) #
  return model


# Since quantization-aware training does not apply to some types of layers
# we use `quantize_annotate_layer` to annotate that only the Dense and
# Conv2D layers should be quantized.
def only_dense_and_conv_quantization(layer):
  if isinstance(layer, Dense) or isinstance(layer, Conv2D):
    return tfmot.quantization.keras.quantize_annotate_layer(layer)
  return layer




def evaluate_print_test_acc(app, model, test_dataset = None, X_test = None, y_test = None):
  acc_box = app.test_accuracy_label
  loss_box = app.test_loss_label

  acc_box.configure(text = "Test accuracy: Calculating...")
  loss_box.configure(text = "Test loss: Calculating...")

  if app.streamlining.get():
    test_loss, test_acc = model.evaluate(test_dataset, verbose=2)
  else:
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)

  show_test_accuracy = "{:.2f}".format(test_acc)
  show_test_loss = "{:.2f}".format(test_loss)

  # get test accuracy as a string
  acc_box.configure(text = "Test accuracy: " + show_test_accuracy)
  loss_box.configure(text = "Test loss: " + show_test_loss)



# need this for real time plotting
class log_callback(Callback):

  def __init__(self, app):
    self.app = app
    self.time_ref = time.time()

  def on_epoch_end(self, epoch, logs = None):
      self.app.real_time_plots["training_accuracy"].append(logs["accuracy"])
      self.app.real_time_plots["validation_accuracy"].append(logs["val_accuracy"])
      time_per_epoch = (time.time() - self.time_ref)
      self.app.time_per_epoch.configure(text = "Time per epoch (s): " + "{:.2f}".format(time_per_epoch))
      self.time_ref = time.time()




def create_callback_list(app, plot_training = True, early_stopping = True, model_checkpoint = True):

  callbacks = []

  # early stopping callback so that we stop training if validation loss doesn't reduce for 4 epochs
  early_stop = EarlyStopping(monitor = 'val_loss',
                                 patience = 4,
                                 restore_best_weights = False)
  # checkpoint callback to save the best model thus far (only weights are saved)
  checkpoint_best = ModelCheckpoint('best_model_weights.h5',
                                    monitor = 'val_loss',
                                    save_best_only = True,
                                    save_weights_only = True)

  if plot_training:
    callbacks.append(log_callback(app))
  if early_stopping:
    callbacks.append(early_stop)
  if model_checkpoint:
    callbacks.append(checkpoint_best)

  return callbacks




def create_and_compile_model(model_architecture, input_shape, num_of_classes, quantization_aware):
  # we also need the input and output shapes for the structure of the Neural Network

  # define model for convolutional and dense model
  if model_architecture == 'CONV':
    model = build_conv_model(input_shape, num_of_classes)
  else:
    model = build_dense_model(input_shape, num_of_classes)

  learning_rate = 0.001

  if quantization_aware:
    # load weights from pretrained model
    model.load_weights('best_model_weights.h5')

    # Use 'clone_model` to apply `only_dense_and_conv_quantization` to the layers of the model.
    # annotated_model = clone_model(model, clone_function=only_dense_and_conv_quantization)

    # Now that the Dense and Conv2D layers are annotated,
    # `quantize_apply` states that we do quantization-aware training
    # model = tfmot.quantization.keras.quantize_apply(model)
    model = tfmot.quantization.keras.quantize_model(model)
    learning_rate = 0.000001



  # compile model
  model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate),
                loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                metrics=['accuracy'])
  model.summary()

  return model




def convert_and_save_model(app, save_path):
    app.menu_label.config(text = "Converting and saving model...")

    # user selections
    processing_method = (app.selected_processing_method.get()).lower()
    expected_duration = float(app.expected_duration_scale.get())
    sample_rate = int(app.selected_sample_rate.get())
    window_size = int((2 ** float(app.window_size_spinbox.get())))
    window_stride = int(sample_rate * float(app.window_stride_scale.get()))


    # convert from .h5 to .tflite
    converter = tf.lite.TFLiteConverter.from_keras_model(app.model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    if app.streamlining.get():
      converter.representative_dataset = (lambda : representative_dataset(app.data_for_full_int))

    tflite_model = converter.convert()
    with open('model.tflite', 'wb') as tflite_file:
        tflite_file.write(tflite_model)


    # convert from .tflite to .cc
    platform_name = platform.system()
    tflite_file_path = 'model.tflite'
    if (platform_name == "Linux" or platform_name == "Darwin"):
        command_convert = 'python3 -m hexdump ' + tflite_file_path + ' > model.txt'

    elif(platform_name == "Windows"):
        command_convert = 'python -m hexdump ' + tflite_file_path + ' > model.txt'
    proc = subprocess.Popen(command_convert, shell=True)
    proc.communicate()

    all_lines = []
    start = "0x"
    array_name = "alignas(8) const unsigned char model_tflite[] = {"
    array_len = "unsigned int model_tflite_len = "
    with open('model.txt') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            line = lines[i].strip().split(":")[1]
            line = line.split("  ",2)
            line = line[:-1]
            for element in line:
                split = element.split(" ")
                for x in split:
                    if(x):
                        x = start + x
                        all_lines.append(x)

    f = open(save_path,"w+")
    f.write(array_name)
    f.write("\n")
    count = 0
    for i in range(len(all_lines)):
        if(count == 12):
            f.write("\n")
            f.write("\r")
        if(i == len(all_lines)-1):
            f.write(all_lines[i])
        else:
            f.write(all_lines[i] + ", ")
    f.write("\n")
    f.write("};\n")
    f.write(array_len + str(len(all_lines)) + ";")
    f.close()


    # delete saved model.tflite file since it's only an intermediate step between .h5 and .cc
    # also delete model.txt file
    os.remove('model.tflite')
    os.remove('model.txt')


    all_label_string = "const char* RESPONSES[] = {"
    for label in app.all_labels:
      all_label_string += ('"' + label + '", ')
    all_label_string = all_label_string[:-2]
    all_label_string += "};"

    # write processing parameters to .cc file to be read by arduino file
    with open(save_path) as cc_file:

        new_cc = '''
// ADDED LINES START
constexpr char* processing_method = "{}";
constexpr double expected_duration = {};
constexpr int sample_rate = {};
constexpr int window_size_samples = {};
constexpr int window_stride_samples = {};

{}
unsigned short NUM_RESPONSES = {};

// ADDED LINES END'''.format(processing_method,
                             expected_duration,
                             sample_rate,
                             window_size,
                             window_stride,
                             all_label_string,
                             len(app.all_labels)) + '\n\n' + cc_file.read()


    new_file = open(save_path, "w")
    new_file.write(new_cc)
    new_file.close()

    app.menu_label.config(text = "Done converting and saving!")


    for i in range(20):
      print("\n")