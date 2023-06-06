from is_msgs import camera_pb2 as _camera_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

BILINEAR: ColorProcessingAlgorithm
DESCRIPTOR: _descriptor.FileDescriptor
DIRECTIONAL_FILTER: ColorProcessingAlgorithm
EDGE_SENSING: ColorProcessingAlgorithm
HQ_LINEAR: ColorProcessingAlgorithm
IPP: ColorProcessingAlgorithm
NEAREST_NEIGHBOR: ColorProcessingAlgorithm
NEAREST_NEIGHBOR_AVERAGE: ColorProcessingAlgorithm
NOT_SPECIFIED: ColorProcessingAlgorithm
RIGOROUS: ColorProcessingAlgorithm
WEIGHTED_DIRECTIONAL_FILTER: ColorProcessingAlgorithm

class Camera(_message.Message):
    __slots__ = ["algorithm", "id", "initial_config", "ip", "onboard_color_processing", "packet_delay", "packet_resend", "packet_resend_max_requests", "packet_resend_timeout", "packet_size", "restart_period", "reverse_x", "use_turbojpeg"]
    ALGORITHM_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INITIAL_CONFIG_FIELD_NUMBER: ClassVar[int]
    IP_FIELD_NUMBER: ClassVar[int]
    ONBOARD_COLOR_PROCESSING_FIELD_NUMBER: ClassVar[int]
    PACKET_DELAY_FIELD_NUMBER: ClassVar[int]
    PACKET_RESEND_FIELD_NUMBER: ClassVar[int]
    PACKET_RESEND_MAX_REQUESTS_FIELD_NUMBER: ClassVar[int]
    PACKET_RESEND_TIMEOUT_FIELD_NUMBER: ClassVar[int]
    PACKET_SIZE_FIELD_NUMBER: ClassVar[int]
    RESTART_PERIOD_FIELD_NUMBER: ClassVar[int]
    REVERSE_X_FIELD_NUMBER: ClassVar[int]
    USE_TURBOJPEG_FIELD_NUMBER: ClassVar[int]
    algorithm: ColorProcessingAlgorithm
    id: int
    initial_config: _camera_pb2.CameraConfig
    ip: str
    onboard_color_processing: bool
    packet_delay: int
    packet_resend: bool
    packet_resend_max_requests: int
    packet_resend_timeout: int
    packet_size: int
    restart_period: float
    reverse_x: bool
    use_turbojpeg: bool
    def __init__(self, id: Optional[int] = ..., ip: Optional[str] = ..., algorithm: Optional[Union[ColorProcessingAlgorithm, str]] = ..., onboard_color_processing: bool = ..., use_turbojpeg: bool = ..., packet_size: Optional[int] = ..., packet_delay: Optional[int] = ..., packet_resend: bool = ..., packet_resend_timeout: Optional[int] = ..., packet_resend_max_requests: Optional[int] = ..., reverse_x: bool = ..., restart_period: Optional[float] = ..., initial_config: Optional[Union[_camera_pb2.CameraConfig, Mapping]] = ...) -> None: ...

class CameraGatewayOptions(_message.Message):
    __slots__ = ["camera", "rabbitmq_uri", "zipkin_uri"]
    CAMERA_FIELD_NUMBER: ClassVar[int]
    RABBITMQ_URI_FIELD_NUMBER: ClassVar[int]
    ZIPKIN_URI_FIELD_NUMBER: ClassVar[int]
    camera: Camera
    rabbitmq_uri: str
    zipkin_uri: str
    def __init__(self, rabbitmq_uri: Optional[str] = ..., zipkin_uri: Optional[str] = ..., camera: Optional[Union[Camera, Mapping]] = ...) -> None: ...

class ColorProcessingAlgorithm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
