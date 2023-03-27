import os
import glob

from setuptools import setup, find_packages

package_name = 'is_spinnaker_gateway'

setup(
    name=package_name,
    version='0.1.1',
    packages=find_packages(
        exclude=[
            "tests*",
            "examples*",
            "etc*",
        ],
    ),
    install_requires=[
        'setuptools',
        'wheel',
        'is_msgs==1.1.10',
        'is_wire==1.2.0',
        'vine==1.3.0',
        'numpy==1.22.4',
        'protobuf>=3.6.0,<=3.20.3',
        'google-api-core==1.19.1',
        'googleapis-common-protos==1.52.0',
        'google-auth==1.35.0',
        'opencv-contrib-python==4.7.0.68',
        'opencensus-ext-zipkin==0.2.1',
        'python-dateutil==2.8.0',
        'pyturbojpeg @ git+https://github.com/lilohuang/PyTurboJPEG.git',
        'spinnaker-python @ file://localhost/{}/{}'.format(os.getcwd(), glob.glob('etc/spinnaker/*.whl')[0]),
    ],
    zip_safe=False,
    author=['Luiz Carlos Cosmi Filho'],
    author_email=['luiz.cosmi@edu.ufes.br'],
    maintainer='Luiz Carlos Cosmi Filho',
    maintainer_email='luiz.cosmi@edu.ufes.br',
    keywords=['spinnaker', 'blackfly', 'camera', 'gateway'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
        'Programming Language :: Python :: 3 :: Only'
        'Topic :: Software Development',
    ],
    description='Camera gateway using Spinnaker SDK to integrate Blackfly GigE cameras.',
    license='Apache License, Version 2.0',
    extras_require={
        'dev': [
            'pytest==7.2.1',
            'pytest-cov==4.0.0',
            'flake8==6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'is-spinnaker-gateway=is_spinnaker_gateway.service:main',
        ],
    },
)