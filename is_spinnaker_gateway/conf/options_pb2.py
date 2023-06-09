# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: options.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from is_msgs import camera_pb2 as is__msgs_dot_camera__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\roptions.proto\x1a\x14is_msgs/camera.proto\"\xe8\x02\n\x06\x43\x61mera\x12\n\n\x02id\x18\x01 \x01(\r\x12\n\n\x02ip\x18\x02 \x01(\t\x12,\n\talgorithm\x18\x03 \x01(\x0e\x32\x19.ColorProcessingAlgorithm\x12 \n\x18onboard_color_processing\x18\x04 \x01(\x08\x12\x15\n\ruse_turbojpeg\x18\x05 \x01(\x08\x12\x13\n\x0bpacket_size\x18\x06 \x01(\x05\x12\x14\n\x0cpacket_delay\x18\x07 \x01(\x05\x12\x15\n\rpacket_resend\x18\x08 \x01(\x08\x12\x1d\n\x15packet_resend_timeout\x18\t \x01(\x05\x12\"\n\x1apacket_resend_max_requests\x18\n \x01(\x05\x12\x11\n\treverse_x\x18\x0b \x01(\x08\x12\x16\n\x0erestart_period\x18\x0c \x01(\x02\x12/\n\x0einitial_config\x18\r \x01(\x0b\x32\x17.is.vision.CameraConfig\"Y\n\x14\x43\x61meraGatewayOptions\x12\x14\n\x0crabbitmq_uri\x18\x01 \x01(\t\x12\x12\n\nzipkin_uri\x18\x02 \x01(\t\x12\x17\n\x06\x63\x61mera\x18\x03 \x01(\x0b\x32\x07.Camera*\xe0\x01\n\x18\x43olorProcessingAlgorithm\x12\x11\n\rNOT_SPECIFIED\x10\x00\x12\x14\n\x10NEAREST_NEIGHBOR\x10\x01\x12\x1c\n\x18NEAREST_NEIGHBOR_AVERAGE\x10\x02\x12\x10\n\x0c\x45\x44GE_SENSING\x10\x03\x12\r\n\tHQ_LINEAR\x10\x04\x12\x0c\n\x08\x42ILINEAR\x10\x05\x12\x16\n\x12\x44IRECTIONAL_FILTER\x10\x06\x12\x1f\n\x1bWEIGHTED_DIRECTIONAL_FILTER\x10\x07\x12\x0c\n\x08RIGOROUS\x10\x08\x12\x07\n\x03IPP\x10\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'options_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _COLORPROCESSINGALGORITHM._serialized_start=494
  _COLORPROCESSINGALGORITHM._serialized_end=718
  _CAMERA._serialized_start=40
  _CAMERA._serialized_end=400
  _CAMERAGATEWAYOPTIONS._serialized_start=402
  _CAMERAGATEWAYOPTIONS._serialized_end=491
# @@protoc_insertion_point(module_scope)
