#!/usr/bin/env python3
"""
Setup file for Knowledge Base & Token Intelligence System.
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="knowledge_base_system",
    version="1.0.0",
    author="Knowledge Base Team",
    author_email="taiscoding@github.com",
    description="Privacy-first knowledge management system with token intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taiscoding/knowledge-base-system.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=0.20.0",
    ],
    entry_points={
        "console_scripts": [
            "token-intelligence-server=token_intelligence.api_server:main",
            "knowledge-base-server=knowledge_base.api_server:main",
            "kb-cli=knowledge_base.cli:main"
        ],
    },
    project_urls={
        "Documentation": "https://docs.knowledge-base-system.com",
        "Source": "https://github.com/taiscoding/knowledge-base-system.git",
        "Issues": "https://github.com/taiscoding/knowledge-base-system/issues",
    }
) 