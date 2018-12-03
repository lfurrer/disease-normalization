#!/usr/bin/env python3
# coding: utf8

# Author: Lenz Furrer, 2018


'''
Common tools for terminology resource processing.
'''


from collections import namedtuple


# Common format for terminology entries.
DictEntry = namedtuple('DictEntry', 'name id alt def_ syn')


class Terminology:
    '''
    Terminology indexed by names and IDs.
    '''
    def __init__(self, dict_entries):
        self._by_name = {}
        self._by_id = {}
        self._index(dict_entries)

    def _index(self, entries):
        for entry in entries:
            self.add(entry)

    def add(self, entry):
        '''
        Update the terminology with a DictEntry object.
        '''
        self._add(self._by_name, entry, entry.name, entry.syn)
        self._add(self._by_id, entry, entry.id, entry.alt)

    @staticmethod
    def _add(index, entry, main, secondary):
        for elem in (main, *secondary):
            index.setdefault(elem, []).append(entry)

    def has_id(self, id_):
        '''
        Is there an entry with this ID (canonical or alternative)?
        '''
        return id_ in self._by_id

    def has_name(self, name):
        '''
        Is there an entry mentioning this name?
        '''
        return name in self._by_name

    def ids(self, names):
        '''
        Get all (preferred) IDs associated with these names.
        '''
        return set(e.id for name in names for e in self._by_name.get(name, ()))

    def names(self, ids):
        '''
        Get all names and synonyms associated with these IDs.
        '''
        names = set()
        for id_ in ids:
            for e in self._by_id.get(id_, ()):
                names.add(e.name)
                names.update(e.syn)
        return names

    def definitions(self, name):
        '''
        Get all definitions associated with this name.
        '''
        return set(e.def_ for e in self._by_name.get(name, ()))

    def canonical_ids(self, id_):
        '''
        Get the preferred ID of all entries that list this ID as alternative.
        '''
        return set(e.id for e in self._by_id[id_])

    def iter_ids(self):
        '''
        Iterate over all IDs.
        '''
        yield from self._by_id

    def iter_names(self):
        '''
        Iterate over all names.
        '''
        yield from self._by_name
