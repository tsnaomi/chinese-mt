A Direct Machine Translation of Chinese

----

To use baseline.py:

```
from baseline import baseline_translate

# get a list representation of the baseline translation of the dev set
# here, bt is a list of lists, with the latter of the form ['说到', 'refer']
bt = baseline_translate('segmented-ctb-dev.txt')

# get a string representation of the baseline translation of the dev set
bt = baseline_translate('segmented-ctb-dev.txt', as_string=True)
```

If you keep the translation as a list of lists, you can later call _translate_as_string() to get a string representation:

```
from baseline import _translate_as_string

list_translation = [['说到', refer], ['筷子', 'chopsticks'], ]

string_translation = _translate_as_string(list_translation)
```

To demo how baseline.py handles the dev set, call this in your command line:

```
python baseline.py
```