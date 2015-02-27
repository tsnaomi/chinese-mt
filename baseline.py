# coding=utf-8

import nltk
import re
import subprocess

from defSelector import defSelector, getWord
# from nltk.tree import Tree
from ngram import StupidBackoffTrigramLanguageModel
# from .parser.sentenceReorder import (
#     reorder,
#     substituteNormalNumbers,
#     tree2TaggedSentence,
#     )
from PorterStemmer import PorterStemmer
# from sentenceArranger import sentenceArranger


# To get a baseline translation, pass kw='baseline' to translate().

def translate(filename, as_string=False, preprocess=False, kw='optimized'):
    '''Return a Chinese to English translation.'''
    # get a word-by-word translation
    translation = baseline_translate(filename, preprocess, kw)

    if kw == 'optimized':

        # for words that have several possible translations, select the best
        # possible translation given its context (the previous and following
        # words)
        translation = select_best(translation)

        # position copulas before adverbs and delete copulas preceding
        # prepositions
        translation = finesse_copulas(translation)

        # add gerunds to clause-initial verbs
        translation = gerundize_verbs(translation)

    # if as_string is True, convert translation into a string
    if as_string:
        translation = translate_as_string(translation)

    return translation


def baseline_translate(filename, preprocess, kw):
    '''Return a primitive translation of a file from Chinese into English.

    This function produces a word-by-word translation.

    If 'preprocess' is True, the file's contents will be segmented (using the
    Stanford segmenter), and parsed (using the Stanford parser), and
    re-arranged to become more English-like.

    Therefore, if 'preprocess' is False, the file specified by fileness should
    already be segmented, parsed, and reordered. Beware: segmenting, parsing,
    and reordering is a slow ordeal.
    '''
    punctuation = '，。、'
    punct_dict = {'，': ',', '、': ',', '。': '.'}
    translation = []

    if preprocess:
        # segment, parse, and re-arrange the words to be translated
        text = preprocess(filename)
        text = text.splitlines(True)

    else:
        # open the file to be translated
        with open(filename, 'r') as f:
            text = f.readlines()

    for line in text:
        # split sentence into a list
        line = line.strip(' ').replace('\n', ' \n').split(' ')

        # rearrange sentence to make it English-comprehensible
        # change kw to 'baseline' to get a baseline translation
        # line = sentenceArranger(line, kw)

        for i, word in enumerate(line):

            word = getWord(word)

            if word in punctuation:
                # preserve punctuation in translation
                token = punct_dict[word]

            else:

                try:
                    # grab the best English translation of a word
                    # change kw to "baseline" to get a baseline translation
                    token = defSelector(i, line, kw)

                    # if the token is a verb, append the Chinese word, English
                    # verb, and the inflection
                    if isinstance(token, tuple):
                        translation.append([word, token[0], token[1]])
                        continue

                except (KeyError, IndexError):
                    # append the token itself
                    token = word

            translation.append([word, token])

    return translation


def translate_as_string(list_translation):
    # convert a list translation into a string translation
    string_translation = [t[1] for t in list_translation]
    string_translation = ' '.join(string_translation)
    string_translation = _prettify(string_translation)

    return string_translation


def _prettify(text):
    # remove improper whitespacing around punctuation
    text = text.replace(' ,', ',').replace('  ', ' ').replace(' .', '.')
    text = text.replace('\n ', '\n')

    # capitalize the first letter of each sentence
    naughty_lowercase = [m.end(0) for m in re.finditer(r'^|\n', text)][:-1]
    for i in naughty_lowercase:
        text = text[:i] + text[i].upper() + text[i+1:]

    return text


# Pre-Processing --------------------------------------------------------------

def preprocess(filename):
    '''Segment, parse, and reorder the words in the specified file.'''
    segmented = _segment(filename)
    # parsed = _parse(segmented)
    # reordered = _reorder(parsed)

    # return reordered
    return segmented


def _segment(filename):
    # segment the specified file using the Stanford segmenter
    cmd = 'stanford-segmenter-2015-01-30/segment.sh ctb %s UTF-8 0' % filename
    segmented = subprocess.check_output(cmd, shell=True)

    return segmented


