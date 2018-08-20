#!/usr/bin/env python3
# coding: utf8

# Author: Lenz Furrer, 2018


'''
Dataset loading utilities.
'''


from .terminology import Terminology
from .ncbi_disease import parse_MEDIC_terminology, parse_NCBI_disease_corpus
from .share_clef import parse_ShARe_CLEF_corpus, parse_SNOMED_terminology


# Make the data/terminology loaders accessible through config names.
corpus_loader = {
    'ncbi-disease': parse_NCBI_disease_corpus,
    'share-clef': parse_ShARe_CLEF_corpus,
}
dict_loader = {
    'ncbi-disease': parse_MEDIC_terminology,
    'share-clef': parse_SNOMED_terminology,
}

def load_data(conf, subset, terminology=None):
    '''
    Pick and parse the right corpus or dict file.

    The parameter subset is one of "train", "dev", "test",
    and "dict".
    '''
    dataset = conf.general.dataset
    fn = conf[dataset]['{}_fn'.format(subset)]
    if subset == 'dict':
        return dict_loader[dataset](fn)
    else:
        if terminology is None:
            terminology = load_dict(conf)
        return corpus_loader[dataset](fn, terminology)


def load_dict(conf):
    '''
    Read a dict file into a Terminology instance.
    '''
    return Terminology(load_data(conf, 'dict'))


def itermentions(corpus):
    '''
    Iterate over pairs <text, IDs>.
    '''
    for doc in corpus:
        for sec in doc['sections']:
            for mention in sec['mentions']:
                yield mention['text'], mention['id']
