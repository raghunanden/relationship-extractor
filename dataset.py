from corpus import Corpus
from knowledge_base import KB
import random
import numpy as np
from collections import defaultdict

def find_unrelated_pairs(corpus, kb):
    unrelated_pairs = set()
    for ex in corpus.get_examples():
        if kb.get_triples_for_entities(ex.entity_1, ex.entity_2):
            continue
        if kb.get_triples_for_entities(ex.entity_2, ex.entity_1):
            continue
        unrelated_pairs.add((ex.entity_1, ex.entity_2))
        unrelated_pairs.add((ex.entity_2, ex.entity_1))
    return unrelated_pairs

def build_datasets(corpus, kb,all_relations,KBTriple, include_positive=True, sampling_rate=0.1, seed=1):
    unrelated_pairs = find_unrelated_pairs(corpus, kb)
    random.seed(seed)
    unrelated_pairs = random.sample(unrelated_pairs, int(sampling_rate * len(unrelated_pairs)))
    kbts_by_rel = defaultdict(list)
    labels_by_rel = defaultdict(list)
    for index, rel in enumerate(all_relations):
        if include_positive:
            for kbt in kb.get_triples_for_relation(rel):
                kbts_by_rel[rel].append(kbt)
                labels_by_rel[rel].append(True)
        for sbj, obj in unrelated_pairs:
            kbts_by_rel[rel].append(KBTriple(rel, sbj, obj))
            labels_by_rel[rel].append(False)
    return kbts_by_rel, labels_by_rel

def split_corpus_and_kb(
        corpus,
        kb,
        split_names=['tiny', 'train', 'dev', 'test'],
        split_fracs=[0.01, 0.69, 0.15, 0.15],
        seed=1):
    if len(split_names) != len(split_fracs):
        raise ValueError('split_names and split_fracs must be of equal length')
    if sum(split_fracs) != 1.0:
        raise ValueError('split_fracs must sum to 1')
    n = len(split_fracs)  # for convenience only

    def split_list(xs):
        xs = sorted(xs)  # sorted for reproducibility
        if seed:
            random.seed(seed)
        random.shuffle(xs)
        split_points = [0] + [int(round(frac * len(xs))) for frac in np.cumsum(split_fracs)]
        return [xs[split_points[i]:split_points[i + 1]] for i in range(n)]

    # first, split the entities that appear as subjects in the KB
    sbjs = list(set([kbt.sbj for kbt in kb.get_triples()]))
    sbj_splits = split_list(sbjs)
    sbj_split_dict = dict([(sbj, i) for i, split in enumerate(sbj_splits) for sbj in split])

    # next, split the KB triples based on their subjects
    kbt_splits = [[kbt for kbt in kb.get_triples() if sbj_split_dict[kbt.sbj] == i] for i in range(n)]

    # now split examples based on the entities they contain
    ex_splits = [[] for i in range(n + 1)]  # include an extra split
    for ex in corpus.get_examples():
        if ex.entity_1 in sbj_split_dict:
            # if entity_1 is a sbj in the KB, assign example to split of that sbj
            ex_splits[sbj_split_dict[ex.entity_1]].append(ex)
        elif ex.entity_2 in sbj_split_dict:
            # if entity_2 is a sbj in the KB, assign example to split of that sbj
            ex_splits[sbj_split_dict[ex.entity_2]].append(ex)
        else:
            # otherwise, put in extra split to be redistributed
            ex_splits[-1].append(ex)
    # reallocate the examples that weren't assigned to a split on first pass
    extra_ex_splits = split_list(ex_splits[-1])
    ex_splits = [ex_splits[i] + extra_ex_splits[i] for i in range(n)]

    # create a Corpus and a KB for each split
    data = {}
    for i in range(n):
        data[split_names[i]] = {'corpus': Corpus(ex_splits[i]), 'kb': KB(kbt_splits[i])}
    data['all'] = {'corpus': corpus, 'kb': kb}
    return data

