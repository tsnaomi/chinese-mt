# coding=utf-8

import nltk
import re
import subprocess

from defSelector import defSelector, getWord
from ngram import StupidBackoffTrigramLanguageModel
from pattern.en import lexeme, parse, referenced, superlative
from pprint import pprint
from PorterStemmer import PorterStemmer


# To get a baseline translation, pass kw='baseline' to translate().

def translate(
        filename='parser/dev-reordered-30-stp.txt',
        as_string=False,
        pre=False,
        post=True,
        kw='optimized',
        ):
    '''Return a Chinese to English translation.'''
    # get a word-by-word translation
    translation = baseline_translate(filename, pre, kw)

    if post:
        # apply post-processing strategies
        translation = postprocess(translation)

    # if as_string is True, convert translation into a string
    if as_string:
        translation = _translate_as_string(translation, prettify=False)

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
                        # translation.append([word, token[0], token[1]])
                        # continue
                        token = token[0]

                except (KeyError, IndexError):
                    # append the token itself
                    token = word

            if token:
                translation.append(token)

    return translation


def _translate_as_string(list_translation, prettify=True):
    # convert a list translation into a string translation
    string_translation = ' '.join(list_translation)

    if prettify:
        string_translation = _prettify(string_translation)

    string_translation = '.\n'.join(string_translation.split('. '))

    return string_translation


def _prettify(text):
    # remove sentence-onset tags
    text = text.replace('<S>', '')

    # affix possessive 's to previous word
    text = text.replace(' \'s', '\'s').replace('s\'s', 's\'')

    # remove improper whitespacing around punctuation
    text = text.replace(' ,', ',').replace('  ', ' ').replace(' .', '.')
    text = text.replace(' \'', '\'').replace('\n ', '\n')

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


def _parse(segmented_text):
    # create temporary file containting segmented text
    with ('temp.txt', 'w') as f:
        f.write(segmented_text)

    cmd = '/stanford-parser-full-2015-01-30/lexparser-lang.sh Chinese 30 '
    cmd += 'chineseFactored.ser.gz parsed temp.txt'

    # parse the segmented text
    parsed = subprocess.check_output(cmd, shell=True)

    # delete the temporary file
    subprocess.call('rm tempt.txt', shell=True)

    return parsed


def _reorder(parsed_text):   # TODO
    # from nltk.tree import Tree
    # from .parser.sentenceReorder import (
    #     reorder,
    #     substituteNormalNumbers,
    #     tree2TaggedSentence,
    #     )
    # from sentenceArranger import sentenceArranger

    # # reorder the sentences in the parsed file
    # parsed_strings = [s for s in parsed_text.split('\n\n') if s != '']
    # parsed_trees = [Tree.fromstring(s) for s in parsed_strings]

    # reordered_trees = [reorder(ptr) for ptr in parsed_trees]
    # sentences = [tree2TaggedSentence(ptr) for ptr in reordered_trees]

    # substituted = [substituteNormalNumbers(s) for s in sentences]

    # text = '\n'.join(substituted)

    # return text
    pass


# Post-Processing -------------------------------------------------------------


porter = PorterStemmer()
stupid = StupidBackoffTrigramLanguageModel()

with open('EnglishWords.txt') as f:
    EnglishWords = f.read()


def postprocess(text):
    '''Apply functions to a translation to achieve modest English fluency.'''
    # refine word-by-word lookup
    text = refine_lookup(text)

    # tokenize prettified string translation
    translation = _format_as_string(text)

    # apply genitive alternation
    translation = genitive_alternation(translation)

    # generate superlatives
    translation = render_superlatives(translation)

    # change negative determiners into negation
    translation = convert_negative(translation)

    # deal with the "under the sun" idiom
    translation = under_the_sun_idiom(translation)

    # position copulas before adverbs
    translation = finesse_copulas(translation)

    # inflect verbs
    translation = inflect_verbs(translation)

    # instert determiners
    translation = insert_determiners(translation)  # TODO

    return translation


def _format_as_string(text):
    # restore missing periods
    for i, word in enumerate(text[2:], 2):
        if word == '\n' and text[i-1] != '.':
            text[i-1] += '.'

    string = _translate_as_string(text, prettify=False)
    tokenized = nltk.word_tokenize(string)

    # add initial sentence-onset tag
    for i in range(len(tokenized[:-1])):
        if i == 0 or tokenized[i-1] == '.':
            tokenized[i] = '<S> ' + tokenized[i]

    # render sentence-onset tags their own token
    tokenized = ' '.join(tokenized).split(' ')

    return tokenized


def select_best_candidate(candidates):
    '''Using a stupid backoff trigram model, select the best candidate.'''
    # assumes that candidates is a list of tuples of the form:
    # ('previous-word target-word next-word', 'target-word')
    # here, the target word for the highest scored trigram is returned
    candidates = [(c[0].replace('  ', ' ').strip(), c[1]) for c in candidates]
    scores = [(stupid.score(c[0].split()), c[0], c[1]) for c in candidates]
    best = max(scores)
    # print scores, '\n', best, '\n'
    return best[2]


def refine_lookup(text):
    '''Select the best translation of a word, given several possibilities.'''
    for i, word in enumerate(text):

        if '/' in word:
            words = word.split('/')
            candidates = []
            previous = text[i-1] if i != 0 else ''
            next_ = text[i+1] if i != len(text) else ''

            if '/' in next_:
                next_ = next_.split('/')

                for n in next_:
                    candidates_ = [
                        ('%s %s %s' % (previous, w, n), w)
                        for w in words
                        ]

            else:
                candidates_ = [
                    ('%s %s %s' % (previous, w, next_), w)
                    for w in words
                    ]

            candidates.extend(candidates_)

            best = select_best_candidate(candidates)
            text[i] = best

    return text


