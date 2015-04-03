> This package is a work in progress and has not yet been posted on pypi

# scrubadub

Remove personally identifiable information from free text. Sometimes
we have additional metadata about the people we wish to
anonymize. Other times we don't. This package makes it easy to
seamlessly scrub personal information from these records


## From the command line

Using `scrubadub` from the command line makes it easy to remove
personal information from files.

```sh
echo "John is a cat" > private.txt

# Replace names with {{NAME}} placeholder
scrubadub private.txt                           # {{NAME}} is a cat

# Replace names with {{NAME-ID}} placeholder to be consistent across records
scrubadub --anonymous private.txt               # {{NAME-2351}} is a cat

# Replace names with random, gender-consistent names
scrubadub --replace private.txt                 # Jason is a cat

# its not uncommon to have additional information about the people in
# the dataset you are trying to scrub. For example, they might be your
# users.
echo "username,first_name,last_name,species,city,state" > metadata.csv
echo "jsmith1,John,Smith,cat,Chicago,IL" >> metadata.csv

# we can then use this information to be particularly careful to omit
# the details about these users from the resulting data
scrubadub --metadata=metadata.csv private.txt   # {{first_name}} is a {{species}}

# When combined with textract (http://textract.readthedocs.org)...
textract letter_to_your_mother.doc | scrubadub  # total anonymity
textract letter_to_senator.pdf | scrubadub      # who sent that anyway?
```

## From python

Of course, since `scrubadub` is written in python, it is easy to
incorporate it into your existing python scripts.

```python
import scrubadub

text = "John is a cat"

# similar to the command line, you can use any particular method to
# scrub personal information from text
placeholder_text = scrubadub.clean(text)
anonymous_text = scrubadub.clean(text, method="anonymous")
replace_text = scrubadub.clean(text, method="replace")


# for more fine-grained control, you can subclass Scrubber and adapt
# your approach for your particular data set.
class NoEmailScrubber(scrubadub.Scrubber):
	def clean_email(self, text):
		return text

see_my_email_address = scrubadub.clean_email(text, cls=NoEmailScrubber)
```


## Getting started

1. Create a python virtual environment and install the requirements

    ```
    mkvirtualenv scrubadub
    pip install -r REQUIREMENTS
    ```

## Related work

`scrubadub` isn't the first package to attempt to remove personally
identifiable information from free text. There are a handful of other
projects out there that have very similar aims and which provide some
inspiration for how `scrubadub` should work.

- [MITRE](http://mist-deid.sourceforge.net/) gives the
    ability to replace names with a placeholder like `[NAME]` or alternatively
    replace names with fake names. last release in 8/2014. not on github.
    unclear what language although it looks like python. it is clear that the
    documentation sucks and is primarily intended for academic audiences (docs
    are in papers).

- [physionet has a few deidentification
    packages](http://www.physionet.org/physiotools/software-index.shtml#deid)
    that look pretty decent but are both written in perl and require advance
    knowledge of what you are trying to replace. Intended for HIPAA regulations.
    In particular, [deid](http://www.physionet.org/physiotools/deid/) has some
    good lists of names that might be useful in spite of the fact it has 5k+
    lines of gross perl.
