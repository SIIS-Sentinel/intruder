from setuptools import setup, find_packages

setup(name="intruder",
      packages=find_packages(),
      install_requires=[
          'dnspython',
          'netifaces',
          'paho-mqtt',
          'psycopg2',
          'python-nmap',
          'SQLAlchemy'
      ],
      )
