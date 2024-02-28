import sys

from google.protobuf.json_format import Parse

from is_spinnaker_gateway.conf.options_pb2 import CameraGatewayOptions
from is_spinnaker_gateway.gateway import CameraGateway
from is_spinnaker_gateway.logger import Logger


def load_json(  # type: ignore[return]
    logger: Logger,
    path: str = "/etc/is-spinnaker-gateway/options.json",
) -> CameraGatewayOptions:
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


def main() -> None:
    if len(sys.argv) > 1:
        options_filename = sys.argv[1]
    else:
        options_filename = '/etc/is-spinnaker-gateway/options.json'
    logger = Logger(name="CameraGateway")
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
    gateway.run()


if __name__ == "__main__":
    main()
