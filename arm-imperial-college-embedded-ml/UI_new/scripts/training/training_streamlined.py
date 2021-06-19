from imports import *
from scripts.dataset.dataset_functions import *
from scripts.processing.shared_processing_functions import *
from scripts.processing.processing_streamlined import *
from scripts.training.shared_model_functions import *



''' The following functions are only used by the streamlined version of the pipeline (using tf.data.Dataset) '''



def preprocess_data_and_train_model(app):

  try: 

    # print the user-selected processing and training parameters
    print_processing_selections(app)
    print_training_selections(app)


    # get train, validation, test files
    train_files, val_files, test_files = split_datasets(app)
    print('----------------------------- Done preparing datasets! -----------------------------', '\n\n')



    # locally define important dataset and model parameters
    all_labels = get_all_labels(app)
    batch_size = int(app.batch_size_scale.get())
    epoch_num = int(app.epochs_scale.get())
    model_architecture = app.selected_model_architecture.get()

    
    print('-------------------------- Defining dataset preprocessing --------------------------', '\n\n')
    # get feature and label arrays for each of the file splits
    train_dataset = preprocess_files(train_files, app, all_labels)
    val_dataset = preprocess_files(val_files, app, all_labels)
    test_dataset = preprocess_files(test_files, app, all_labels)
    app.data_for_full_int = preprocess_files(train_files, app, all_labels, representative = True)

    # batch the datasets above
    train_dataset_batched = train_dataset.batch(batch_size)
    val_dataset_batched = val_dataset.batch(batch_size)
    test_dataset_batched = test_dataset.batch(batch_size)



    
    print('--------------------------- Checking a training example  ---------------------------', '\n\n')
    # get an example from the training data to extract the input_shape
    # also define the reshape_shape as well as the number of classes
    # print('train_dataset.take(1): ', train_dataset.take(1))
    for example_feature_map, example_label in train_dataset.take(1):
        continue
    example_feature_map = example_feature_map.numpy()
    input_shape = example_feature_map.shape
    # reshape_shape_without_extra_axis = get_reshape_shape(app)
    # reshape_shape = reshape_shape_without_extra_axis + (1,)
    num_of_classes = len(all_labels)

    # print important parameters
    print('example_feature_map: ', example_feature_map)
    print('example_feature_map.shape: ', example_feature_map.shape)
    print('example_label: ', example_label)
    print('example_label.shape: ', example_label.shape, '\n')
    print('input_shape: ', input_shape)
    # print('reshape_shape: ', reshape_shape)
    print('num_of_classes: ', num_of_classes, '\n')

    # plot an example feature map
    # actually breaks the code later during training
    # plot_example_feature_map(example_feature_map, reshape_shape_without_extra_axis)


    print('------------------------ Starting compilation and training  ------------------------', '\n\n')
    # create and compile first model
    model = create_and_compile_model(model_architecture = model_architecture,
                                     input_shape = input_shape,
                                     num_of_classes = num_of_classes,
                                     quantization_aware = False)

    # train
    model.fit(train_dataset_batched,
              validation_data = val_dataset_batched,
              epochs = epoch_num,
              callbacks = create_callback_list(app))

    # evaluate and print test accuracy
    evaluate_print_test_acc(app, model, test_dataset_batched)




    app.menu_label.configure(text = "Retraining for quantization...")
    quantization_aware_model = create_and_compile_model(model_architecture = model_architecture,
                                                        input_shape = input_shape,
                                                        num_of_classes = num_of_classes,
                                                        quantization_aware = True)

    # train again
    quantization_aware_model.fit(train_dataset_batched,
                                 validation_data = val_dataset_batched,
                                 epochs = epoch_num,
                                 callbacks = create_callback_list(app, model_checkpoint=False))

    # evaluate and print test accuracy
    evaluate_print_test_acc(app, quantization_aware_model, test_dataset_batched)

    # delete the weights saved by the first model, since they have been loaded into
    # the quantization aware model at the start of training and are no longer needed
    os.remove('best_model_weights.h5')



    app.menu_label.configure(text = "Done training!")
    model = quantization_aware_model
    app.model = model
    
  except Exception as exception:
    app.menu_label.configure(text = str(exception))