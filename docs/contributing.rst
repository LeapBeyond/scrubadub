.. _contributing:

Contributing
============

The overarching goal of this project is to remove personally identifiable
information from raw text as reliably as possible. In practice, this means that
this project, by default, will preferentially be overly conservative in removing
information that might be personally identifiable. As this project matures, I
fully expect the project to become ever smarter about how it interprets and
anonymizes raw text.

Regardless of which personal information is identified, this project is committed
to being as agnostic about the manner in which the text is anonymized, so long
as it is done with rigor and does not inadvertantly lead to `improper
anonymization <https://medium.com/@vijayp/of-taxis-and-rainbows-f6bc289679a1>`_.
Replacing with placholders? Replacing with anonymous (but consistent) IDs?
Replacing with random metadata? Other ideas? All should be supported to make
this project as useful as possible to the people that need it.

Another important aspect of this project is that we want to have extremely good
documentation and source code that is easy to read. If you notice a type-o,
error, confusing statement etc, please fix it!


.. _contributing-quick-start:

Quick start
-----------

1. `Fork <https://github.com/LeapBeyond/scrubadub/fork>`_ and clone the
   project:

   .. code-block:: bash

        git clone https://github.com/YOUR-USERNAME/scrubadub.git

2. Create a python virtual environment and install the requirements

   .. code-block:: bash

       mkvirtualenv scrubadub
       pip install -r requirements/python-dev

3. Contribute! There are several `open issues
   <https://github.com/LeapBeyond/scrubadub/issues>`_ that provide
   good places to dig in. Check out the `contribution guidelines
   <https://github.com/LeapBeyond/scrubadub/blob/master/CONTRIBUTING.md>`_
   and send pull requests; your help is greatly appreciated!

4. Run the test suite that is defined in ``.travis.yml`` to make sure
   everything is working properly

   .. code-block:: bash

       ./tests/run.py

   Current build status: |Build Status|

.. |Build Status| image:: https://travis-ci.org/LeapBeyond/scrubadub.png
   :target: https://travis-ci.org/LeapBeyond/scrubadub
