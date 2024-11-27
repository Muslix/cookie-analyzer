from setuptools import setup, find_packages

setup(
    name="cookie_checker",
    version="0.1.0",
    description="Ein Tool zur Cookie-Analyse basierend auf der Open Cookie Database",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dein Name",
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
)
