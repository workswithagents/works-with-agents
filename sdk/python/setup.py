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
    long_description="Agent OSI Model Python SDK — Trust Score, Deployment, SLA, Identity, Compliance, Onboarding, IACP, Economics, Reputation. + ASFS Converter + Compliance Proxy. Zero dependencies beyond stdlib. CC BY 4.0.",
    long_description_content_type="text/plain",
    author="Vilius Vystartas",
    author_email="hello@workswithagents.com",
    url="https://workswithagents.dev",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[],
)
