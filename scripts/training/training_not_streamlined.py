from imports import *
from scripts.dataset.dataset_functions import *
from scripts.processing.shared_processing_functions import *
from scripts.processing.processing_not_streamlined import *
from scripts.training.shared_model_functions import *



''' The following functions are only used by the NON-streamlined version of the pipeline '''



def train_model(app):
  
  print_training_selections(app)
  msg_box = app.menu_label
  data = app.data
  batch_size = int(app.batch_size_scale.get())
  epoch_num = int(app.epochs_scale.get())
  validation_split = app.validation_split_scale.get()
  test_split = app.test_split_scale.get()
  model_architecture = app.selected_model_architecture.get()
  num_of_classes = len(data["mapping"])



  # get train, validation, test splits
  X_train, X_validation, X_test, y_train, y_validation, y_test = prepare_datasets(data, test_split, validation_split)
  print('Finished preparing training, validation, and test data')
  print('X_train.shape: {}'.format(X_train.shape) ,'\n')
  input_shape = (X_train[1]).shape
  print('input_shape: ', input_shape)



  # create and compile first model
  model = create_and_compile_model(model_architecture = model_architecture,
                                    input_shape = input_shape,
                                    num_of_classes = num_of_classes,
                                    quantization_aware = False)

  # train
  model.fit(X_train, y_train,
            validation_data = (X_validation, y_validation),
            batch_size = batch_size,
            epochs = epoch_num,
            callbacks = create_callback_list(app))

  # evaluate and print test accuracy
  evaluate_print_test_acc(app, model, X_test=X_test, y_test=y_test)




  msg_box.configure(text = "Retraining for quantization...")
  quantization_aware_model = create_and_compile_model(model_architecture = model_architecture,
                                                      input_shape = input_shape,
                                                      num_of_classes = num_of_classes,
                                                      quantization_aware = True)

  # train again
  quantization_aware_model.fit(X_train, y_train,
                               validation_data = (X_validation, y_validation),
                               batch_size = batch_size,
                               epochs = epoch_num,
                               callbacks = create_callback_list(app, model_checkpoint=False))

  # evaluate and print test accuracy
  evaluate_print_test_acc(app, quantization_aware_model, X_test=X_test, y_test=y_test)

  # delete the weights saved by the first model, since they have been loaded into
  # the quantization aware model at the start of training and are no longer needed
  os.remove('best_model_weights.h5')



  msg_box.configure(text = "Done training!")
  model = quantization_aware_model
  app.model = model