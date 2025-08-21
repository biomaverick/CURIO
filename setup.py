from setuptools import setup, find_packages

setup(
    name="curio_pkg",
    version="0.1.0",
    description="Curio Bioinformatics Toolkit",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/curio_pkg",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.9",
)
