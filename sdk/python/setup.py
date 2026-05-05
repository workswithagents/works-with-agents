"""
Works With Agents — Python SDK
Reference implementations for all Agent OSI Model protocols.
Zero dependencies beyond stdlib (cryptography optional).
"""
from setuptools import setup, find_packages

setup(
    name="workswithagents",
    version="0.1.0",
    description="Works With Agents — Agent OSI Model Python SDK",
    long_description=open("README.md").read() if __import__('os').path.exists("README.md") else "",
    author="Vilius Vystartas",
    author_email="hello@workswithagents.com",
    url="https://workswithagents.dev",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: CC BY 4.0",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
