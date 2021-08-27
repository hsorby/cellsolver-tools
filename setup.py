import os
import re
import codecs

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='cellsolver-tools',
    version=find_version('src', 'cellsolvertools', '__init__.py'),
    packages=['cellsolvertools'],
    package_dir={'': 'src'},
    url='https://github.com/hsorby/cellsolver-tools',
    license='Apache 2.0',
    author='Hugh Sorby',
    author_email='h.sorby@auckland.ac.nz',
    description='A collection of scripts to enhance the usage of Cell Solver.',
    install_requires=['matplotlib', 'cellsolver'],
    entry_points={
        'console_scripts': ['cellsolver-multi-process=cellsolvertools.multi_processing_script:main',
                            'cellsolver-sensitivity-plot=cellsolvertools.multi_trial_plot:main'],
    }
)
