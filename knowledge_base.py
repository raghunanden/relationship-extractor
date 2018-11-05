from collections import namedtuple, Counter
import os
import gzip

rel_ext_data_home = 'rel_ext_data'
KBTriple = namedtuple('KBTriple', 'rel, sbj, obj')

def read_kb_triples():
    kb_triples = []
    path = os.path.join(rel_ext_data_home, 'kb.tsv.gz')
    print('Reading KB triples from {} ...'.format(path))
    with gzip.open(path) as f:
        for line in f:
            rel, sbj, obj = line[:-1].decode('utf-8').split('\t')
            kb_triples.append(KBTriple(rel, sbj, obj))
    print('Read {} KB triples'.format(len(kb_triples)))
    return kb_triples

#kb_triples = read_kb_triples()

class KB():

    def __init__(self, kb_triples):
        self._kb_triples = kb_triples
        self._all_relations = []
        self._all_entity_pairs = []
        self._kb_triples_by_relation = {}
        self._kb_triples_by_entities = {}
        self._collect_all_entity_pairs()
        self._index_kb_triples_by_relation()
        self._index_kb_triples_by_entities()

    def _collect_all_entity_pairs(self):
        pairs = set()
        for kbt in self._kb_triples:
            pairs.add((kbt.sbj, kbt.obj))
        self._all_entity_pairs = sorted(list(pairs))

    def _index_kb_triples_by_relation(self):
        for kbt in self._kb_triples:
            if kbt.rel not in self._kb_triples_by_relation:
                self._kb_triples_by_relation[kbt.rel] = []
            self._kb_triples_by_relation[kbt.rel].append(kbt)
        self._all_relations = sorted(list(self._kb_triples_by_relation))

    def _index_kb_triples_by_entities(self):
        for kbt in self._kb_triples:
            if kbt.sbj not in self._kb_triples_by_entities:
                self._kb_triples_by_entities[kbt.sbj] = {}
            if kbt.obj not in self._kb_triples_by_entities[kbt.sbj]:
                self._kb_triples_by_entities[kbt.sbj][kbt.obj] = []
            self._kb_triples_by_entities[kbt.sbj][kbt.obj].append(kbt)

    def get_triples(self):
        return iter(self._kb_triples)

    def get_all_relations(self):
        return self._all_relations

    def get_all_entity_pairs(self):
        return self._all_entity_pairs

    def get_triples_for_relation(self, rel):
        try:
            return self._kb_triples_by_relation[rel]
        except KeyError:
            return []

    def get_triples_for_entities(self, e1, e2):
        try:
            return self._kb_triples_by_entities[e1][e2]
        except KeyError:
            return []

    def __repr__(self):
        return 'KB with {} triples'.format(len(self._kb_triples))

def count_relation_combinations(kb):
    counter = Counter()
    for sbj, obj in kb.get_all_entity_pairs():
        rels = tuple(sorted(set([kbt.rel for kbt in kb.get_triples_for_entities(sbj, obj)])))
        if len(rels) > 1:
            counter[rels] += 1
    counts = sorted([(count, key) for key, count in counter.items()], reverse=True)
    print('The most common relation combinations are:')
    for count, key in counts:
        print('{:10d} {}'.format(count, key))