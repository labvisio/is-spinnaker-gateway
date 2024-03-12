import glob
import os

from setuptools import find_packages, setup

setup(
    name="is_spinnaker_gateway",
    version="0.3.0",
    description="Gateway for Blackfly and Blackfly S GigE camera models using Spinnaker SDK.",
    long_description=open("README.md").read().strip(),
    long_description_content_type="text/markdown",
    keywords=[
        "spinnaker",
        "blackfly",
        "blackfly-s",
        "camera",
        "gateway",
    ],
    license="MIT",
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
        "is_msgs==1.1.18",
        "is_wire==1.2.1",
        "numpy==1.26.4",
        "opencv-contrib-python-headless==4.9.0.80",
        "opencensus-ext-zipkin==0.2.1",
        "python-dateutil==2.8.2",
        "pyturbojpeg @ git+https://github.com/lilohuang/PyTurboJPEG.git",
        "spinnaker-python @ file://localhost/{}/{}".format(
            os.getcwd(),
            glob.glob("etc/spinnaker/*.whl")[0],
        ),
        "typing-extensions==4.10.0",
    ],
    zip_safe=False,
    author=["LabVISIO"],
    author_email=["labvisio.ufes@gmail.com"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3 :: Only",
    ],
    extras_require={
        "dev": [
            "pytest==8.0.2",
            "pytest-cov==4.1.0",
            "flake8==7.0.0",
            "mypy==1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "is-spinnaker-gateway=is_spinnaker_gateway.service:main",
        ],
    },
)
