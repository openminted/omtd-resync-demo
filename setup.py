from setuptools import setup

import re
VERSIONFILE="resyncserver/_version.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(r"^__version__ = '(\d\.\d.\d+(\.\d+)?)'", verfilestr, re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

setup(
    name='resync-omtd-demo',
    version=version,
    packages=['resyncserver'],
    package_data={'resyncserver': ['static/*','templates/*']},
    scripts=['resync-server.py'],
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3.3",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Topic :: Internet :: WWW/HTTP",
                 "Environment :: Web Environment"],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Giorgio Basile',
    author_email='giorgio.basile@open.ac.uk',
    description='ResourceSync generator and server demo',
    long_description=open('README.md').read(),
    install_requires=[
        "resync>=1.0.1",
        "tornado>=4.4.2",
        "pyyaml",
        "watchdog>=0.8.3",
        "rspub-core>=0.1",
        'logutils',
        "elasticsearch>=1.0.0,<2.0.0"
    ],
    test_suite="resyncserver.test",
)