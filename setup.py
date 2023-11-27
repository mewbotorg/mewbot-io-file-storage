# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
setup.py intended for a mewbot.io namespace plugin.
"""

import os
import pathlib

import setuptools

# Finding the right README.md and inheriting the mewbot licence
root_repo_dir = pathlib.Path(__file__).parent

with (root_repo_dir / "README.md").open("r", encoding="utf-8") as rmf:
    long_description = rmf.read()

with (root_repo_dir / "requirements.txt").open("r", encoding="utf-8") as rf:
    requirements = list(x for x in rf.read().splitlines(False) if x and not x.startswith("#"))

# Reading the LICENSE file and parsing the results
# LICENSE file should contain a symlink to the licence in the LICENSES folder
# Held in the root of the repo

license_file = root_repo_dir / "LICENSE.md"
if license_file.is_symlink():
    license_identifier = license_file.readlink().stem
else:
    with license_file.open("r", encoding="utf-8") as license_data:
        license_file = root_repo_dir / license_data.read().strip()
    license_identifier = license_file.stem

# There are a number of bits of special sauce in this call
# - You can fill it out manually - for your project
# - You can copy this and make the appropriate changes
# - Or you can run "mewbot make_namespace_plugin" - and follow the onscreen instructions.
#   Which should take care of most of the fiddly bits for you.
setuptools.setup(
    name="mewbot-io-file-storage",
    python_requires=">=3.10",  # Might be relaxed later
    version=os.environ.get("RELEASE_VERSION", "0.0.1alpha1"),
    install_requires=requirements,

    description="An IOConfig which allows mewbot to write to local file storage.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    license=license_identifier,
    license_file=str(license_file.absolute()),

    author="Alex Cameron",
    author_email="mewbot@quicksilver.london",
    maintainer="Alex Cameron",
    maintainer_email="mewbot@quicksilver.london",

    url="https://github.com/mewbotorg/mewbot-io-file_storage",
    project_urls={
        "Bug Tracker": "https://github.com/mewbotorg/mewbot-file-storage/issues",
    },

    packages=setuptools.find_namespace_packages(where="src", include=["mewbot.*"]),
    package_dir={"": "src"},
    package_data={"": ["py.typed"]},
    entry_points={"mewbotv1": ["file_storage = mewbot.io.file_storage"]},

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
)
