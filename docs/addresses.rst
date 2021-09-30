
Addresses
=========

Address detection is hard, despite the fact it may seem simple on the surface.
We use the `pyap <https://github.com/vladimarius/pyap>`_ package to detect addresses and `libpostal <https://github.com/openvenues/libpostal>`_ to verify them.
This is implemented in ``scrubadub_address.address.AddressDetector``, which is in a separate package and not enabled by default due to its dependencies on these two libraries.
We currently support British, American and Canadian addresses.

Installation
------------

First libpostal needs to be installed.
Full instructions can be found in the `libpostal documentation <https://github.com/openvenues/libpostal#installation-maclinux>`_, but a summary is given below for linux installation:

.. code-block:: console

    $ sudo apt-get install curl autoconf automake libtool pkg-config
    $ git clone https://github.com/openvenues/libpostal
    $ cd libpostal
    $ ./bootstrap.sh
    $ ./configure --prefix=/usr/local/
    $ make -j4
    $ sudo make install

Once you have installed libpostal, the remaining python dependencies can be installed:

.. code-block:: console

    $ pip install scrubadub_address

This will also bring along the ``pypostal`` and ``pyap`` python packages as dependencies.

Usage
-----

Once the dependencies are installed you can import the detector and add it to your ``Scrubber`` as shown below:

.. code-block:: pycon

    >>> import scrubadub, scrubadub_address
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub_address.detectors.AddressDetector)
    >>> scrubber.clean("I live at 6919 Bell Drives, East Jessicastad, MO 76908")
    'I live at {{ADDRESS}}'
