import os
import pickle
from string import punctuation

import Levenshtein as lev

import db


class Autocomplete:
    def __init__(self):
        if not os.path.isdir('models'):
            os.makedirs('models')
        if not os.path.isfile("models/song_titles"):
            song_titles = db.get_song_titles()
            with open('models/song_titles', 'wb') as fp:
                pickle.dump([self.preprocess_text(doc) for doc in song_titles], fp)

        with open('models/song_titles', 'rb') as fp:
            self.corpus_prp = pickle.load(fp)
        self.uniq_corpus = set(self.corpus_prp)

    def preprocess_text(self, text):
        tokens = text.lower().split(" ")
        tokens = [token for token in tokens if token != " " and token.strip() not in punctuation]
        text = " ".join(tokens)
        return text

    def _get_closest_levenstein(self, token, top_k=10):
        top_token = [" " for _ in range(top_k)]
        top_score = [0.0 for _ in range(top_k)]

        for t in self.uniq_corpus:
            temp_score_lev = lev.ratio(token, t)
            for i in range(top_k):
                if temp_score_lev > top_score[i]:
                    old_t = top_token[i]
                    old_score = top_score[i]

                    for j in range(i + 1, top_k):
                        temp_score = top_score[j]
                        temp_token = top_token[j]

                        top_score[j] = old_score
                        top_token[j] = old_t

                        old_score = temp_score
                        old_t = temp_token

                    top_score[i] = temp_score_lev
                    top_token[i] = t
                    break

        return top_token

    def calculate_levenshtein(self, query):
        query = self.preprocess_text(query)
        top_k_results = self._get_closest_levenstein(query, top_k=5)
        return top_k_results
