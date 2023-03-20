from typing import Union, Tuple, List, Any

import cv2
import PySpin
import numpy as np

from turbojpeg import TurboJPEG
from is_wire.core import Status, StatusCode
from google.protobuf.wrappers_pb2 import FloatValue

from is_msgs.camera_pb2 import CameraSetting
from is_msgs.image_pb2 import (
    Image,
    ColorSpace,
    ColorSpaces,
    ImageFormat,
    ImageFormats,
    Resolution,
)

from is_spinnaker_gateway.logger import Logger
from is_spinnaker_gateway.driver.base import CameraDriver
from is_spinnaker_gateway.conf.options_pb2 import ColorProcessingAlgorithm
from is_spinnaker_gateway.driver.spinnaker.utils import (
    set_op_enum,
    get_op_enum,
    get_op_int,
    set_op_int,
    get_op_float,
    set_op_float,
    set_op_bool,
    minmax_op_float,
)


class SpinnakerDriver(CameraDriver):

    def __init__(self,
                 use_turbojpeg: bool = True,
                 compression_level: float = 0.8,
                 onboard_color_processing: bool = False,
                 color_algorithm: ColorProcessingAlgorithm = ColorProcessingAlgorithm.BILINEAR):

        super(CameraDriver, self).__init__()
        self._logger = Logger("SpinnakerDriver")
        self._logger.set_critical_callback(callback=self.close)
        self._encoder = TurboJPEG()
        self._use_turbojpeg = use_turbojpeg
        self._compression_level = compression_level
        self._color_space = ColorSpaces.Value("RGB")
        self._encode_format = ImageFormats.Value("JPEG")
        self._onboard_color_processing = onboard_color_processing
        self._system = PySpin.System.GetInstance()
        if not onboard_color_processing:
            self._processor = PySpin.ImageProcessor()
            if color_algorithm == ColorProcessingAlgorithm.Value("NEAREST_NEIGHBOR"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_NEAREST_NEIGHBOR,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("NEAREST_NEIGHBOR_AVERAGE"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_NEAREST_NEIGHBOR_AVG,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("EDGE_SENSING"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_EDGE_SENSING,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("HQ_LINEAR"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("BILINEAR"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_BILINEAR,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("DIRECTIONAL_FILTER"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_DIRECTIONAL_FILTER,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("WEIGHTED_DIRECTIONAL_FILTER"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_WEIGHTED_DIRECTIONAL_FILTER,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("RIGOROUS"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_RIGOROUS,
                )
            elif color_algorithm == ColorProcessingAlgorithm.Value("IPP"):
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_IPP,
                )
            else:
                self._processor.SetColorProcessing(
                    PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_BILINEAR,
                )
        self.running = False
        self.initied = False

    def make_failed_set(self, code: StatusCode, property: str, value: Any):
        if code != StatusCode.OK:
            self._logger.critical("Cannot set '{}' to '{}'.", property, value)

    def connect(self, ip: str = "10.20.6.0"):
        cam_list = self._system.GetCameras()
        n_cameras = cam_list.GetSize()
        self._logger.info("Found {} cameras.".format(n_cameras))

        not_found = True
        i = 0
        while not_found:
            try:
                self._camera = cam_list.GetByIndex(i)
            except PySpin.SpinnakerException as ex:
                self._logger.critical("Spinnaker Exception \n{}", ex)

            code, ip_address = get_op_int(self._camera.GetTLDeviceNodeMap(), "GevDeviceIPAddress")
            if code != StatusCode.OK:
                self._logger.warn("Cannot get 'GevDeviceIPAddress' from camera {}.", i)

            ip_address = self.get_ip(ip_address)
            if ip == ip_address:
                try:
                    self._camera.Init()
                    self.initied = True
                except PySpin.SpinnakerException as ex:
                    self._logger.critical("Spinnaker Exception \n{}", ex)

                code = set_op_enum(self._camera.GetNodeMap(), "UserSetSelector", "Default")
                self.make_failed_set(code, "UserSetSelector", "Default")

                try:
                    self._camera.UserSetLoad()
                    self._logger.info("Loaded default configuration.")
                except PySpin.SpinnakerException as ex:
                    self._logger.critical("Spinnaker Exception \n{}", ex)

                code = set_op_enum(self._camera.GetNodeMap(), "AcquisitionMode", "Continuous")
                self.make_failed_set(code, "AcquisitionMode", "Continuous")

                code = set_op_enum(self._camera.GetNodeMap(), "TriggerMode", "Off")
                self.make_failed_set(code, "TriggerMode", "Off")

                code = set_op_enum(self._camera.GetNodeMap(), "TriggerSelector", "FrameStart")
                self.make_failed_set(code, "TriggerSelector", "FrameStart")

                self._logger.info("Connected to camera with IP='{}'", ip_address)
                not_found = False

            i += 1
        cam_list.Clear()

    def get_ip(self, ip: int) -> str:
        ip_list = self.int2base(x=ip, base=256)
        return ".".join([str(i) for i in ip_list])

    def close(self):
        if self.initied:
            self._camera.DeInit()
            del self._camera
        self._system.ReleaseInstance()

    @staticmethod
    def int2base(x: int, base: int) -> List[int]:
        if x == 0:
            return 0
        digits = []
        while x:
            digits.append(x % base)
            x = int(x / base)
        digits.reverse()
        return digits

    def start_capture(self):
        if not self.running:
            self._camera.BeginAcquisition()
            self.running = True

    def stop_capture(self):
        if self.running:
            self._camera.EndAcquisition()
        self.running = False

    def to_array(self, image: PySpin.ImagePtr) -> np.ndarray:
        if not self._onboard_color_processing:
            if self._color_space == ColorSpaces.Value("RGB"):
                bgr = self._processor.Convert(image, PySpin.PixelFormat_BGR8)
            else:
                bgr = self._processor.Convert(image, PySpin.PixelFormat_Mono8)
            array = bgr.GetNDArray()
        else:
            array = image.GetNDArray()
        image.Release()
        return array

    def to_image(self, image: PySpin.ImagePtr) -> Image:
        array = self.to_array(image=image)
        if self._encode_format == ImageFormats.Value("JPEG"):
            if self._use_turbojpeg:
                quality = int(self._compression_level * (100 - 0) + 0)
                return Image(data=self._encoder.encode(array, quality=quality))
            else:
                encode_format = ".jpeg"
                params = [cv2.IMWRITE_JPEG_QUALITY, int(self._compression_level * (100 - 0) + 0)]
        elif self._encode_format == ImageFormats.Value("PNG"):
            encode_format = ".png"
            params = [cv2.IMWRITE_PNG_COMPRESSION, int(self._compression_level * (9 - 0) + 0)]
        elif self._encode_format == ImageFormats.Value("WebP"):
            encode_format = ".webp"
            params = [cv2.IMWRITE_WEBP_QUALITY, int(self._compression_level * (100 - 1) + 1)]
        else:
            return Image()
        cimage = cv2.imencode(ext=encode_format, img=array, params=params)
        return Image(data=cimage[1].tobytes())

    def grab_image(self, wait: bool = True) -> Union[PySpin.ImagePtr, None]:
        try:
            if wait:
                image = self._camera.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)
            else:
                image = self._camera.GetNextImage(PySpin.EVENT_TIMEOUT_NONE)
            if image.IsIncomplete():
                self._logger.warn('Image incomplete with status {}.', image.GetImageStatus())
                image.Release()
                return None
            else:
                return image
        except PySpin.SpinnakerException as ex:
            self._logger.warn('Spinnaker Exception: {}.', ex)
            return None

    def get_sampling_rate(self) -> Tuple[Status, FloatValue]:
        code, value = get_op_float(self._camera.GetNodeMap(), "AcquisitionFrameRate")
        rate = FloatValue()
        rate.value = value
        return Status(code=code), rate

    def set_sampling_rate(self, sampling_rate: FloatValue) -> Status:
        code = set_op_enum(self._camera.GetNodeMap(), "AcquisitionFrameRateAuto", "Off")
        if code != StatusCode.OK:
            return Status(
                code=code,
                why="Failed to set 'AcquisitionFrameRateAuto' to 'Off'.",
            )
        code = set_op_bool(self._camera.GetNodeMap(), "AcquisitionFrameRateEnabled", True)
        if code != StatusCode.OK:
            return Status(
                code=code,
                why="Failed to set 'AcquisitionFrameRateEnabled' to 'True'.",
            )
        code = set_op_float(self._camera.GetNodeMap(), "AcquisitionFrameRate", sampling_rate.value)
        if code != StatusCode.OK:
            return Status(
                code=code,
                why=f"Failed to set 'AcquisitionFrameRate' to '{sampling_rate.value}'.",
            )
        return Status(code=StatusCode.OK)

    def get_color_space(self) -> Tuple[Status, ColorSpace]:
        color_space = ColorSpace()
        color_space.value = self._color_space
        return Status(code=StatusCode.OK), color_space

    def set_color_space(self, color_space: ColorSpace) -> Status:
        if color_space.value == ColorSpaces.Value("RGB"):
            self._color_space = color_space.value
            if self._onboard_color_processing:
                code = set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "RGB8Packed")
                return Status(code=code, why="Failed to set 'PixelFormat' to 'RGB8Packed'.")
            else:
                code = set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "BayerRG8")
                return Status(code=code, why="Failed to set 'PixelFormat' to 'BayerRG8'.")
        elif color_space.value == ColorSpaces.Value("GRAY"):
            code = set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "Mono8")
            return Status(code=code, why="Failed to set 'PixelFormat' to 'Mono8'.")
        else:
            return Status(
                code=StatusCode.FAILED_PRECONDITION,
                why="'ColorSpace' property only accept RGB or GRAY values.",
            )

    def get_format(self) -> Tuple[Status, ImageFormat]:
        image_format = ImageFormat()
        image_format.format = self._encode_format
        image_format.compression.value = self._compression_level
        return Status(code=StatusCode.OK), image_format

    def set_format(self, image_format: ImageFormat) -> Status:
        if image_format.format == ImageFormats.Value("JPEG"):
            self._encode_format = ImageFormats.Value("JPEG")
        elif image_format.format == ImageFormats.Value("PNG"):
            self._encode_format = ImageFormats.Value("PNG")
        elif image_format.format == ImageFormats.Value("WebP"):
            self._encode_format = ImageFormats.Value("WebP")
        else:
            return Status(
                code=StatusCode.FAILED_PRECONDITION,
                why="'ImageFormat' property only accept JPEG, PNG or WebP values.",
            )
        if image_format.compression.value > 0 and image_format.compression.value < 1:
            self._compression_level = image_format.compression.value
            return Status(code=StatusCode.OK)
        else:
            return Status(
                code=StatusCode.FAILED_PRECONDITION,
                why="Compression value must be greater than zero and less than one.",
            )

    def get_resolution(self) -> Tuple[Status, Resolution]:
        resolution = Resolution()
        code, width = get_op_int(self._camera.GetNodeMap(), "Width")
        if code != StatusCode.OK:
            return Status(code=code, why="Failed to get 'Width' property."), resolution
        code, height = get_op_int(self._camera.GetNodeMap(), "Width")
        if code != StatusCode.OK:
            return Status(code=code, why="Failed to get 'Height' property."), resolution
        resolution.width = width
        resolution.height = height
        return Status(code=StatusCode.OK), resolution

    def set_gain(self, gain: CameraSetting) -> Status:
        if gain.automatic:
            code = set_op_enum(self._camera.GetNodeMap(), "GainAuto", "Continuous")
            return Status(code=code)
        else:
            code = set_op_enum(self._camera.GetNodeMap(), "GainAuto", "Off")
            if code != StatusCode.OK:
                return Status(code=code, why="Failed to set 'GainAuto' to 'Off'.")
            code, value_range = minmax_op_float(self._camera.GetNodeMap(), "Gain")
            if code != StatusCode.OK:
                return Status(code=code, why="Failed to get 'Gain' property.")
            value = (gain.ratio * (value_range[1] - value_range[0]) / 100) + value_range[0]
            code = set_op_float(self._camera.GetNodeMap(), "Gain", value)
            if code != StatusCode.OK:
                return Status(code=code, why=f"Failed to set 'Gain' to {value}.")
            return Status(code=StatusCode.OK)

    def get_gain(self) -> Tuple[Status, CameraSetting]:
        setting = CameraSetting()
        code, auto = get_op_enum(self._camera.GetNodeMap(), "GainAuto")
        if code != StatusCode.OK:
            return setting, Status(code=code, why="Failed to get 'GainAuto' property")
        if auto == "Continuous":
            setting.automatic = True
        else:
            setting.automatic = False
        code, value = get_op_float(self._camera.GetNodeMap(), "Gain")
        if code != StatusCode.OK:
            return Status(code=code, why=f"Failed to set 'Gain' to '{value}'"), setting
        code, value_range = minmax_op_float(self._camera.GetNodeMap(), "Gain")
        if code != StatusCode.OK:
            return Status(code=code, why="Failed to get 'Gain' property"), setting
        setting.ratio = ((value - value_range[0]) * 100) / (value_range[1] - value_range[0])
        return Status(code=StatusCode.OK), setting

    def set_reverse_y(self, reverse_y: bool) -> Status:
        code = set_op_bool(self._camera.GetNodeMap(), "ReverseY", reverse_y)
        self.make_failed_set(code, "ReverseY", reverse_y)

    def set_reverse_x(self, reverse_x: bool) -> Status:
        code = set_op_bool(self._camera.GetNodeMap(), "ReverseX", reverse_x)
        self.make_failed_set(code, "ReverseX", reverse_x)

    def set_packet_size(self, packet_size: int) -> Status:
        code = set_op_int(self._camera.GetNodeMap(), "GevSCPSPacketSize", packet_size)
        self.make_failed_set(code, "GevSCPSPacketSize", packet_size)

    def set_packet_delay(self, packet_delay: int) -> Status:
        code = set_op_int(self._camera.GetNodeMap(), "GevSCPD", packet_delay)
        self.make_failed_set(code, "GevSCPD", packet_delay)

    def set_packet_resend(self, packet_resend: bool) -> Status:
        code = set_op_bool(
            self._camera.GetTLStreamNodeMap(),
            "StreamPacketResendEnable",
            packet_resend,
        )
        self.make_failed_set(code, "StreamPacketResendEnable", packet_resend)

    def set_packet_resend_timeout(self, packet_resend_timeout: int) -> Status:
        code = set_op_int(
            self._camera.GetTLStreamNodeMap(),
            "StreamPacketResendTimeout",
            packet_resend_timeout,
        )
        self.make_failed_set(code, "StreamPacketResendTimeout", packet_resend_timeout)

    def set_packet_resend_max_requests(self, packet_resend_max_requests: int) -> Status:
        code = set_op_int(
            self._camera.GetTLStreamNodeMap(),
            "StreamPacketResendMaxRequests",
            packet_resend_max_requests,
        )
        self.make_failed_set(code, "StreamPacketResendMaxRequests", packet_resend_max_requests)
