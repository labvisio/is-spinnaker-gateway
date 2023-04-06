# is-spinnaker-gateway

[![Docker image tag](https://img.shields.io/docker/v/labvisio/is-spinnaker-gateway?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-spinnaker-gateway/tags)
[![Docker image size](https://img.shields.io/docker/image-size/labvisio/is-spinnaker-gateway?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-spinnaker-gateway)
[![Docker pulls](https://img.shields.io/docker/pulls/labvisio/is-spinnaker-gateway?style=flat-square)](https://hub.docker.com/r/labvisio/is-spinnaker-gateway)

This repository contains a implementation of a camera gateway for [BlackFly GigE] camera models using [Spinnaker SDK]. All messages used are defined in [is-msgs] and [is-wire-py] package is used to implement the pub/sub middleware for the Inteligent Space architecture.

<p align="center">
  <img src="https://www.flir.com.br/globalassets/imported-assets/image/blackflys-cmount-gige.png" alt=“flir camera gige” width="400" height="400" />
</p>

## Configuration

The behavior of the service can be customized by passing a JSON configuration file as the first argument, e.g: `is-spinnaker-gateway options.json`. The schema for this file can be found in [`is_spinnaker_gateway/conf/options.proto`](is_spinnaker_gateway/conf/options.proto). An example configuration file can be found in [`etc/conf/options.json`](etc/conf/options.json).


## Development

It is recommended that you use Ubuntu 22.04 for development. Also, make sure you have Docker installed (if not, [Install Docker Engine on Ubuntu] and [Linux post-installation steps for Docker Engine]). 

### Spinnaker SDK

First, make sure to download [Spinnaker SDK] for **Ubuntu 22.04**. The files are and their locations are:

* **spinnaker-3.0.0.118-amd64-pkg.tar.gz**: Linux > Ubuntu 22.04
* **spinnaker_python-3.0.0.118-cp310-cp210-linux_x86_64.tar.gz**: Linux > Ubuntu 22.04 > python

Then, extract and move all `.deb` and `*.whl` into `etc/spinnaker/` folder.

### Docker image

Once you have the necessary files for the camera driver at `etc/spinnaker/`, to build the docker image just run:
```bash
make image
```

You can also build the image with your user and the version you want:
```bash
make image USER=luizcarloscf VERSION=0.1.3-beta
```

## Usefull resources and links

* [Undestading Color Interpolation]
* [Troubleshooting Image Consistency Errors]
* [Setting Persistent IP in SpinnakerQT]

[is-msgs]: https://github.com/labviros/is-msgs
[is-wire-py]: https://github.com/labviros/is-wire-py

[Install Docker Engine on Ubuntu]: https://docs.docker.com/engine/install/ubuntu/
[Linux post-installation steps for Docker Engine]: https://docs.docker.com/engine/install/linux-postinstall/

[Blackfly GigE]: https://www.flir.com/products/blackfly-gige/
[Spinnaker SDK]: https://www.flir.com.br/products/spinnaker-sdk/?vertical=machine+vision&segment=iis
[Undestading Color Interpolation]: https://www.flir.eu/support-center/iis/machine-vision/application-note/understanding-color-interpolation/
[Troubleshooting Image Consistency Errors]: https://www.flir.com/support-center/iis/machine-vision/application-note/troubleshooting-image-consistency-errors/
[Setting Persistent IP in SpinnakerQT]: https://www.flir.eu/support-center/iis/machine-vision/knowledge-base/persistent-ip-in-spinnakerqt/