import sys
from numpy.distutils.core import setup

__author__ = "Casper Steinmann"
__copyright__ = "Copyright 2020"
__credits__ = ["Casper Steinmann (2020) https://github.com/steinmanngroup/molecule_one_batch_api"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Casper Steinmann"
__email__ = "css@bio.aau.dk"
__status__ = "Beta"
__description__ = "molecule.one batch API"
__url__ = "https://github.com/steinmanngroup/molecule_one_batch_api"


# use README.md as long description
def readme():
    with open('README.md') as f:
        return f.read()


def setup_pepytools():
    setup(

        name="moleculeone",
        packages=['moleculeone'],

        # metadata
        version=__version__,
        author=__author__,
        author_email=__email__,
        platforms = 'Any',
        description = __description__,
        long_description = readme(),
        keywords = ['Chemistry', 'Synthetic Accessibility'],
        classifiers = [],
        url = __url__,
    )


if __name__ == '__main__':
    setup_pepytools()