# coding=utf-8

import nltk
import re
import subprocess
import sys

from defSelector import defSelector, getWord
from ngram import StupidBackoffTrigramLanguageModel
from pattern.en import (
    conjugate,
    # lemma,
    lexeme,
    # parse,
    pluralize,
    referenced,
    suggest,
    superlative
    )


stupid = StupidBackoffTrigramLanguageModel()


def translate(filename, post=True, refined=True, baseline=False):
    '''Return a Chinese to English translation.'''
    # ensure that the pre-processed text is up-to-date
    execute_reordering()

    # get a word-by-word translation
    translation = baseline_translate(filename, refined, baseline)

    # tokenize prettified string translation
    translation = _prepare_as_string(translation)

    if post:
        # apply post-processing strategies
        translation = postprocess(translation)

    # convert translation into a string
    translation = _translate_as_string(translation)

    return translation


def baseline_translate(filename, refined=True, baseline=False):
    '''Return a primitive translation of a file from Chinese into English.

    This function produces a word-by-word translation.
    '''
    punctuation = '，。、'
    punct_dict = {'，': ',', '、': ',', '。': '.'}
    translation = []

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
                    # grab English translation(s) of the word
                    # change kw to "baseline" to get a baseline translation
                    token = defSelector(i, line, baseline)

                    # if token is a tuple, take only the first item in the
                    # tuple, which will be a verb
                    if isinstance(token, tuple):
                        token = token[0]

                except (KeyError, IndexError):
                    # append the token itself
                    token = word

            if token:
                translation.append(token)

    if refined:
        # refine the word-by-word translation by selecting the *best*
        # translation for each word
        translation = _refine_lookup(translation)

    return translation


def _refine_lookup(text):
    '''Select the best translation of a word, given several possibilities.

    This selection is done using a Stupid Backoff Trigram language model.
    '''
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


def _prepare_as_string(text):
    # restore missing periods
    for i, word in enumerate(text[2:], 2):
        if word == '\n' and text[i-1] != '.':
            text[i-1] += '.'

    string = _translate_as_string(text, prettify=False)
    tokenized = nltk.word_tokenize(string)

    # add sentence-onset tags
    for i in range(len(tokenized[:-1])):
        if i == 0 or tokenized[i-1] == '.':
            tokenized[i] = '<S> ' + tokenized[i]

    # render sentence-onset tags their own token
    tokenized = ' '.join(tokenized).split(' ')

    return tokenized


def _translate_as_string(list_translation, prettify=True):
    # convert a list translation into a string translation
    string_translation = ' '.join(list_translation)

    if prettify:
        string_translation = _prettify(string_translation)

    string_translation = '.\n'.join(string_translation.split('. '))

    return string_translation


def _prettify(text):
    # remove sentence-onset tags
    text = text.replace('<S> ', '')

    # affix possessive 's to previous word
    text = text.replace(' \'s', '\'s').replace('s\'s', 's\'')

    # remove improper whitespacing around punctuation
    text = text.replace(' ,', ',').replace('  ', ' ').replace(' .', '.')
    text = text.replace('\n ', '\n')

    # capitalize the first letter of each sentence
    lowercase = [m.end(0) for m in re.finditer(r'^|\. ', text)]
    for i in lowercase:
        text = text[:i] + text[i].upper() + text[i+1:]

    return text


# Pre-Processing --------------------------------------------------------------

def execute_reordering():
    '''Ensure that the pre-processed text is up-to-date.'''
    cmd = 'cd parser; python sentenceReorder.py; cd ..'
    subprocess.call(cmd, shell=True)


# Post-Processing -------------------------------------------------------------


def postprocess(translation):
    '''Apply functions to a translation to achieve modest English fluency.'''
    # strip clause marker
    translation = strip_complementizer(translation)

    # apply genitive alternation
    translation = alternate_pos_with_gen(translation)

    # generate superlatives
    translation = render_superlatives(translation)

    # change negative determiners into negation
    translation = convert_negatives(translation)

    # deal with the "under the sun" idiom
    translation = relocate_under_the_sun_idiom(translation)

    # position copulas before adverbs
    translation = finesse_copulas(translation)

    # pluralize nouns modified by cardinal numbers
    translation = pluralize_nouns(translation)

    equilibrium = None

    while equilibrium != translation:
        equilibrium = translation

        # inflect verbs
        translation = inflect_verbs(translation)

        # instert determiners
        translation = insert_determiners(translation)

    return translation


def select_best_candidate(candidates):
    '''Using a stupid backoff trigram model, select the best candidate.'''
    # assumes that candidates is a list of tuples of the form:
    # ('previous-word target-word next-word', 'target-word')
    # here, the target word for the highest scored trigram is returned
    candidates = [(c[0].replace('  ', ' ').strip(), c[1]) for c in candidates]
    scores = [(stupid.score(c[0].split()), c[0], c[1]) for c in candidates]
    best = max(scores)
    # print scores, '\n', 'winner: ', best, '\n'
    return best[2]


def strip_complementizer(text):
    for i, word in enumerate(text):

        if word == 'that':
            text[i] = ''

    return text


