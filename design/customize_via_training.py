"""scrubadub currently removes personally identifiable information with some
regular expression and natural language processing techniques. These techniques
work very well in a wide range of circumstances, but they also tend to make
mistakes.

For example, the first sentence should obfuscate the name 'April' and
the second sentence should not obfuscate the month 'April'.

April is a good friend of mine. I hope to see her in April.

To make this possible, scrubadub needs to be able to incorporate some
techniques for training a classifier to identify filth. The training interface
is important and probably not something that is best done in a terminal, but it
is important that the technical infrastructure is there for it to work.
"""

import scrubadub

# a TrainedScrubber can be taught what is dirty about a particular document.
scrubber = scrubadub.TrainedScrubber()
for document in training_documents:

    # TrainedScrubber.detect_filth just returns a list of filth objects that
    # are returned by Scrubber.iter_filth. This is used to help make
    # classification easy for end users.
    filth_list = scrubber.detect_filth(document)

    # The filth_list is then refined by human input. It is very difficult to
    # imagine doing this in a terminal in an effective way (although `git add
    # -i` might be a decent example). I imagine that person_identifies_filth is
    # a web interface where users can easily brush text to improve recall and
    # adjust the preliminary filth_list to improve precision.
    filth_list = person_identifies_filth(document, filth_list)

    # The TrainedScrubber.train method should incorporate the filth_list into
    # its classifier and further return a cleaned document with the filth
    # removed in an appropriate way.
    cleaned_document = scrubber.train(document, filth_list)

# the TrainedScrubber.predict (or maybe just TrainedScrubber.clean?) method is
# then used to use the classifier to selectively clean filth based on the human
# input. This way, you might only have to train ~1000 documents to do a good
# job of scrubbing the rest (imagine having to do this for 1mm documents)
for document in test_documents:
    clean_document = scrubber.predict(document)
