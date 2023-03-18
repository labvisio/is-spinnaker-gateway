FROM ubuntu:22.04 as build

ENV READTHEDOCS=True
ENV DEBIAN_FRONTEND=teletype

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        apt-utils \
        gcc \
        linux-libc-dev \
        libc6-dev \
        libffi-dev \
        rustc \
        build-essential \
        libssl-dev \
        cargo \
        git \
        python3 \
        python3-pip ;\
    pip3 install --upgrade poetry; \
    poetry config virtualenvs.in-project true;

COPY . /opt/is-spinnaker-gateway/
WORKDIR /opt/is-spinnaker-gateway/
RUN set -eux; \
    poetry install --only main; \
    poetry run pip install --upgrade protobuf==3.20.3

FROM ubuntu:22.04 as final

RUN set -eux; \ 
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libsm6 \
        libxext6 \
        libglib2.0-0 \
        libxrender-dev \
        libgl1-mesa-glx \
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

WORKDIR /opt/is-spinnaker-gateway
COPY --from=build /opt/is-spinnaker-gateway/.venv /opt/is-spinnaker-gateway/.venv
COPY --from=build /opt/is-spinnaker-gateway/is_spinnaker_gateway /opt/is-spinnaker-gateway/is_spinnaker_gateway
COPY --from=build /opt/is-spinnaker-gateway/etc/conf/options.json /etc/is-spinnaker-gateway/options.json
COPY etc/spinnaker /opt/is-spinnaker-gateway/etc/spinnaker

RUN set -eux; \
    cd etc/spinnaker/;\
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
    cd ../../; \
    rm -rf etc/

ENV VIRTUAL_ENV=/opt/is-spinnaker-gateway/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD [ "is-spinnaker-gateway", "/etc/is-spinnaker-gateway/options.json" ]
