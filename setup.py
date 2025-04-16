from setuptools import setup, find_packages

setup(
    name='xpire',
    version='0.1.2',
    description='XPIRE - eXtended PYthon Interpreter for Retro Emulation',
    author='Jorge Luis Juarez',
    author_email='contacto@jorgejuarez.net',
    packages=find_packages(),
    py_modules=['main'],
    install_requires=['click', 'pygame'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'xpire = main:xpire',
        ]
    }
)