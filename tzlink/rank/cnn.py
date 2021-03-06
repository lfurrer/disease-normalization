#!/usr/bin/env python3
# coding: utf8

# Author: Lenz Furrer, 2018


'''
Convolutional Neural Network for ranking mention-candidate pairs.
'''


import logging

from keras.models import Model
from keras.layers import Input, Dense, Concatenate, Layer
from keras.layers import Conv1D, GlobalMaxPooling1D, Embedding
from keras import backend as K

from ..preprocessing import samples
from .callback import EarlyStoppingRankingAccuracy


def run_training(conf, dumpfn, **evalparams):
    '''
    Train a model and evaluate/predict.
    '''
    sampler = samples.Sampler(conf)
    tr_data = sampler.training_samples()
    val_data = sampler.prediction_samples()
    logging.info('compiling model architecture...')
    model = _create_model(conf, sampler)
    logging.info('training CNN...')
    earlystopping = EarlyStoppingRankingAccuracy(conf, val_data, dumpfn, evalparams)
    model.fit(tr_data.x, tr_data.y, sample_weight=tr_data.weights,
              callbacks=[earlystopping],
              epochs=conf.rank.epochs,
              batch_size=conf.rank.batch_size)
    logging.info('done.')


def _create_model(conf, sampler):
    # Embedding layers are shared among all inputs.
    emb = [embedding_layer(conf[emb], sampler.emb[emb].emb_matrix)
           for emb in conf.rank.embeddings]
    inp_mentions, sem_mentions = _semantic_repr_qa(conf, emb, 'sample_size')
    inp_context, sem_context = _semantic_repr_qa(conf, emb, 'context_size')
    inp_scores = Input(shape=(len(conf.candidates.generator.split('\n')),))
    inp_overlap = Input(shape=(1,))  # token overlap between q and a

    v_sem = PairwiseSimilarity()(sem_mentions)
    join_layer = Concatenate()(
        [*sem_mentions, v_sem, *sem_context, inp_scores, inp_overlap])
    hidden_layer = Dense(units=K.int_shape(join_layer)[-1],
                         activation=conf.rank.activation)(join_layer)
    logistic_regression = Dense(units=1, activation='sigmoid')(hidden_layer)

    model = Model(inputs=(*inp_mentions, *inp_context, inp_scores, inp_overlap),
                  outputs=logistic_regression)
    model.compile(optimizer=conf.rank.optimizer, loss=conf.rank.loss)
    return model


def _semantic_repr_qa(conf, emb_layers, size_name):
    sizes = [conf[emb][size_name] for emb in conf.rank.embeddings]
    emb_info = [(s, e) for s, e in zip(sizes, emb_layers) if s]
    if not emb_info:  # sample/context size is 0 -> omit entirely
        return [], []
    nodes = (semantic_layers(conf, emb_info) for _ in range(2))
    (inp_q, inp_a), (sem_q, sem_a) = zip(*nodes)
    return inp_q + inp_a, [sem_q, sem_a]


def semantic_layers(conf, emb_info):
    '''Layers for semantic representation.'''
    inp, sem = [], []
    for size, emb_layer in emb_info:
        i = Input(shape=(size,))
        inp.append(i)
        e = emb_layer(i)
        for width in conf.rank.filter_width:
            sem.append(_convolution_pooling(conf, width, e))
    sem = _conditional_concat(sem)
    return inp, sem


def embedding_layer(econf, matrix=None, **kwargs):
    '''A layer for word/character/... embeddings.'''
    if matrix is not None:
        args = matrix.shape
        kwargs.update(weights=[matrix],
                      trainable=econf.trainable)
    else:
        args = (econf.embedding_voc, econf.embedding_dim)
    return Embedding(*args, **kwargs)


def _convolution_pooling(conf, width, x):
    x = Conv1D(conf.rank.n_kernels,
               kernel_size=width,
               activation=conf.rank.activation,
              )(x)
    x = GlobalMaxPooling1D()(x)
    return x


def _conditional_concat(layers):
    if len(layers) > 1:
        return Concatenate()(layers)
    return layers[0]


class PairwiseSimilarity(Layer):
    '''
    Join layer with a trainable similarity matrix.

    v_sem = sim(v_q, v_a) = v_q^T M v_a
    '''

    def __init__(self, **kwargs):
        self.M = None  # set in self.build()
        super().__init__(**kwargs)

    def build(self, input_shape):
        try:
            shape_q, shape_a = input_shape
        except ValueError:
            raise ValueError('input_shape must be a 2-element list')
        self.M = self.add_weight(name='M',
                                 shape=(shape_q[1], shape_a[1]),
                                 initializer='uniform',
                                 trainable=True)
        super().build(input_shape)

    def call(self, inputs):
        q, a = inputs
        # https://github.com/wglassly/cnnormaliztion/blob/master/src/nn_layers.py#L822
        return K.batch_dot(q, K.dot(a, K.transpose(self.M)), axes=1)

    @staticmethod
    def compute_output_shape(input_shape):
        return (input_shape[0][0], 1)
