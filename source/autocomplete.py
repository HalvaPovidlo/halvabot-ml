from string import punctuation
import Levenshtein as lev


class Autocomplete:
    def __init__(self, titles):
        self.corpus = titles
        self.corpus_prp = [self.preprocess_text(doc) for doc in self.corpus]
        self.uniq_words_corpus = self.corpus_prp

    def preprocess_text(self, text):
        tokens = text.lower().split(" ")

        tokens = [token for token in tokens if token != " " and token.strip() not in punctuation]
        text = " ".join(tokens)
        return text

    def compute_df(self, word, corpus):
        return sum([1.0 for i in corpus if word in i]) / len(corpus)

    def _get_closest_levenstein_word(self, token, top_k=10):
        top_token = [" " for _ in range(top_k)]
        top_score = [0.0 for _ in range(top_k)]

        for t in self.uniq_words_corpus:
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

        return [top_token, top_score]

    def calculate_levenshtein(self, word, a=0.9):
        top_k_words, top_k_scores = self._get_closest_levenstein_word(word, top_k=5)
        d = {}
        for t, sc in zip(top_k_words, top_k_scores):
            new_score = self.compute_df(t, self.corpus_prp) * a + sc * (1 - a)
            d.update({t: new_score})
        sort_top_k = sorted(d.items(), key=lambda item: item[1], reverse=True)
        result = [w[0] for w in sort_top_k]
        return result
