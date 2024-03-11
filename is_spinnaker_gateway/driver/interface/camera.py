from abc import ABC, abstractmethod
from typing import List, TypedDict

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.wrappers_pb2 import FloatValue, Int64Value
from is_msgs.camera_pb2 import CameraSetting
from is_msgs.image_pb2 import (
    BoundingPoly,
    ColorSpace,
    Image,
    ImageFormat,
    Resolution,
)


class CameraEthernet(TypedDict):
    ip_address: str
    subnet_mask: int
    mac_address: str


class CameraInfo(TypedDict):
    interface: CameraEthernet
    serial_number: str
    model_name: str
    link_speed: int


class CameraDriver(ABC):

    @abstractmethod
    def find_cameras(self) -> List[CameraInfo]:
        pass

    @abstractmethod
    def connect(self, cam_info: CameraInfo, max_retries: int) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def start_capture(self) -> None:
        pass

    @abstractmethod
    def stop_capture(self) -> None:
        pass

    @abstractmethod
    def grab_image(self) -> Image:
        pass

    @abstractmethod
    def last_timestamp(self) -> Timestamp:
        pass

    @abstractmethod
    def get_sampling_rate(self) -> FloatValue:
        pass

    @abstractmethod
    def set_sampling_rate(self, sampling_rate: FloatValue) -> None:
        pass

    @abstractmethod
    def get_delay(self) -> FloatValue:
        pass

    @abstractmethod
    def set_delay(self, delay: FloatValue) -> None:
        pass

    @abstractmethod
    def get_resolution(self) -> Resolution:
        pass

    @abstractmethod
    def set_resolution(self, resolution: Resolution) -> None:
        pass

    @abstractmethod
    def get_format(self) -> ImageFormat:
        pass

    @abstractmethod
    def set_format(self, image_format: ImageFormat) -> None:
        pass

    @abstractmethod
    def get_color_space(self) -> ColorSpace:
        pass

    @abstractmethod
    def set_color_space(self, color_space: ColorSpace) -> None:
        pass

    @abstractmethod
    def get_region_of_interest(self) -> BoundingPoly:
        pass

    @abstractmethod
    def set_region_of_interest(self, roi: BoundingPoly) -> None:
        pass

    @abstractmethod
    def get_brightness(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_brightness(self, brightness: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_exposure(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_exposure(self, exposure: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_focus(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_focus(self, focus: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_gain(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_gain(self, gain: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_gamma(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_gamma(self, gamma: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_hue(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_hue(self, hue: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_iris(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_iris(self, iris: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_saturation(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_saturation(self, saturation: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_sharpness(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_sharpness(self, sharpness: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_shutter(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_shutter(self, shutter: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_white_balance_bu(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_white_balance_bu(self, white_balance_bu: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_white_balance_rv(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_white_balance_rv(self, white_balance_rv: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_zoom(self) -> CameraSetting:
        pass

    @abstractmethod
    def set_zoom(self, zoom: CameraSetting) -> None:
        pass

    @abstractmethod
    def get_stream_channel_id(self) -> Int64Value:
        pass

    @abstractmethod
    def set_stream_channel_id(self, stream_channel_id: Int64Value) -> None:
        pass

    @abstractmethod
    def set_reverse_x(self, reverse_x: bool) -> None:
        pass

    @abstractmethod
    def set_packet_size(self, packet_size: int) -> None:
        pass

    @abstractmethod
    def set_packet_delay(self, packet_delay: int) -> None:
        pass

    @abstractmethod
    def set_packet_resend(self, packet_resend: bool) -> None:
        pass

    @abstractmethod
    def set_packet_resend_timeout(self, timeout: int) -> None:
        pass

    @abstractmethod
    def set_packet_resend_max_requests(self, max_requests: int) -> None:
        pass
