from typing import Tuple, Any

from is_wire.core import Status, StatusCode
from google.protobuf.wrappers_pb2 import FloatValue, Int64Value

from is_msgs.camera_pb2 import CameraSetting
from is_msgs.image_pb2 import Image, Resolution, ColorSpace, ImageFormat, BoundingPoly


class CameraDriver:

    def get_resolution(self) -> Tuple[Status, Resolution]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Resolution property not implemented for this camera.",
        )
        return status, Resolution()

    def set_resolution(self, resolution: Resolution) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Resolution property not implemented for this camera.",
        )
        return status

    def get_format(self) -> Tuple[Status, ImageFormat]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="ImageFormat property not implemented for this camera.",
        )
        return status, ImageFormat()

    def set_format(self, image_format: ImageFormat) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="ImageFormat property not implemented for this camera.",
        )
        return status

    def get_color_space(self) -> Tuple[Status, ColorSpace]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="ColorSpace property not implemented for this camera.",
        )
        return status, ColorSpace()

    def set_color_space(self, color_space: ColorSpace) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="ColorSpace property not implemented for this camera.",
        )
        return status

    def get_region_of_interest(self) -> Tuple[Status, BoundingPoly]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="RegionOfInterest property not implemented for this camera.",
        )
        return status, BoundingPoly()

    def set_region_of_interest(self, region_of_interest: BoundingPoly) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="RegionOfInterest property not implemented for this camera.",
        )
        return status

    def get_sampling_rate(self) -> Tuple[Status, FloatValue]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="SamplingRate property not implemented for this camera.",
        )
        return status, FloatValue()

    def set_sampling_rate(self, sampling_rate: FloatValue) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="SamplingRate property not implemented for this camera.",
        )
        return status

    def get_delay(self) -> Tuple[Status, FloatValue]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Delay property not implemented for this camera.",
        )
        return status, FloatValue()

    def set_delay(self, delay: FloatValue) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Delay property not implemented for this camera.",
        )
        return status

    def get_brightness(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Brightness property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_brightness(self, brightness: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Brightness property not implemented for this camera.",
        )
        return status

    def get_exposure(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Brightness property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_exposure(self, exposure: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Exposure property not implemented for this camera.",
        )
        return status

    def get_focus(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Focus property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_focus(self, focus: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Focus property not implemented for this camera.",
        )
        return status

    def get_gain(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Gain property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_gain(self, gain: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Gain property not implemented for this camera.",
        )
        return status

    def get_gamma(self) -> Tuple[Status, CameraSetting, None]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Gamma property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_gamma(self, gamma: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Gamma property not implemented for this camera.",
        )
        return status

    def get_hue(self) -> Tuple[Status, CameraSetting, None]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Hue property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_hue(self, hue: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Hue property not implemented for this camera.",
        )
        return status

    def get_iris(self) -> Tuple[Status, CameraSetting, None]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Iris property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_iris(self, iris: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Iris property not implemented for this camera.",
        )
        return status

    def get_saturation(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Saturation property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_saturation(self, saturation: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Saturation property not implemented for this camera.",
        )
        return status

    def get_sharpness(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Sharpness property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_sharpness(self, sharpness: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Sharpness property not implemented for this camera.",
        )
        return status

    def get_shutter(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Shutter property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_shutter(self, shutter: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Shutter property not implemented for this camera.",
        )
        return status

    def get_white_balance_bu(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="WhiteBalanceBU property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_white_balance_bu(self, white_balance_bu: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="WhiteBalanceBU property not implemented for this camera.",
        )
        return status

    def get_white_balance_rv(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="WhiteBalanceRV property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_white_balance_rv(self, white_balance_rv: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="WhiteBalanceRV property not implemented for this camera.",
        )
        return status

    def get_zoom(self) -> Tuple[Status, CameraSetting]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="Zoom property not implemented for this camera.",
        )
        return status, CameraSetting()

    def set_zoom(self, zoom: CameraSetting) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="Zoom property not implemented for this camera.",
        )
        return status

    def get_stream_channel_id(self) -> Tuple[Status, Int64Value]:
        status = Status(
            code=StatusCode.UNIMPLEMENTED,
            why="StreamChannelID property not implemented for this camera.",
        )
        return status, Int64Value()

    def set_stream_channel_id(self, stream_channel_id: Int64Value) -> Status:
        status = Status(
            code=StatusCode.INTERNAL_ERROR,
            why="StreamChannelID property not implemented for this camera.",
        )
        return status

    def start_capture(self):
        raise NotImplementedError("Driver subclass must implement 'start_capture' method.")

    def stop_capture(self):
        raise NotImplementedError("Driver subclass must implement 'stop_capture' method.")

    def grab_image(self) -> Any:
        raise NotImplementedError("Driver subclass must implement 'grab_image' method.")

    def to_image(self, image: Any) -> Image:
        raise NotImplementedError("Driver subclass must implement 'to_image' method.")
