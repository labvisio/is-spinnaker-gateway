from typing import Any

from is_wire.core import StatusCode
from google.protobuf.wrappers_pb2 import FloatValue, Int64Value

from is_msgs.camera_pb2 import CameraSetting
from is_msgs.image_pb2 import Image, Resolution, ColorSpace, ImageFormat, BoundingPoly

from is_spinnaker_gateway.exceptions import StatusException


class CameraDriver:

    def get_resolution(self) -> Resolution:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Resolution property not implemented for this camera.",
        )

    def set_resolution(self, resolution: Resolution) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Resolution property not implemented for this camera.",
        )

    def get_format(self) -> ImageFormat:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="ImageFormat property not implemented for this camera.",
        )

    def set_format(self, image_format: ImageFormat) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="ImageFormat property not implemented for this camera.",
        )

    def get_color_space(self) -> ColorSpace:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="ColorSpace property not implemented for this camera.",
        )

    def set_color_space(self, color_space: ColorSpace) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="ColorSpace property not implemented for this camera.",
        )

    def get_region_of_interest(self) -> BoundingPoly:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="RegionOfInterest property not implemented for this camera.",
        )

    def set_region_of_interest(self, roi: BoundingPoly) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="RegionOfInterest property not implemented for this camera.",
        )

    def get_sampling_rate(self) -> FloatValue:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="SamplingRate property not implemented for this camera.",
        )

    def set_sampling_rate(self, sampling_rate: FloatValue) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="SamplingRate property not implemented for this camera.",
        )

    def get_delay(self) -> FloatValue:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Delay property not implemented for this camera.",
        )

    def set_delay(self, delay: FloatValue) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Delay property not implemented for this camera.",
        )

    def get_brightness(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Brightness property not implemented for this camera.",
        )

    def set_brightness(self, brightness: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Brightness property not implemented for this camera.",
        )

    def get_exposure(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Brightness property not implemented for this camera.",
        )

    def set_exposure(self, exposure: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Exposure property not implemented for this camera.",
        )

    def get_focus(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Focus property not implemented for this camera.",
        )

    def set_focus(self, focus: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Focus property not implemented for this camera.",
        )

    def get_gain(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Gain property not implemented for this camera.",
        )

    def set_gain(self, gain: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Gain property not implemented for this camera.",
        )

    def get_gamma(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Gamma property not implemented for this camera.",
        )

    def set_gamma(self, gamma: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Gamma property not implemented for this camera.",
        )

    def get_hue(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Hue property not implemented for this camera.",
        )

    def set_hue(self, hue: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Hue property not implemented for this camera.",
        )

    def get_iris(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Iris property not implemented for this camera.",
        )

    def set_iris(self, iris: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Iris property not implemented for this camera.",
        )

    def get_saturation(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Saturation property not implemented for this camera.",
        )

    def set_saturation(self, saturation: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Saturation property not implemented for this camera.",
        )

    def get_sharpness(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Sharpness property not implemented for this camera.",
        )

    def set_sharpness(self, sharpness: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Sharpness property not implemented for this camera.",
        )

    def get_shutter(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Shutter property not implemented for this camera.",
        )

    def set_shutter(self, shutter: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Shutter property not implemented for this camera.",
        )

    def get_white_balance_bu(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="WhiteBalanceBU property not implemented for this camera.",
        )

    def set_white_balance_bu(self, white_balance_bu: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="WhiteBalanceBU property not implemented for this camera.",
        )

    def get_white_balance_rv(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="WhiteBalanceRV property not implemented for this camera.",
        )

    def set_white_balance_rv(self, white_balance_rv: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="WhiteBalanceRV property not implemented for this camera.",
        )

    def get_zoom(self) -> CameraSetting:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="Zoom property not implemented for this camera.",
        )

    def set_zoom(self, zoom: CameraSetting) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="Zoom property not implemented for this camera.",
        )

    def get_stream_channel_id(self) -> Int64Value:
        raise StatusException(
            code=StatusCode.UNIMPLEMENTED,
            message="StreamChannelID property not implemented for this camera.",
        )

    def set_stream_channel_id(self, stream_channel_id: Int64Value) -> None:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message="StreamChannelID property not implemented for this camera.",
        )

    def start_capture(self) -> None:
        raise NotImplementedError("Driver subclass must implement 'start_capture' method.")

    def stop_capture(self) -> None:
        raise NotImplementedError("Driver subclass must implement 'stop_capture' method.")

    def grab_image(self) -> Any:
        raise NotImplementedError("Driver subclass must implement 'grab_image' method.")

    def to_image(self, image: Any) -> Image:
        raise NotImplementedError("Driver subclass must implement 'to_image' method.")
