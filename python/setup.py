from setuptools import find_packages, setup

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Read dev requirements
with open("requirements-dev.txt") as f:
    dev_requirements = f.read().splitlines()

# Read version
with open("VERSION") as f:
    version = f.read()

setup(
    name="jazzy_fish",
    version=version,
    # Packages reside in src/
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    author="Mihai Bojin",
    author_email="557584+MihaiBojin@users.noreply.github.com",
    # Describes the library
    description="Library that generates a sufficiently-large, unique, human-friendly identifiers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # URLs relevant to the project
    url="https://github.com/jazzy-fish/jazzy-fish",
    project_urls={
        "Bug Reports": "https://github.com/jazzy-fish/jazzy-fish/issues/new",
        "Source": "https://github.com/jazzy-fish/jazzy-fish",
    },
    keywords="jazzy fish unique human friendly identifiers",
    # Defines requirements and dev-requirements
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    # Defines the license
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",  # Development status
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    # Defines entry points
    entry_points={
        "console_scripts": [
            "clean_wordlist=preprocessor.clean_wordlist:main",
            "generate_words=preprocessor.generate_words:main",
        ],
    },
    # Defines the minimum version requirement of Python
    python_requires=">=3.11",
)
