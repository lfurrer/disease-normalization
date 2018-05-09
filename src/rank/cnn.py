#!/usr/bin/env python3
# coding: utf8

# Author: Lenz Furrer, 2018


import os
import argparse

from keras.models import Model
from keras.layers import Input, Dense, Flatten, Concatenate, Dot
from keras.layers import Conv1D, GlobalMaxPooling1D, Embedding

from gensim.models.keyedvectors import KeyedVectors


def main():
    '''
    Run as script.
    '''
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument()
    args = ap.parse_args()


def _run(conf):
    emb_lookup, emb_matrix = _load_embeddings(conf)
    model = _create_model(conf, emb_matrix)


def _create_model(conf, embeddings=None):
    inp_q, inp_a = (Input(shape=(conf.rank.sample_size,)) for _ in range(2))
    emb = _embedding_layer(conf, embeddings)
    sem_q = _semantic_layers(emb(inp_q))
    sem_a = _semantic_layers(emb(inp_a))
    v_sem = Dot(-1)(sem_q, sem_a)
    join_layer = Concatenate()([sem_q, v_sem, sem_a])
    hidden_layer = Dense(units=1+2*conf.rank.n_kernels,
                         activation=conf.rank.activation)(join_layer)
    logistic_regression = Dense(units=2, activation='softmax')(hidden_layer)

    model = Model(inputs=(inp_q, inp_a), outputs=logistic_regression)
    return model


def _load_embeddings(conf):
    wv = KeyedVectors.load_word2vec_format(conf.rank.embedding_fn)
    lookup = {w: i for i, w in enumerate(wv.index2word)}
    return lookup, wv.syn0


def _embedding_layer(conf, matrix=None):
    if matrix is not None:
        vocab_size, embedding_dim = matrix.shape
        layer = Embedding(vocab_size,
                          embedding_dim,
                          weights=[matrix],
                          input_length=conf.rank.sample_size,
                          trainable=False)
    else:
        layer = Embedding(conf.rank.embedding_voc,
                          conf.rank.embedding_dim,
                          input_length=conf.rank.sample_size)
    return layer


def _semantic_layers(x):
    x = Conv1D(conf.rank.n_kernels,
               kernel_size=conf.rank.filter_width,
               activation=conf.rank.activation,
              )(x)
    x = GlobalMaxPooling1D()(x)
    x = Flatten()(x)
    return x


if __name__ == '__main__':
    main()