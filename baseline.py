# coding=utf-8

import subprocess

from dictionary import dictionary


def baseline_translate(filename, as_string=False, segment=False):
    '''Return a primitive translation of a file from Chinese into English.

    This function produces a word-by-word translation. If 'as_string' is True,
    the translation is returned as a string. Otherwise, the translation is
    returned as a list.

    If 'segment' is True, the Stanford segmenter will be used to segment the
    file. Therefore, if 'segment' is False, the file specified by filename
    should already be segmented. Beware: the segmenter is a tad slow.
    '''
    punctuation = '，。、'
    punct_dict = {'，': ',', '、': ',', '。': '.'}
    translation = []

    if segment:
        segmented = _segment(filename)
        text = segmented.split()

    else:

        # open the file to be translated
        with open(filename, 'r') as f:
            lines = f.readlines()
            text = ' '.join(lines)
            text = text.split()

    for t in text:

        if t in punctuation:
            # keep punctuation in translation
            translation.append(punct_dict[t])

        else:

            try:
                # grab first English translation of word
                word = dictionary[t][0][0]
                translation.append(word)

            except IndexError:
                # append the Chinese token itself
                translation.append(t)

    # if as_string is True, convert translation into a string
    if as_string:
        translation = ' '.join(translation)
        translation = translation.replace(' ,', ',').replace(' .', '.')

    return translation


def _segment(filename):
    # segment the specified file using the Stanford segmenter
    cmd = 'stanford-segmenter-2015-01-30/segment.sh ctb %s UTF-8 0' % filename
    segmented = subprocess.check_output(cmd, shell=True)

    return segmented


if __name__ == '__main__':
    print baseline_translate('segmented-ctb-dev.txt', as_string=True)
