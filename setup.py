from setuptools import setup

version = "1.2.0"

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="smort-query",
    version=version,
    description=("Django like query engine for any objects."),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Mateusz Nowak",
    author_email="nowak.mateusz@hotmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    url="https://github.com/matiuszka/smort-query",
    packages=[
        "smort_query",
    ],
    python_requires=">=3.6",
    package_dir={"smort_query": "smort_query"},
    include_package_data=True,
    install_requires=["more_itertools~=8.0"],
    license="MIT",
    zip_safe=False,
)
