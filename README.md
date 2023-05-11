# is-spinnaker-gateway

[![Docker image tag](https://img.shields.io/docker/v/labvisio/is-spinnaker-gateway?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-spinnaker-gateway/tags)
[![Docker image size](https://img.shields.io/docker/image-size/labvisio/is-spinnaker-gateway?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-spinnaker-gateway)
[![Docker pulls](https://img.shields.io/docker/pulls/labvisio/is-spinnaker-gateway?style=flat-square)](https://hub.docker.com/r/labvisio/is-spinnaker-gateway)

This repository contains a implementation of a camera gateway for [BlackFly GigE] camera models using [Spinnaker SDK]. All messages used are defined in [is-msgs] and [is-wire-py] package is used to implement the pub/sub middleware for the Inteligent Space architecture.

<p align="center">
  <img src="https://www.flir.com.br/globalassets/imported-assets/image/blackflys-cmount-gige.png" alt=“flir camera gige” width="400" height="400" />
</p>

## Configuration

The behavior of the service can be customized by passing a JSON configuration file as the first argument, e.g: `is-spinnaker-gateway options.json`. The schema for this file can be found in [`is_spinnaker_gateway/conf/options.proto`](is_spinnaker_gateway/conf/options.proto). An example configuration file can be found in [`etc/conf/options.json`](etc/conf/options.json). Check the following table to see the available settings and which ones are modifiable during streaming:

| Configuration      | Available          | Modifiable during streaming | 
|--------------------|--------------------|-----------------------------|
| Sampling Rate      | :heavy_check_mark: | :heavy_check_mark:          |
| Delay              | :x:                | :x:                         |
| Image Resolution   | :x:                | :x:                         |
| Image Format       | :heavy_check_mark: | :heavy_check_mark:          |
| Image Color Space  | :heavy_check_mark: | :x:                         |
| Region of Interest | :heavy_check_mark: | :x:                         |
| Brightness         | :heavy_check_mark: | :heavy_check_mark:          |
| Exposure           | :x:                | :x:                         |
| Focus              | :x:                | :x:                         |
| Gain               | :heavy_check_mark: | :heavy_check_mark:          |
| Gamma              | :x:                | :x:                         |
| Hue                | :x:                | :x:                         |
| Iris               | :x:                | :x:                         |
| Saturation         | :x:                | :x:                         |
| Sharpness          | :x:                | :x:                         |
| Shutter            | :heavy_check_mark: | :heavy_check_mark:          |
| White Balance RV   | :heavy_check_mark: | :heavy_check_mark:          |
| White Balance BU   | :heavy_check_mark: | :heavy_check_mark:          |
| Zoom               | :x:                | :x:                         |
| Contrast           | :x:                | :x:                         |

---
**NOTE**

When setting the `white_balance_rv` to automatic, `white_balance_bu` will also be set to automatic.  It is not possible to set one to automatic and the other not. So, be careful when configuring it.

---

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

## Troubleshooting

The Teledyne FLIR company provides a good guide to [Troubleshooting Image Consistency Errors]. Image consistency errors have a variety of causes, and the user may have to address more than one cause to correct the errors. Note that this gateway provides some really important configurations to optimize the streamming:

* `onboard_color_processing`: by default, the cameras capture images with a BayerRG8 filter. Essentially, an 1288x788 with only one channel. To build a RGB Image is necessary to interpolate for each pixel based on its neighbors the other channel values. The Blackfly GigE cameras have the capacity to run a interpolation algorithm and construct a RGB image onboard. But, it implies in more data over the network. If you would like to run all gateways in only one server, you may have to set this to `False`. However, by setting `onboard_color_processing=False` it implies in some processing time to construct an RGB inside the gateway.

* `algorithm`: if `onboard_color_processing=False`, you can choose the color processing algorithm to build the RGB image. The Teledyne FLIR company also provides a guide to [Undestading Color Interpolation], where you can choose the best algorithm to fit your needs.

* `packet_size`: UDP packet size. Always try to optimize the packet size according to your network settings. Larger packets implies in less chance of packet drop and less packets per image, but your local network should not fragment these packets to improve streamming.

* `packet_delay`: UDP packet delay. Always try to maximize to packet delay. Higher delays allows socket to process more resend requests. However, when increasing the packet delay, the maximum framerate will be lower. In the guide [Troubleshooting Image Consistency Errors], there is a section about **Understanding Packet Delay, Device Link Throughput, and camera framerate** that explain how packet delay changes the maximum framerate.

* `packet_resend`: flag to enable/disable resend UDP Packets. If not enable, may result in image inconsistencies.

* `packet_resend_timeout`: time in milliseconds to wait after the image trailer is received and before is completed by the driver.

* `packet_resend_max_requests`: maximum number of requests per image. Each resend request consists of a span of consecutive UDP packet IDs.

* `restart_period`: restart capture stream from time to time. The package `PySpin` has some bugs, after some time the streamming stops due to memory related issues in Boost C++ library used by Spinnaker SDK. 

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