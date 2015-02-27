import math

from nltk.corpus import brown


CORPUS = brown.sents(categories=brown.categories())


class StupidBackoffTrigramLanguageModel:

    def __init__(self, corpus=CORPUS):
        self.unigrams = {'UNK': 0, }
        self.bigrams = {'UNK': 0, }
        self.trigrams = {'UNK': 0, }
        self.total = 0
        self.train(corpus)

    def train(self, corpus):
        '''Train a stupid backoff language model using trigrams.'''
        for sentence in corpus:

            for i, word in enumerate(sentence):
                self.unigrams.setdefault(word, 0)
                self.unigrams[word] += 1
                self.total += 1

                if i > 0:
                    bigram = (sentence[i-1], word)
                    self.bigrams.setdefault(bigram, 0)
                    self.bigrams[bigram] += 1

                if i > 1:
                    trigram = (sentence[i-2], word)
                    self.trigrams.setdefault(trigram, 0)
                    self.trigrams[trigram] += 1

    def score(self, sequence):
        '''Given a list of words, return a log-probability of the sequence.'''
        score = 0.0

        for i, word in enumerate(sequence):
            C = word

            if i > 0:
                B = sequence[i-1]

                if i > 1:
                    A = sequence[i-2]
                    AB = (A, B)
                    ABC = (A, B, C)
                    ABC_count = self.trigrams.get(ABC, 0)

                    if ABC_count:
                        AB_count = self.bigrams[AB]
                        score += math.log(ABC_count)
                        score -= math.log(AB_count)
                        continue

                BC = (B, C)
                BC_count = self.bigrams.get(BC, 0)

                if BC_count:
                    B_count = self.unigrams[B]
                    score += math.log(BC_count * 0.4)
                    score -= math.log(B_count)
                    continue

            C_count = self.unigrams.get(C, 0) + 1
            score += math.log(C_count * 0.4)
            score -= math.log(self.total + len(self.unigrams))

        return score


if __name__ == '__main__':
    m3 = StupidBackoffTrigramLanguageModel()

    candidates = [
        'China was under the sun',
        'China is under the sun',
        'China to be under the sun',
        'China being under the sun',
        'China are under the sun',
        ]

    for t in candidates:
        print '\t%s: %s' % (t, m3.score(t.split()))