def genitive_alternation(text):
    '''Apply the genitive for if it scores better than the posessive.

    The genitive alternation is the alternation between phrases of the
    'noun2 of noun1' and those of the form 'noun1 's noun2'.
    '''
    tagged = nltk.pos_tag(text)
    nouns = ('N', 'J')

    for i, word in enumerate(text):

        if word == '\'s' and tagged[i-1][1].startswith(nouns) and \
                tagged[i+1][1].startswith(nouns):
            noun1 = text[i-1]
            noun2 = text[i+1]
            candidates = [
                ('%s \'s %s' % (noun1, noun2), 'POS'),
                ('%s of %s' % (noun2, noun1), 'GEN'),
                ]

            best = select_best_candidate(candidates)

            if best == 'GEN':
                text[i-1] = noun2
                text[i] = 'of'
                text[i+1] = noun1

    return text


def render_superlatives(text):
    '''Conjugate English superlatives.'''
    for i, word in enumerate(text):

        if word == 'MOST' and i + 1 != len(text):
            text[i] = 'the'
            text[i+1] = superlative(text[i+1])

    return text


def convert_negative(text):
    '''Convert 'no' determiners into the negative 'not'.'''
    tagged = nltk.pos_tag(text)

    for i, word in enumerate(text):

        if word == 'no' and tagged[i][1] == 'DT':
            candidates = [
                ('no %s' % text[i+1], word),
                ('not %s' % text[i+1], 'not'),
                ]

            best = select_best_candidate(candidates)
            text[i] = best

    return text


def under_the_sun_idiom(text):
    '''Move adjunctal 'under the sun' idiom to the end of the clause.'''
    for i, word in enumerate(text):

        if word == 'under' and text[i+1] == 'the' and text[i+2] == 'sun':
            text[i], text[i+1], text[i+2] = '', '', ''

            index = i + 3
            while index + 1 != len(text) and text[index] not in '.,':
                index += 1

            text[index] = 'under the sun%s' % text[index]

    text = ' '.join(text).split()

    return text


def finesse_copulas(text):
    '''Position copulas before ADVs.'''
    tagged = nltk.pos_tag(text)

    for i, word in enumerate(text):

        if word == 'be':

            # remove marker-like copulas, which taggers interpret as nouns
            if tagged[i][1].startswith('N'):
                text[i] = ''

            # move copulas before adverbs
            elif i != 0 and tagged[i-1][1] == 'RB':

                prev = i - 1
                while i > 0 and tagged[prev][1] == 'RB':
                    prev -= 1

                text[i] = ''
                text[prev + 1] = 'be ' + text[prev + 1]

            # remove copulas preceding prepositional phrases
            # 'IN' is the tag for prepositions
            elif i + 1 <= len(text) and tagged[i+1][1] == 'IN':
                text[i] = ''

    return text


def inflect_verbs(text):
    '''Inflect verbs.'''
    tagged = nltk.pos_tag(text)

    for i, word in enumerate(text):

        if tagged[i][1].startswith('V'):
            paradigm = lexeme(word)
            negatives = ('n\'t', ' not')
            inflections = [v for v in paradigm if not v.endswith(negatives)]

            # preserve negation
            if word not in inflections:
                continue

            candidates = []

            for v in inflections:
                prev1 = text[i-2] if i > 1 else ''
                prev2 = text[i-1] if i > 1 else ''
                next_ = text[i+1] if i + 1 != len(text) else ''
                c = ('%s %s %s %s' % (prev1, prev2, v, next_), v)
                candidates.append(c)

            best = select_best_candidate(candidates)
            text[i] = best

    text = ' '.join(text).split()

    return text


def insert_determiners(text):
    '''Insert determiners'''
    tagged = nltk.pos_tag(text)
    modifiers = ('RB', 'JJ', 'CD', 'DT', 'POS', 'NN')

    for i, word in enumerate(text):
        tag = tagged[i][1]

        if tag.startswith(modifiers):

            if i == 0 or tagged[i-1][1].startswith(modifiers):
                continue

            if tag == 'DT' or tagged[i+1][1] == 'DT':
                continue

            previous = text[i-1] if i != 0 else ''
            next_ = text[i+1] if i + 1 != len(text) else ''
            a = referenced(word).split()[0]  # indefinite article
            candidates = [
                ('%s %s %s' % (previous, word, next_), ''),
                ('%s the %s %s' % (previous, word, next_), 'the '),
                ('%s %s %s %s' % (previous, a, word, next_), a),
                ]

            best = select_best_candidate(candidates)
            text[i] = best + word

    text = ' '.join(text).split()

    return text


# -----------------------------------------------------------------------------

if __name__ == '__main__':

    def execute_reordering():
        cmd = 'cd parser; python sentenceReorder.py; cd ..'
        subprocess.call(cmd, shell=True)

    execute_reordering()

    # tagged tranlsation
    print '\n\033[4mTagged translation\033[0m:\n'
    print nltk.pos_tag(translate('parser/dev-reordered-30-stp.txt'))

    # string translation with post-processing
    print '\n\033[4mString translation (with post-processing)\033[0m:\n'
    translation = translate(as_string=True)
    print '\n', translation

    # # string translation without post-processing
    # print '\n\033[4mString translation (no post-processing)\033[0m:\n'
    # translation2 = translate(as_string=True, post=False).replace('\n\n', '\n')
    # print translation2

    # # parsed translation
    # print parse(translation)
