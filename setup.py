#!/usr/bin/python

import sys
import setuptools

with open("./dnstap_dashboard/__init__.py", "r") as fh:
    for line in fh.read().splitlines():
        if line.startswith('__version__'):
            PKG_VERSION = line.split('"')[1]
            
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()
    
KEYWORDS = ('dnstap dashboard dns metrics')

install_requires = [
                     "pyyaml",
                     "requests"
                   ]
if sys.platform.startswith('win32'):
    install_requires.append("windows-curses")
    
setuptools.setup(
    name="dnstap_dashboard",
    version=PKG_VERSION,
    author="Denis MACHARD",
    author_email="d.machard@gmail.com",
    description="dnstap dashboard - real-time metrics for dns server",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/dmachard/dnstap-dashboard",
    packages=['dnstap_dashboard'],
    include_package_data=True,
    platforms='any',
    keywords=KEYWORDS,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    entry_points={'console_scripts': ['dnstap_dashboard = dnstap_dashboard.dashboard:start_dashboard']},
    install_requires=install_requires
)
