Any and all contributions are welcome and appreciated. To make it easy
to keep things organized, this project uses the
[general guidelines](https://help.github.com/articles/using-pull-requests)
for the fork-branch-pull request model for github. Briefly, this means:

1. Make sure your fork's `master` branch is up to date:

    	git remote add LeapBeyond https://github.com/LeapBeyond/scrubadub.git
        git checkout master
        git pull LeapBeyond/master

2. Start a feature branch with a descriptive name about what you're trying
   to accomplish:

        git checkout -b italian-name-fix

3. Make commits to this feature branch (`italian-name-fix`, in this case)
   in a way that other people can understand with good commit message
   to explain the changes you've made:

        emacs scrubadub/__init__.py
	    git add scrubadub/__init__.py
	    git commit -m 'added italian name fix'

4. If an issue already exists for the code you're contributing, use
   [issue2pr](http://issue2pr.herokuapp.com/) to attach your code to that issue:

        git push origin italian-name-fix
		chrome http://issue2pr.herokuapp.com
		# enter the issue URL, HEAD=yourusername:italian-name-fix, Base=master

   If the issue doesn't already exist, just send a pull request in the
   usual way:

        git push origin italian-name-fix
		chrome http://github.com/LeapBeyond/scrubadub/compare


Style guidelines
----------------

As a general rule of thumb, the goal of this package is to be as
readable as possible to make it easy for novices and experts alike to
contribute to the source code in meaningful ways. Pull requests that
favor cleverness or optimization over readability are less likely to be
incorporated.

To make this notion of "readability" more concrete, here are a few
stylistic guidelines that are inspired by other projects and we
generally recommend:

-  write functions and methods that can `fit on a screen or two of a
   standard
   terminal <https://www.kernel.org/doc/Documentation/CodingStyle>`_
   --- no more than approximately 40 lines.

-  unless it makes code less readable, adhere to `PEP 8
   <http://legacy.python.org/dev/peps/pep-0008/>`_ style
   recommendations --- use an appropriate amount of whitespace. This
   is enforced in the test suite

- `code comments should be about *what* and *why* is being done, not *how* it is
  being done <https://www.kernel.org/doc/Documentation/CodingStyle>`_ ---
  that should be self-evident from the code itself.


Common contributions: Removing a new type of filth
--------------------------------------------------

This project has really taken off, much more so than I would have thought
(thanks everybody!). One very common contribution is adding a new type of filth
that should be removed by `scrubadub`. To make it as easy as possible to add
these types of contributions, I thought I'd jot down a few notes about how to
add a new type of filth, for example, addresses.

* Create an appropriately named python file in `scrubadub/filth/` and write a
  new `Filth` class that inherits from `scrubadub.filth.base.Filth`. In this
  case, perhaps you'd create an `AddressFilth` class in
  `scrubadub/filth/address.py`

* Add your new type of `Filth` to the `scrubadub.filth` namespace by importing
  it in `scrubadub/filth/__init__.py`

* Create an appropriately named python file in `scrubadub/detectors/` and write
  a new `Detector` class that inherits from
  `scrubadub.detectors.base.Detector`. In this case, perhaps you'd create an
  `AddressDetector` class in `scrubadub/detectors/address.py`.

* Add your new type of `Detector` to the `scrubadub.detectors` namespace by
  importing it in `scrubadub/detectors/__init__.py`.

* Register your new detector by adding it to the `types` dictionary in
  `scrubadub/detectors/__init__.py`

* Create a new python file to handle some tests for your particular type of
  filth. In this case, perhaps you would write your tests in
  `tests/test_addresses.py`

* Add documentation for the new type of filth in `docs/index.rst` and be sure
  to give yourself a pat on the back in `docs/changelog.rst`

* Make sure all of the tests are passing by running `./tests/run.py` and fix
  any lingering problems (usually PEP-8 nonsense).
