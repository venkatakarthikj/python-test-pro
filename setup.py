from setuptools import setup

import versioneer

setup(
    name="apsm",
    description="Athena Bitcoin's Persistent State Machines",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    package_dir={'apsm': 'src'},
    packages=['apsm'],
    url="https://www.athenabitcoin.com",
    download_url="https://git-codecommit.us-west-2.amazonaws.com/v1/repos/athena-persistent-state-machines",
    author="Athena Bitcoin, Inc.",
    author_email="tech@athenabitcoin.com",
    classifiers=[
        "Programming Language :: Python", ],
    test_suite='nose.collector',
    tests_require=[
        'nose>=1.3.7',
        'dill>=0.2.8.2',
        'docker>=1.24.1',
        'boto3>=1.9.71'
    ],
    install_requires=['transitions==0.6.9',
                      ]

)
