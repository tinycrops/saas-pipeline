from setuptools import setup, find_packages

setup(
    name="saas-pipeline",
    version="0.1.0",
    description="A modular toolkit for building, growing, and scaling a SaaS business from $0 to $100k/month",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="SaaS Pipeline Team",
    author_email="team@saaspipeline.dev",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",  # For OpenAI API integration
        "python-dotenv>=1.0.0",  # For environment variable management
        "pyyaml>=6.0.1",  # For YAML configuration files
        "click>=8.1.0",  # For CLI interface
        "rich>=13.0.0",  # For beautiful terminal output
        "requests>=2.31.0",  # For HTTP requests
        "tenacity>=8.2.0",  # For retry logic
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "saas-pipeline=saas_pipeline.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 