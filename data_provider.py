from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from pathlib import Path


slim = tf.contrib.slim


def get_split(dataset_dir, split_name='train', batch_size=32):
    """Returns a data split of the RECOLA dataset.
    
    Args:
        split_name: A train/test/valid split name.
    Returns:
        The raw audio examples and the corresponding arousal/valence
        labels.
    """
    path = Path(dataset_dir) / '{}.tfrecords'.format(split_name)
    paths = [str(path)]

    is_training = split_name == 'train'

    filename_queue = tf.train.string_input_producer(paths, shuffle=is_training)

    reader = tf.TFRecordReader()

    _, serialized_example = reader.read(filename_queue)

    features = tf.parse_single_example(
        serialized_example,
        features={
            'raw_audio': tf.FixedLenFeature([], tf.string),
            'label': tf.FixedLenFeature([], tf.int64),
        }
    )
    
    raw_audio, label = tf.train.shuffle_batch(
        [features['raw_audio'], features['label']], 1, 5000, 500, 4)

    raw_audio = tf.decode_raw(raw_audio[0], tf.float32)

    frames, labels = tf.train.batch([raw_audio, label[0]], batch_size,
                                    capacity=1000, dynamic_pad=True)

    # 640 samples at 16KhZ corresponds to 40ms.
    raw_audio.set_shape([640])
    label.set_shape([1])


    frames = tf.reshape(frames, (batch_size, -1, 640))
    labels = slim.one_hot_encoding(labels, 2)
    
    return frames, labels
