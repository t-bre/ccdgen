import setuptools
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name = "Compile Commands Generator",
    version = "0.1.0",
    author = "Tim Brewis",
    author_email = "timbrewis27@gmail.com",
    license = "Apache-2.0",
    description = ("Generates compilation databases by capturing standard "
                   "output from Make"),
    long_description = read('README.md'),
    long_description_content_type = 'text/markdown',
    project_urls={
        'Source': 'https://github.com/t-bre/compile-commands',
        'Tracker': 'https://github.com/t-bre/compile-commands/issues',
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.10'
    ],
    keywords = 'make'
)