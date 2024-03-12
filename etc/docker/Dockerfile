FROM ubuntu:22.04 as build

ENV READTHEDOCS=True
ENV DEBIAN_FRONTEND=teletype

ENV VIRTUAL_ENV=/opt/is-spinnaker-gateway/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        git \
        python3 \
        python3-pip \
        python3-venv

COPY . /opt/is-spinnaker-gateway/

WORKDIR /opt/is-spinnaker-gateway/
RUN set -eux; \
    make venv; \
    make build

FROM ubuntu:22.04 as final

RUN set -eux; \ 
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libturbojpeg \
        libavcodec58 \
        libavformat58 \
        libswscale5 \
        libswresample3 \
        libavutil56 \
        libusb-1.0-0 \
        libpcre2-16-0 \
        libdouble-conversion3 \
        libxcb-xinput0 \
        libxcb-xinerama0 \
        debconf-utils \
        python3; \
        apt-get clean ; rm -rf /tmp/* /var/tmp/*;

WORKDIR /tmp
COPY etc/spinnaker /tmp/spinnaker

RUN set -eux; \
    cd spinnaker/;\
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections; \
    echo libgentl libspinnaker/accepted-flir-eula boolean true | debconf-set-selections; \
    dpkg -i libgentl_*.deb; \
    dpkg -i libspinnaker_*.deb; \
    dpkg -i libspinnaker-dev_*.deb; \
    dpkg -i libspinnaker-c_*.deb; \
    dpkg -i libspinnaker-c-dev_*.deb; \
    dpkg -i libspinvideo_*.deb; \
    dpkg -i libspinvideo-dev_*.deb; \
    dpkg -i libspinvideo-c_*.deb; \
    dpkg -i libspinvideo-c-dev_*.deb; \
    dpkg -i spinupdate_*.deb; \
    dpkg -i spinupdate-dev_*.deb; \
    dpkg -i spinnaker_*.deb; \
    dpkg -i spinnaker-doc_*.deb; \
    cd ../; \
    rm -rf spinnaker/ /opt/spinnaker/doc /opt/spinnaker/src /opt/spinnaker/licenses

WORKDIR /opt/is-spinnaker-gateway
COPY --from=build /opt/is-spinnaker-gateway/.venv /opt/is-spinnaker-gateway/.venv
COPY --from=build /opt/is-spinnaker-gateway/etc/conf/options.json /etc/is-spinnaker-gateway/options.json

ENV VIRTUAL_ENV=/opt/is-spinnaker-gateway/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SPINNAKER_GENTL64_CTI="/opt/spinnaker/lib/spinnaker-gentl/Spinnaker_GenTL.cti"

CMD [ "is-spinnaker-gateway", "/etc/is-spinnaker-gateway/options.json" ]
