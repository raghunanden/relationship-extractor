import gzip
import numpy as np
import random
import os
import pandas as pd

from collections import Counter, defaultdict, namedtuple
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split

