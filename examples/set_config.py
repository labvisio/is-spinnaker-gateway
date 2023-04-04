import socket

from google.protobuf.empty_pb2 import Empty
from is_wire.core import Channel, Subscription, Message

from is_msgs.image_pb2 import ImageFormats
from is_msgs.camera_pb2 import CameraConfig


def main():
    channel = Channel(uri="amqp://guest:guest@localhost:5672")
    subscription = Subscription(channel)
    config = CameraConfig()
    config.image.format.format = ImageFormats.Value("JPEG")
    config.image.format.compression.value = 0.8
    message = Message()
    message.pack(config)
    message.reply_to = subscription
    message.topic = "CameraGateway.0.SetConfig"
    channel.publish(message=message)
    try:
        reply = channel.consume(timeout=3.0)
        struct = reply.unpack(Empty)
        print('RPC Status:', reply.status, '\nReply:', struct)
    except socket.timeout:
        print('No reply :(')


if __name__ == "__main__":
    main()
