from setuptools import setup, find_packages

setup(
    name='ht1632cpy',
    version='0.2',
    description='Library to interface with HT1632C LED driver',
    author='Mike Chester',
    author_email='mikeachester@gmail.com',
    install_requires=[
        'wiringpi>=2.46.0',
    ],
    packages=find_packages(),
)
