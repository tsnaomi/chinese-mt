A Direct Machine Translation of Chinese

----

To get a semi-fluent translation of the development set, run the following command. This will return a translation that has undergone post-processing.

```
$ python baseline.py
```


To get a *baseline* (i.e., sans post-processing) translation of the development set, add the ```-baseline``` flag. This will return a word-for-word translation, composed of the first English word that appears in our dictionary for any given Chinese word.

```
$ python baseline.py -baseline
```

To get a baseline-like translation of the development set, but with all of the possible translations for a given Chinese word, use the ```-dict``` flag. If this flag is used, post-processing will not occur.

```
$ python baseline.py -dict
```


To get a translation that uses a refined word-for-word translation, but has not undergone post-processing, use the ```-post-false``` flag. Instead of returning the first possible translation for a given Chinese word, this will return the *best* translation, as determined by a Stupid Backoff Trigram language model.

```
$ python baseline.py -post-false
```

To translate the validation set, use ```-val```:

```
$ python baseline.py -val
```
