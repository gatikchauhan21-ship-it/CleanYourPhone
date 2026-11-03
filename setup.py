"""CleanYourPhone setup script for packaging and CLI distribution."""

import os
from setuptools import setup, find_packages

long_description = "Turn budget Android phones into flagship experiences via Wireless ADB without root."
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="cleanyourphone",
    version="1.0.0",
    author="CleanYourPhone Contributors",
    author_email="maintainers@cleanyourphone.dev",
    description="Zero-Root Flagship Optimizer and Debloater for Android over Wireless ADB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gatikchauhan21-ship-it/CleanYourPhone",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "colorama>=0.4.6",
        "requests>=2.31.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "cleanyourphone=src.cli:main",
        ],
    },
)
