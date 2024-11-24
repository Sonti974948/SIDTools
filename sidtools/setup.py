
from setuptools import setup, find_packages

setup(
    name='sidtools',
    version='0.1.1',
    description='A package for sidtools utilities',
    author='Siddharth Sonti',
    author_email='sonti.siddharth1907@gmail.com',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            's_make=sidtools.cli:s_make_main',
            's_run=sidtools.cli:s_run_main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
