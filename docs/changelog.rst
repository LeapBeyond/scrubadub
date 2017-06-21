Change Log
==========

This project uses `semantic versioning <http://semver.org/>`_ to
track version numbers, where backwards incompatible changes
(highlighted in **bold**) bump the major version of the package.


latest changes in development for next release
----------------------------------------------

.. THANKS FOR CONTRIBUTING; MENTION WHAT YOU DID IN THIS SECTION HERE!

* bug fixes:

  * fixed documentation (`#32`_ via `@ivyleavedtoadflax`_)

1.2.0
-----

* added python 3 compatability (`#31`_ via `@davidread`_)

1.1.1
-----

* fixed ``FilthMergeError`` (`#29`_ via `@hugofvs`_)

1.1.0
-----

* regular expression detection of Social Security Numbers (`#17`_)

* Added functionality to keep ``replace_with = "identifier"`` (`#21`_)

* several bug fixes, including:

   * inaccurate name detection (`#19`_)

1.0.3
-----

* minor change to force ``Detector.filth_cls`` to exist (`#13`_)

1.0.1
-----

* several bug fixes, including:

  * installation bug (`#12`_)

1.0.0
-----

* **major update to process Filth in parallel** (`#11`_)

0.1.0
-----

* added skype username scrubbing (`#10`_)

* added username/password scrubbing (`#4`_)

* added phone number scrubbing (`#3`_)

* added URL scrubbing, including URL path removal (`#2`_)

* make sure unicode is passed to ``scrubadub`` (`#1`_)

* several bug fixes, including:

  * accuracy issues with things like "I can be reached at 312.456.8453" (`#8`_)

  * accuracy issues with usernames that are email addresses (`#9`_)


0.0.1
-----

* initial release, ported from past projects

.. list of contributors that are linked to above. putting links here
   to make the text above relatively clean

.. _@davidread: https://github.com/davidread
.. _@deanmalmgren: https://github.com/deanmalmgren
.. _@hugofvs: https://github.com/hugofvs
.. _@ivyleavedtoadflax: https://github.com/ivyleavedtoadflax


.. list of issues that have been resolved. putting links here to make
   the text above relatively clean

.. _#1: https://github.com/datascopeanalytics/scrubadub/issues/1
.. _#2: https://github.com/datascopeanalytics/scrubadub/issues/2
.. _#3: https://github.com/datascopeanalytics/scrubadub/issues/3
.. _#4: https://github.com/datascopeanalytics/scrubadub/issues/4
.. _#8: https://github.com/datascopeanalytics/scrubadub/issues/8
.. _#9: https://github.com/datascopeanalytics/scrubadub/issues/9
.. _#10: https://github.com/datascopeanalytics/scrubadub/issues/10
.. _#11: https://github.com/datascopeanalytics/scrubadub/issues/11
.. _#12: https://github.com/datascopeanalytics/scrubadub/issues/12
.. _#13: https://github.com/datascopeanalytics/scrubadub/issues/13
.. _#17: https://github.com/datascopeanalytics/scrubadub/issues/17
.. _#19: https://github.com/datascopeanalytics/scrubadub/issues/19
.. _#21: https://github.com/datascopeanalytics/scrubadub/issues/21
.. _#29: https://github.com/datascopeanalytics/scrubadub/issues/29
.. _#31: https://github.com/datascopeanalytics/scrubadub/pull/31
.. _#32: https://github.com/datascopeanalytics/scrubadub/pull/32
