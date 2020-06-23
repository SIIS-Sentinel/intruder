from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="intruder",
    version="0.1.0",
    author="Adrien Cosson",
    author_email="adrien@cosson.io",
    description="The Intruder code for the Sentinel experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdrienCos/intruder",
    packages=find_packages(),
    install_requires=[
        'dnspython',
        'netifaces',
        'paho-mqtt',
        'psycopg2',
        'python-nmap',
        'requests',
        'bookkeeper @ git+http://github.com/AdrienCos/bookkeeper#egg=bookkeeper'
    ],
    python_requires=">=3.5"
)