def alternate_pos_with_gen(text):
    '''Apply the genitive if it scores better than the posessive.

    The genitive alternation is the alternation between phrases of the
    'noun2 of noun1' and those of the form 'noun1 's noun2'.
    '''
    tagged = nltk.pos_tag(text)
    nouns = ('N', 'J')

    for i, word in enumerate(text):

        if word == '\'s' and tagged[i-1][1].startswith(nouns) and \
                tagged[i+1][1].startswith(nouns):

            x, X, noun = i - 1, i - 1, True
            while text[x] not in '<S>,':
                x -= 1

                if noun and tagged[x][1].startswith('N'):
                    X -= 1
                else:
                    noun = False

            y, Y, noun = i + 1, i + 1, True
            while text[y] not in ',.':
                y += 1

                if noun and tagged[y][1].startswith('N'):
                    Y += 1
                else:
                    noun = False

            # ignore stacked possessive constructions
            if ' '.join(text[x:y]).count('\'s') < 2:
                noun1 = ' '.join(text[X:i])
                noun2 = ' '.join(text[i+1:Y+1])
                candidates = [
                    ('%s \'s %s' % (noun1, noun2), 'POS'),
                    ('%s of %s' % (noun2, noun1), 'GEN'),
                    ]

                best = select_best_candidate(candidates)

                if best == 'GEN':
                    text[X:Y+1] = text[i+1:Y+1] + ['of', ] + text[X:i]

    return text


def render_superlatives(text):
    '''Conjugate English superlatives.'''
    for i, word in enumerate(text):

        if word == 'MOST' and i + 1 != len(text):
            text[i] = ''
            text[i+1] = superlative(text[i+1])

    return text


def convert_negatives(text):
    '''Finesse negative determiners and negation.'''
    tagged = nltk.pos_tag(text)

    for i, word in enumerate(text):

        if word == 'no' and tagged[i][1] == 'DT':
            candidates = [
                ('no %s' % text[i+1], word),
                ('not %s' % text[i+1], 'not'),
                ]

            best = select_best_candidate(candidates)
            text[i] = best
            continue

    return text


def relocate_under_the_sun_idiom(text):
    '''Move adjunctal 'under the sun' idiom to the end of the clause.'''
    for i, word in enumerate(text):

        if word == 'under' and text[i+1] == 'the' and text[i+2] == 'sun':
            text[i], text[i+1], text[i+2] = '', '', ''

            index = i + 3
            while index + 1 != len(text) and text[index] not in '.,':
                index += 1

            text[index] = 'under the sun %s' % text[index]

    text = ' '.join(text).split()

    return text


def finesse_copulas(text):
    '''Position copulas before ADVs and delete them before prepositions.'''
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

            # capture infinitives, but exclude the copula for how popular it is
            if text[i-1] != 'to' and word != 'be':

                x = i - 1
                while text[x] != ',' and text[x] != '<S>':
                    x -= 1

                if any(y[1].startswith('V') for y in tagged[x:i]):
                    inf = conjugate(word, tense='INFINITIVE')
                    to = (
                        '%s %s to %s' % (prev1, prev2, inf),
                        'to %s' % inf)
                    candidates.append(to)

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
            text[i] = '%s %s' % (best, word)

    text = ' '.join(text).split()

    return text


def pluralize_nouns(text):
    tagged = nltk.pos_tag(text)

    for i, word in enumerate(text[:-1]):

        if tagged[i][1] == 'CD' and word != 'one' and word != '1':

            nn = i + 1
            while not tagged[nn][1].startswith('N'):
                nn += 1

            # if the cardinal number is modifying a noun
            if tagged[nn][1].startswith('N'):

                # if the noun is not already plural
                if not tagged[nn][1].endswith('P'):
                    NS = pluralize(text[nn])
                    NS = suggest(NS)[0][0]
                    text[nn] = NS

    text = ' '.join(text).split()

    return text

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    args = sys.argv[1:]

    def get_filename():
        if '-test' in args:
            # translate the test set
            return 'parser/test-reordered-30-stp.txt'

        if '-val' in args:
            # translate the validation set
            return 'parser/redev-reordered-30-stp.txt'

        # translate the development set
        return 'parser/dev-reordered-30-stp.txt'

    def get_caption():
        if '-baseline' in args:
            return 'Baseline'

        elif '-dict' in args:
            return 'Verbose'

        elif '-post-false' in args:
            return 'Refined-lookup'

        return 'Post-processed'

    FILENAME = get_filename()
    CAPTION = get_caption()
    BASELINE = True if '-baseline' in args else False
    REFINED = False if '-dict' in args else True
    POST = False if '-post-false' in args or not REFINED or BASELINE else True

    print '\n\033[4m%s string translation\033[0m:\n' % CAPTION
    t = translate(FILENAME, post=POST, refined=REFINED, baseline=BASELINE)
    print '\n', t

    # # parsed translation
    # print '\n\033[4mParsed translation\033[0m:\n'
    # print '\n', parse(t, chunks=False)  # relations=True
