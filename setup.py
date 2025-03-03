from setuptools import setup, find_packages

setup(
    name="cookie_analyzer",  # Korrigiert von "cookie_checker" zu "cookie_analyzer"
    version="1.0.1",
    description="Ein Tool zur Cookie-Analyse basierend auf der Open Cookie Database",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Muslix",  # Angepasst für dich
    license="Apache License 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4",
        "playwright",
        "tldextract",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'cookie-analyzer=cookie_analyzer.interface:cli_main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
