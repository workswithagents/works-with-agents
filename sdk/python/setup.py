"""
Works With Agents — Python SDK
Reference implementations for all Agent OSI Model protocols.
Zero dependencies beyond stdlib (cryptography optional).
"""
from setuptools import setup, find_packages

setup(
    name="workswithagents",
    version="0.1.1",
    description="Works With Agents — Agent OSI Model Python SDK",
    long_description="Agent OSI Model Python SDK — Trust Score, Deployment, SLA, Identity, Compliance, Onboarding, IACP, Economics, Reputation. + ASFS Converter + Compliance Proxy. Zero dependencies beyond stdlib. CC BY 4.0.",
    long_description_content_type="text/plain",
    author="Vilius Vystartas",
    author_email="hello@workswithagents.com",
    url="https://workswithagents.dev",
    project_urls={
        "Homepage": "https://workswithagents.dev",
        "Repository": "https://github.com/workswithagents/works-with-agents",
        "Documentation": "https://workswithagents.dev/llms.txt",
        "Issues": "https://github.com/workswithagents/works-with-agents/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    license="CC BY 4.0",
    classifiers=[
        "License :: Other/Proprietary License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
