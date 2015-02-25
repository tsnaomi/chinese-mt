# coding=utf-8

import re
import subprocess

# from dictionary import dictionary
from defSelector import defSelector, getWord
from sentenceArranger import sentenceArranger


def baseline_translate(filename, as_string=False, segment=False):
    '''Return a primitive translation of a file from Chinese into English.

    This function produces a word-by-word translation. If 'as_string' is True,
    the translation is returned as a string. Otherwise, the translation is
    returned as a list.

    If 'segment' is True, the Stanford segmenter will be used to segment the
    file. Therefore, if 'segment' is False, the file specified by filename
    should already be segmented. Beware: the segmenter is a tads slow.
    '''
    punctuation = '，。、'
    punct_dict = {'，': ',', '、': ',', '。': '.'}
    translation = []

    if segment:
        # segment the file to be translated
        segmented = _segment(filename)
        text = segmented.splitlines(True)

    else:
        # open the file to be translated
        with open(filename, 'r') as f:
            text = f.readlines()

    for line in text:

        # split sentence into a list
        line = line.strip(' ').replace('\n', ' \n').split(' ')

        # rearrange sentence to make it English-comprehensible
        # change 'optimized' to 'baseline' to get a baseline translation
        line = sentenceArranger(line, 'optimized')

        for i in xrange(len(line)):

            word = getWord(line[i])

            if word in punctuation:
                # preserve punctuation in translation
                token = punct_dict[word]

            else:

                try:

                    # grab the best English translation of a word
                    # (change 'optimized' to "baseline" to get a baseline
                    # translation)
                    token = defSelector(i, line, 'optimized')

                    # if the token is a verb, append the Chinese word, English
                    # verb, and the inflection
                    if isinstance(token, tuple):
                        translation.append([word, token[0], token[1]])
                        continue

                except (KeyError, IndexError):
                    # append the token itself
                    token = word

            translation.append([word, token])

    # if as_string is True, convert translation into a string
    if as_string:
        translation = _translate_as_string(translation)

    return translation


def _segment(filename):
    # segment the specified file using the Stanford segmenter
    cmd = 'stanford-segmenter-2015-01-30/segment.sh ctb %s UTF-8 0' % filename
    segmented = subprocess.check_output(cmd, shell=True)

    return segmented


def _translate_as_string(list_translation):
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


if __name__ == '__main__':
    print '\n\033[4mList translation\033[0m:\n'
    print baseline_translate('tagger/tagged_dev.txt')
    print '\n\033[4mString translation\033[0m:\n'
    print baseline_translate('tagger/tagged_dev.txt', as_string=True)
