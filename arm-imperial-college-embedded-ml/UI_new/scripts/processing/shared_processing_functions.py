from imports import *


'''The following functions are used by both the streamlined and non-streamlined versions of the pipeline'''

def print_processing_selections(app):

    # get input values from user, note that window_size and window_stride are now in samples
    processing_method = (app.selected_processing_method.get()).lower()
    expected_duration = float(app.expected_duration_scale.get())
    sample_rate = int(app.selected_sample_rate.get())
    window_size = int((2 ** float(app.window_size_spinbox.get())))
    window_stride = int(sample_rate * float(app.window_stride_scale.get()))

    # expected duration is in seconds
    expected_num_samples_per_track = int(expected_duration * sample_rate)

    print('\n')
    print('|-------------------Processing Selections-------------------|')
    print('| processing_method: {}'.format(processing_method))
    print('| expected_duration: {}'.format(expected_duration))
    print('| sample_rate: {}'.format(sample_rate))
    print('| window_size: {}'.format(window_size))
    print('| window_stride: {}'.format(window_stride))
    print('| expected_num_samples_per_track: {}'.format(expected_num_samples_per_track))
    print('|-----------------------------------------------------------|')




def make_track_correct_size(signal, expected_num_samples_per_track):

    # if track is shorter than expected, append it with zeros
    if len(signal) < expected_num_samples_per_track:
      num_zeros_to_pad = expected_num_samples_per_track - len(signal)
      zeros = num_zeros_to_pad * [0.]
      extended_signal = np.append(signal, zeros)
      return extended_signal

    # if track is longer than expected, truncate it
    elif len(signal) > expected_num_samples_per_track:
      return signal[:expected_num_samples_per_track]

    # else return the original track
    else:
      return signal




def fast_RMS(signal, window_size, window_stride):
    # initializations / declarations
    signal_len = len(signal)
    RMS_len = int((signal_len - window_size) / window_stride + 1)
    RMS = []
    squared_signal = [el * el for el in signal]
    window_gap = window_size - window_stride

    if window_gap > 0:
        old_squares_sum = 0
        extra_squares_idx = window_stride - window_gap - 1
        # initialize old_squares_sum and get the partial value for the first RMS
        tmp = 0
        for i in range(min(window_size, signal_len)):
            if i < window_stride:
                old_squares_sum += squared_signal[i]
            else:
                tmp += squared_signal[i]
            
        # get first RMS and initialize the indices
        RMS.append(tmp + old_squares_sum)
        old_squares_idx = window_stride # only need this in the case of extra_squares_idx < 0
        new_squares_idx = window_stride + window_gap

        # main program for window_size > window_stride (works for equality too)
        # this is optimal for small window_stride values
        for i in range(1, RMS_len):
            RMS.append(RMS[i - 1] - old_squares_sum) # remove squares that aren't in the new window

            # get new old squares
            if extra_squares_idx < 0:
                if extra_squares_idx == -1: # in this case, the new old_squares_sum value is readily available
                    old_squares_sum = RMS[i]
                else: # tmp contains more squares than required, adding from the beginning is optimal (window_stride is small)
                    old_squares_sum = 0
                    for _ in range(min(window_stride, signal_len - old_squares_idx)):
                        old_squares_sum += squared_signal[old_squares_idx]
                        old_squares_idx += 1

            # add new squares
            for j in range(min(window_stride, signal_len - new_squares_idx)):
                RMS[i] += squared_signal[new_squares_idx]
                if j == extra_squares_idx: # this can only trigger if extra_squares_idx > -1 i.e. tmp did not contain enough squares initially
                    old_squares_sum = RMS[i]
                new_squares_idx += 1
            if extra_squares_idx > signal_len:
                old_squares_sum = RMS[i]
    else:

        start = 0
        for i in range(RMS_len):
            RMS.append(0)
            for j in range(start, min(start + window_size, signal_len)):
                    RMS[i] += squared_signal[j]
            start += window_stride

    # dividing and square rooting
    for i in range(RMS_len):
        RMS[i] = math.sqrt(abs(RMS[i] / window_size)) # warp in abs to catch any math domain errors due to floating point error

    RMS = np.array(RMS)
    RMS = np.expand_dims(RMS, axis=0)
    RMS = np.expand_dims(RMS, axis=2)
    return RMS




def audio_track_to_features(signal, processing_method, window_size, window_stride):
  if processing_method == 'none':
    # if no processing method is selected we only averaged the signal every 32 samples
    # pad signal to be divisible by 32
    if len(signal) % 32 != 0:
      num_zeros_to_pad = 32 - (len(signal) % 32)
      signal = np.append(signal, num_zeros_to_pad * [0.])

    averaged = np.mean(signal.reshape(-1, 32), axis=1)
    averaged = np.expand_dims(averaged, axis=0)
    averaged = np.expand_dims(averaged, axis=2)
    return averaged, averaged.shape


  elif processing_method == 'stft':
    # perform Short Time Fourier Transform (STFT)
    stft = librosa.stft(y = signal,
                        n_fft = window_size,
                        hop_length = window_stride,
                        window = scipy.signal.windows.boxcar(window_size),
                        center = False)
    # calculate abs values on complex numbers to get magnitude
    spectrogram = np.abs(stft)
    # transpose and return the spectrogram matrix
    transposed_spectrogram = spectrogram.transpose()
    transposed_spectrogram = np.expand_dims(transposed_spectrogram, axis=2)
    return transposed_spectrogram, transposed_spectrogram.shape


  else: # RMS
    RMS = fast_RMS(signal, window_size, window_stride)
    return RMS, RMS.shape
