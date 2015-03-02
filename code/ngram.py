import math
import nltk

from _ngrams import unigrams, bigrams, trigrams, total


CORPUS = nltk.corpus.brown.sents(categories=nltk.corpus.brown.categories())


class Train:

    def __init__(self, corpus=CORPUS):
        self.unigrams = {'UNK': 0, }
        self.bigrams = {('UNK', 'UNK'): 0, }
        self.trigrams = {('UNK', 'UNK', 'UNK'): 0, }
        self.total = 0
        self.train(corpus)
        self.dump()

    def train(self, corpus):
        '''Train a stupid backoff language model using trigrams.'''
        print 'Training takes forever.'

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

    def dump(self):
        '''Dump ngram data into file.'''
        with open('__ngrams.py', 'w') as f:

            print 'Writing unigrams to file...'
            unigrams_ = 'unigrams = {\n'
            for k, v in self.unigrams.iteritems():
                unigrams_ += '    "%s": %s,\n' % (k, v)
            unigrams_ += '    }\n\n'
            f.write(unigrams_)

            print 'Writing bigrams to file...'
            bigrams_ = 'bigrams = {\n'
            for k, v in self.bigrams.iteritems():
                bigrams_ += '    ("%s", "%s"): %s,\n' % (k[0], k[1], v)
            bigrams_ += '    }\n\n'
            f.write(bigrams_)

            print 'Writing trigrams to file...'
            trigrams_ = 'trigrams = {\n'
            for k, v in self.trigrams.iteritems():
                if len(k) == 3:
                    trigrams_ += '    ("%s", "%s", "%s"): %s,\n' % \
                        (k[0], k[1], k[2], v)
                else:
                    trigrams_ += '    ("%s", "%s"): %s,\n' % (k[0], k[1], v)
            trigrams_ += '    }\n\n'
            f.write(trigrams_)

            print 'writing total to file...'
            total_ = 'total = %s' % self.total
            f.write(total_)


class StupidBackoffTrigramLanguageModel:

    def __init__(self, corpus=CORPUS[:1000]):
        self.unigrams = unigrams
        self.bigrams = bigrams
        self.trigrams = trigrams
        self.total = total

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
    m = StupidBackoffTrigramLanguageModel()

    candidates = [
        'using chopsticks have a',
        'using chopsticks has a',
        'using chopsticks having a',
        'using chopsticks had a',
        'using chopsticks to have a',
        'using chopsticks to have',
        ]

    for t in candidates:
        print '\t%s: %s' % (t, m.score(t.split()))
