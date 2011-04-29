from setuptools import setup


# To set __version__
__version__ = '0.0.3'

setup(name="socketconsole",
    version=__version__,
    py_modules=['socketconsole', 'socketreader'],
    description="Unix socket access to python thread dump",
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'socketreader=socketreader:main',
        ]
    }
)
