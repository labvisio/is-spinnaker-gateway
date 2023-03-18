import sys
import logging

from google.protobuf.json_format import Parse

from is_spinnaker_gateway.logger import Logger
from is_spinnaker_gateway.gateway import CameraGateway
from is_spinnaker_gateway.conf.options_pb2 import CameraGatewayOptions


def load_json(
        logger: Logger,
        path: str = "/etc/is-spinnaker-gateway/options.json") -> CameraGatewayOptions:
    try:
        with open(path, 'r') as f:
            try:
                op = Parse(f.read(), CameraGatewayOptions())
                logger.info('CameraGatewayOptions: \n{}', op)
                return op
            except Exception as ex:
                logger.critical('Unable to load options from \'{}\'. \n{}', path, ex)
    except Exception:
        logger.critical('Unable to open file \'{}\'', path)


def main():
    if len(sys.argv) > 1:
        options_filename = sys.argv[1]
    else:
        options_filename = '/etc/is-spinnaker-gateway/options.json'
    logger = Logger(
        name="CameraGateway",
        level=logging.DEBUG,
    )
    options = load_json(
        logger=logger,
        path=options_filename,
    )
    gateway = CameraGateway(
        logger=logger,
        broker_uri=options.rabbitmq_uri,
        zipkin_uri=options.zipkin_uri,
        camera=options.camera,
    )
    while True:
        gateway.run()


if __name__ == "__main__":
    main()
