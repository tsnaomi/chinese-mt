import nltk


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

            print 'writing unigrams to file...'
            unigrams = 'unigrams = {\n'
            for k, v in self.unigrams.iteritems():
                unigrams += '    "%s": %s,\n' % (k, v)
            unigrams += '    }\n\n'
            f.write(unigrams)

            print 'writing bigrams to file...'
            bigrams = 'bigrams = {\n'
            for k, v in self.bigrams.iteritems():
                bigrams += '    ("%s", "%s"): %s,\n' % (k[0], k[1], v)
            bigrams += '    }\n\n'
            f.write(bigrams)

            print 'writing trigrams to file...'
            trigrams = 'trigrams = {\n'
            for k, v in self.trigrams.iteritems():
                if len(k) == 3:
                    trigrams += '    ("%s", "%s", "%s"): %s,\n' % \
                        (k[0], k[1], k[2], v)
                else:
                    trigrams += '    ("%s", "%s"): %s,\n' % (k[0], k[1], v)
            trigrams += '    }\n\n'
            f.write(trigrams)

            print 'writing total to file...'
            total = 'total = %s' % self.total
            f.write(total)


if __name__ == '__main__':
    print 'Training takes forever.'
    # this takes a few hours, uncomment at your own rish
    # Train()
