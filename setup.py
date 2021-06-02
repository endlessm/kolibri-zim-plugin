
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

import kolibri_zim_plugin


dist_name = "kolibri_zim_plugin"
description = """Kolibri plugin to add a Zim file viewer"""


setup(
    name=dist_name,
    description=description,
    version=kolibri_zim_plugin.__version__,
    author="Endless OS Foundation",
    author_email="dylan@endless.org",
    url="https://github.com/endlessm/kolibri-zim-plugin",
    packages=["kolibri_zim_plugin"],
    entry_points={
        "kolibri.plugins": "kolibri_zim_plugin = kolibri_zim_plugin",
    },
    package_dir={"kolibri_zim_plugin": "kolibri_zim_plugin"},
    install_requires=["libzim==0.0.3.post0"],
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords="kolibri",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)