import os
from setuptools import setup, find_packages

setup(
    name="web-archer",
    version="1.0.0",
    author="32exe",
    description="A lightweight, multi-threaded text scraper and website scouting tool",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "ddgs>=6.1.7",
        "curl_cffi>=0.7.0" ,
    ],
    entry_points={
        "console_scripts": [
            "web-scout=web_archer.web__scout:scout_websites",
            "web-archer=web_archer.web__archer:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
)
