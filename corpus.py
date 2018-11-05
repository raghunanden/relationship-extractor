from collections import namedtuple
import gzip
import os

rel_ext_data_home = 'rel_ext_data'

Example = namedtuple('Example',
    'entity_1, entity_2, left, mention_1, middle, mention_2, right, '
    'left_POS, mention_1_POS, middle_POS, mention_2_POS, right_POS')

def read_examples():
    examples = []
    path = os.path.join(rel_ext_data_home, 'corpus.tsv.gz')
    print('Reading examples from {}'.format(path))
    with gzip.open(path) as f:
        for line in f:
            fields = line[:-1].decode('utf-8').split('\t')
            examples.append(Example(*fields))
    print('Read {} examples'.format(len(examples)))
    return examples

#examples = read_examples()

class Corpus():

    def __init__(self, examples):
        self._examples = examples
        self._examples_by_entities = {}
        self._index_examples_by_entities()

    def _index_examples_by_entities(self):
        for ex in self._examples:
            if ex.entity_1 not in self._examples_by_entities:
                self._examples_by_entities[ex.entity_1] = {}
            if ex.entity_2 not in self._examples_by_entities[ex.entity_1]:
                self._examples_by_entities[ex.entity_1][ex.entity_2] = []
            self._examples_by_entities[ex.entity_1][ex.entity_2].append(ex)

    def get_examples(self):
        return iter(self._examples)

    def get_examples_for_entities(self, e1, e2):
        try:
            return self._examples_by_entities[e1][e2]
        except KeyError:
            return []

    def __repr__(self):
        return 'Corpus with {} examples'.format(len(self._examples))

def show_examples_for_pair(e1, e2, corpus):
    exs = corpus.get_examples_for_entities(e1, e2)
    if exs:
        print('The first of {} examples for {} and {} is:'.format(len(exs), e1, e2))
        print(exs[0])
    else:
        print('No examples for {} and {} is:'.format(e1, e2))

#show_examples_for_pair('Steve_Jobs', 'Pixar', corpus)