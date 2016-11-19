from setuptools import setup, find_packages, Extension

ht1632c = Extension(
    'ht1632c',
    libraries=['wiringPi'],
    sources=['ht1632c/ht1632c.c', 'ht1632c/fonts.c'],
    extra_compile_args=['-std=c99']
)

setup (
	name='ht1632cpy',
	version='1.0',
	description='This is a demo package',
	author='Mike Chester',
	author_email='mikeachester@gmail.com',
	ext_modules=[ht1632c],
    packages=find_packages(),
)
