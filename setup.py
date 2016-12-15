from setuptools import setup, find_packages

setup(
    name='upyun-cli',
    version='0.31',
    description='UpYun Command Line Tools',
    packages=find_packages(),
    license='License :: OSI Approved :: MIT License',
    platforms='Platform Independent',
    author='Ming Cheng',
    author_email='mingcheng@outlook.com',
    url='https://github.com/feelinglucky/upyun-cli',
    scripts=['upyun-cli.py'],
    keywords=['upyun'],
    install_requires=[
        'click>=6.6', 'upyun>=2.4.2', 'pyaml>=16.11.4', 'colorama>=0.3.7', 'progressbar2>=2.3'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ],
)
