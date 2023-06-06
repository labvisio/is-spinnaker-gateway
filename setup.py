import os
import glob

from setuptools import setup, find_packages

package_name = 'is_spinnaker_gateway'

setup(
    name=package_name,
    version='0.2.0',
    description='Gateway for BlackFly GigE camera models using Spinnaker SDK.',
    long_description=open("README.md").read().strip(),
    long_description_content_type="text/markdown",
    keywords=['spinnaker', 'blackfly', 'camera', 'gateway'],
    license='MIT',
    packages=find_packages(exclude=[
        "tests*",
        "examples*",
        "etc*",
    ]),
    url="https://github.com/labvisio/is-spinnaker-gateway",
    project_urls={
        "Changes": "https://github.com/labvisio/is-spinnaker-gateway/releases",
        "Code": "https://github.com/labvisio/is-spinnaker-gateway",
        "Issue tracker": "https://github.com/labvisio/is-spinnaker-gateway/issues",
    },
    install_requires=[
        'is_msgs==1.1.17',
        'is_wire==1.2.1',
        'numpy==1.22.4',
        'opencv-contrib-python==4.7.0.68',
        'opencensus-ext-zipkin==0.2.1',
        'python-dateutil==2.8.0',
        'pyturbojpeg @ git+https://github.com/lilohuang/PyTurboJPEG.git',
        'spinnaker-python @ file://localhost/{}/{}'.format(os.getcwd(),
                                                           glob.glob('etc/spinnaker/*.whl')[0]),
    ],
    zip_safe=False,
    author=['LabVISIO'],
    author_email=['labvisio.ufes@gmail.com'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
        'Programming Language :: Python :: 3 :: Only',
    ],
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