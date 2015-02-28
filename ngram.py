import math
import nltk


CORPUS = nltk.corpus.brown.sents(categories=nltk.corpus.brown.categories())


class StupidBackoffTrigramLanguageModel:

    def __init__(self, corpus=CORPUS[:1000]):
        try:
            from _ngrams import unigrams, bigrams, trigrams, total
            self.unigrams = unigrams
            self.bigrams = bigrams
            self.trigrams = trigrams
            self.total = total

        except ImportError:
            self.unigrams = {'UNK': 0, }
            self.bigrams = {('UNK', 'UNK'): 0, }
            self.trigrams = {('UNK', 'UNK', 'UNK'): 0, }
            self.total = 0
            self.train(corpus)

    def train(self, corpus):
        '''Train a stupid backoff language model using trigrams.'''
        try:
            from _ngrams import unigrams, bigrams, trigrams, total
            return unigrams, bigrams, trigrams, total

        except ImportError:
            pass

        for sent in corpus:

            # re-tokenize sentence to split punctuation from words,
            # e.g., Atlanta's -> Atlanta 's
            sent = nltk.word_tokenize(' '.join(sent))

            # get part-of-speech tags
            sent = nltk.pos_tag(sent)

            # convert all non- proper nouns into lowercase
            sent = [w[0].lower() if 'NNP' not in w[1] else w[0] for w in sent]

            # don't need </S> because both the brown corpus and our corpus use
            # periods at the end of sentences
            sentence = ['<S>', ] + sent

            for i, word in enumerate(sentence):
                self.unigrams.setdefault(word, 0)
                self.unigrams[word] += 1
                self.total += 1

                if i > 0:
                    bigram = (sentence[i-1], word)
                    self.bigrams.setdefault(bigram, 0)
                    self.bigrams[bigram] += 1

                if i > 1:
                    trigram = (sentence[i-2], sentence[i-1], word)
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

        # score /= max(len(sequence) - 2, 1)

        return score

if __name__ == '__main__':
    m3 = StupidBackoffTrigramLanguageModel()

    candidates = [
        # 'China was under the sun',
        # 'China is under the sun',
        # 'China to be under the sun',
        # 'China to been under the sun',
        # 'China has',
        # 'China to have',
        # 'is under',
        # 'to be under',
        # 'China being under the sun',
        # 'China are under the sun',
        # 'referring chopsticks\' genesis',
        # 'referring to chopsticks\' genesis',
        # 'referring to the chopsticks\' genesis',
        # 'referring to genesis of chopsticks',
        # 'referring to the genesis of chopstikcs',
        # 'regarding the chopsticks\' genesis',
        # 'regarding the genesis of chopsticks',
        # "China's trade",
        # "trade of China",
        # 'it am',
        # 'it be',
        # 'trade dispute',
        # 'trade is dispute',
        # 'use forks have',
        # 'use forks to have',
        # 'China be',
        # 'a China be',
        # 'the China be',
        # 'China is',
        # 'a China is',
        # 'the China is',
        # 'China is a',
        'first state',
        'first a state',
        'first the state',
        ]

    for t in candidates:
        print '\t%s: %s' % (t, m3.score(t.split()))
