A Direct Machine Translation of Chinese

----

To use baseline.py:

```
from baseline import baseline_translate

# get a list representation of the baseline translation of the dev set
bt = baseline_translate('segmented-ctb-dev.txt')

# get a string representation of the baseline translation of the dev set
bt = baseline_translate('segmented-ctb-dev.txt', as_string=True)
```

To demo how baseline.py handles the dev set, call this in your command line:

```
python baseline.py
```