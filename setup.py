
from setuptools import setup, find_packages

# Get some values from the setup.cfg

NAME = 'ddoitranslatormodule'
VERSION = '0.1'
RELEASE = 'dev' not in VERSION
AUTHOR = "Max Brodheim"
AUTHOR_EMAIL = "mbrodheim@keck.hawaii.edu"
LICENSE = "3-clause BSD"
DESCRIPTION = "Base Translator Module class and example"

scripts = []

# Define entry points for command-line scripts
entry_points = {
    'console_scripts': []
    }

setup(name=NAME,
      provides=NAME,
      version=VERSION,
      license=LICENSE,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      packages=find_packages(),
      scripts=scripts,
      entry_points=entry_points,
      install_requires=[],
      python_requires=">=3.6"
      )