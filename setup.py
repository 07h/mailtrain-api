from setuptools import setup, find_packages

setup(
    name="mailtrain-api",
    version="1.1",
    packages=find_packages(),
    test_suite="tests",
    include_package_data=True,
    install_requires=[
        "httpx",
    ],
)
