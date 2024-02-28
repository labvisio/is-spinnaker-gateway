import socket

from is_msgs.camera_pb2 import CameraConfig, CameraConfigFields
from is_msgs.common_pb2 import FieldSelector
from is_wire.core import Channel, Message, Subscription


def main() -> None:
    channel = Channel(uri="amqp://guest:guest@localhost:5672")
    subscription = Subscription(channel)
    selector = FieldSelector(fields=[CameraConfigFields.Value("ALL")])
    channel.publish(
        message=Message(
            content=selector,
            reply_to=subscription,
        ),
        topic="CameraGateway.1.GetConfig",
    )
    try:
        reply = channel.consume(timeout=3.0)
        unpacked_msg = reply.unpack(CameraConfig)
        print('RPC Status:', reply.status, '\nReply:', unpacked_msg)
    except socket.timeout:
        print('No reply :(')


if __name__ == "__main__":
    main()