# def _parse(segmented_text):
#     # create temporary file containting segmented text
#     with ('temp.txt', 'w') as f:
#         f.write(segmented_text)

#     cmd = '/stanford-parser-full-2015-01-30/lexparser-lang.sh Chinese 30 '
#     cmd += 'chineseFactored.ser.gz parsed temp.txt'

#     # parse the segmented text
#     parsed = subprocess.check_output(cmd, shell=True)

#     # delete the temporary file
#     subprocess.call('rm tempt.txt', shell=True)

#     return parsed


# def _reorder(parsed_text):
#     # reorder the sentences in the parsed file
#     parsed_strings = [s for s in parsed_text.split('\n\n') if s != '']
#     parsed_trees = [Tree.fromstring(s) for s in parsed_strings]

#     reordered_trees = [reorder(ptr) for ptr in parsed_trees]
#     sentences = [tree2TaggedSentence(ptr) for ptr in reordered_trees]

#     substituted = [substituteNormalNumbers(s) for s in sentences]

#     text = '\n'.join(substituted)

#     return text


# Post-Processing -------------------------------------------------------------

porter = PorterStemmer()
stupid = StupidBackoffTrigramLanguageModel()

with open('EnglishWords.txt') as f:
    EnglishWords = f.read()


def select_best(text):
    '''Select the best translation of a word, given several possibilities.'''
    for i, word in enumerate(text):

        if '/' in word[1]:
            words = word[1].split('/')

            candidates = [
                ('%s %s %s' % (
                    text[i-1][1] if i != 0 else '',  # previous word
                    w,
                    text[i+1][1] if i != len(text) else ''  # next word
                    ), w)
                for w in words
                ]

        best = _best_candidate(candidates)

        text[i][1] = best

    return text


def _best_candidate(candidates):
    # assumes that candidates is a list of tuples of the form:
    # ('previous-word target-word next-word', 'target-word')
    # here, the target word for the highest scored trigram is returned
    return max((stupid.score(c[0]), c[1]) for c in candidates)[1]


def finesse_copulas(text):
    '''Position copulas before ADVs and delete copulas that precede Ps.'''
    # wrapper around nltk.pos_tag, which only accepts a tokenized list of words
    tag = lambda w: nltk.pos_tag([w, ])[0][1]

    for i, word in enumerate(text):

        if word[1] == 'be':

            # move copulas before adverbs
            if i != 0 and tag(text[i-1][1]) == 'RB':

                prev = i - 1
                while i > 0 and tag(text[prev][1]) == 'RB':
                    prev -= 1

                text.pop(i)
                text.insert(prev + 1, word)

            # remove copulas preceding prepositional phrases
            # 'IN' is the tag for prepositions
            elif len(text) >= i + 1 and tag(text[i+1][1]) == 'IN':
                text.pop(i)

    return text


def gerundize_verbs(text):
    '''Have sentence-initial verbs take gerunds.'''
    # wrapper around nltk.pos_tag, which only accepts a tokenized list of words
    tag = lambda w: nltk.pos_tag([w, ])[0][1]

    for i, word in enumerate(text):

        # if the word is clause-initial...
        if i == 0 or text[i-1][1] == '\n' or text[i-1][1] == ',':

            # # if the word is a verb...
            if tag(word[1]).startswith(('V', 'NN')):  # REFINE
                stemmed = porter.stem(word[1])
                gerundive1 = stemmed + 'ing'
                gerundive2 = stemmed + stemmed[-1] + 'ing'

                if gerundive1 in EnglishWords:
                    text[i][1] = gerundive1

                elif gerundive2 in EnglishWords:
                    text[i][1] = gerundive2

    return text

# TODO
# 1. inflect nouns, e.g., plurality, case (n-grams) (N)
# 2. select accurate determiners (n-grams) (N)
# 3. inflect verbs, e.g., gerunds, infinitives (n-grams) (N)
# 4. select best prepositions (n-grams) (N)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    print '\n\033[4mList translation\033[0m:\n'
    print translate('parser/dev-reordered-30-stp.txt')
    print '\n\033[4mString translation\033[0m:\n'
    print translate(
        'parser/dev-reordered-30-stp.txt',
        as_string=True,
        kw='optimized',
        )
