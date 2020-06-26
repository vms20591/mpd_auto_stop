#! /usr/bin/env python

from setuptools import find_packages
from setuptools import setup
import mpd_auto_stop as mas
import os
import sys
import io

def read(fname):
  with io.open(os.path.join(os.path.dirname(__file__), fname), encoding="utf8") as fd:
    return fd.read()

VERSION = ".".join(map(str, mas.VERSION))

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Topic :: Multimedia :: Sound/Audio :: Players",
]

LICENSE = read("LICENSE")

setup(
    name="mpd_auto_stop",
    version=VERSION,
    description="A pure python web utility for auto stopping Music Player Daemon, by setting up timers.",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    author="Meenakshi Sundaram V",
    author_email="vms20591@gmail.com",
    license="GNU General Public License v3 (GPLv3)",
    url="https://github.com/vms20591/mpd_auto_stop",
    packages=find_packages(),
    zip_safe=True,
    keywords=["mpd"],
    test_suite="mpd_auto_stop.tests",
    scripts=["bin/mpd_auto_stop"]
)
