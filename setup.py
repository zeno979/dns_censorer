from setuptools import setup

setup(
    name='dns_censorer',
    version='0.1.0',
    author='Sergio Tosti',
    author_email='sergio.tosti -AT- gmail.com',
    description='Blacklist downloader and applier for BIND',
    license='GPLv2',
    keywords='dns bind aams cncpo',
    packages=['dns_censorer'],
    scripts=['censorer'],
    install_requires=[
        'requests',
        'schedule'
    ],
)
