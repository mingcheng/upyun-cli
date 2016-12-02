from setuptools import setup, find_packages

setup(
    name='upyun-cli',
    version='0.1',
    packages=find_packages(),
    py_modules=['upyun-cli'],
    install_requires=[
        'Click', 'Upyun'
    ],
    entry_points='''
        [console_scripts]
        upyun-cli=upyun-cli:cli
    ''',
)