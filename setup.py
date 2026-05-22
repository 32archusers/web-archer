from setuptools import setup, find_packages

setup(
    name="web-archer",
    version="1.4.0",
    description="A multi-threaded text scraper and automated target acquisition crawling ecosystem.",
    author="32archusers",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "curl_cffi",
        # FIX: Changed from 'ddgs' to the actual distribution package name
        "duckduckgo-search>=3.9.0", 
    ],
    entry_points={
        "console_scripts": [
            "web-archer=web_archer.web__archer:main",
            # FIX: Pointed web-scout to main() instead of the non-existent scout_websites
            "web-scout=web_archer.web__scout:main", 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
