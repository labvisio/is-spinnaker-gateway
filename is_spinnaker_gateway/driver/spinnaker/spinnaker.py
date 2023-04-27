from typing import Union, List

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
    BoundingPoly,
)

from is_spinnaker_gateway.logger import Logger
from is_spinnaker_gateway.driver.base import CameraDriver
from is_spinnaker_gateway.exceptions import StatusException
from is_spinnaker_gateway.conf.options_pb2 import ColorProcessingAlgorithm
from is_spinnaker_gateway.driver.spinnaker.utils import (
    set_op_enum,
    get_op_enum,
    get_op_int,
    set_op_int,
    get_op_float,
    set_op_float,
    set_op_bool,
    minmax_op_int,
    minmax_op_float,
    get_value,
    get_ratio,
)


class SpinnakerDriver(CameraDriver):

    def __init__(self, use_turbojpeg: bool, compression_level: float,
                 onboard_color_processing: bool, color_algorithm: ColorProcessingAlgorithm):
        super().__init__()
        self._logger = Logger("SpinnakerDriver")
        self._encoder = TurboJPEG()
        self._use_turbojpeg = use_turbojpeg
        self._compression_level = compression_level
        self._color_space = ColorSpaces.Value("RGB")
        self._encode_format = ImageFormats.Value("JPEG")
        self._onboard_color_processing = onboard_color_processing
        self._system = PySpin.System.GetInstance()
        self._processor = PySpin.ImageProcessor()
        if not onboard_color_processing:
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
        else:
            self._processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_NONE)
        self.running = False
        self.initied = False

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
            ip_address = get_op_int(self._camera.GetTLDeviceNodeMap(), "GevDeviceIPAddress")
            ip_address = self.get_ip(ip_address)
            if ip == ip_address:
                try:
                    self._camera.Init()
                    self.initied = True
                except PySpin.SpinnakerException as ex:
                    self._logger.critical("Spinnaker Exception \n{}", ex)

                set_op_enum(self._camera.GetNodeMap(), "UserSetSelector", "Default")
                self._camera.UserSetLoad()
                self._logger.info("Loaded default configuration.")

                set_op_enum(self._camera.GetNodeMap(), "AcquisitionMode", "Continuous")
                set_op_enum(self._camera.GetTLStreamNodeMap(), "StreamBufferHandlingMode",
                            "NewestOnly")
                self._logger.info("Connected to camera with IP='{}'", ip_address)
                not_found = False

            i += 1
        cam_list.Clear()

    def get_ip(self, ip: int) -> str:
        ip_list = self.int2base(x=ip, base=256)
        return ".".join([str(i) for i in ip_list])

    def close(self):
        try:
            if self._camera.IsStreaming():
                self._camera.EndAcquisition()
            self._camera.DeInit()
            del self._camera
            if not self._system.IsInUse():
                self._system.ReleaseInstance()
        except PySpin.SpinnakerException:
            pass

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
        if not self._camera.IsStreaming():
            self._camera.BeginAcquisition()

    def stop_capture(self):
        if self._camera.IsStreaming():
            self._camera.EndAcquisition()

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
            if self._use_turbojpeg and self._color_space == ColorSpaces.Value("RGB"):
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

    def get_sampling_rate(self) -> FloatValue:
        value = get_op_float(self._camera.GetNodeMap(), "AcquisitionFrameRate")
        rate = FloatValue()
        rate.value = value
        return rate

    def set_sampling_rate(self, sampling_rate: FloatValue):
        set_op_enum(self._camera.GetNodeMap(), "AcquisitionFrameRateAuto", "Off")
        set_op_bool(self._camera.GetNodeMap(), "AcquisitionFrameRateEnabled", True)
        set_op_float(self._camera.GetNodeMap(), "AcquisitionFrameRate", sampling_rate.value)

    def get_color_space(self) -> ColorSpace:
        color_space = ColorSpace()
        color_space.value = self._color_space
        return color_space

    def set_color_space(self, color_space: ColorSpace):
        if not self._camera.IsStreaming():
            if color_space.value == ColorSpaces.Value("RGB"):
                self._color_space = color_space.value
                if self._onboard_color_processing:
                    set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "RGB8Packed")
                else:
                    set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "BayerRG8")
            elif color_space.value == ColorSpaces.Value("GRAY"):
                set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "Mono8")
                self._color_space = ColorSpaces.Value("GRAY")
            else:
                raise StatusException(
                    code=StatusCode.FAILED_PRECONDITION,
                    message="'ColorSpace' property only accept RGB or GRAY values.",
                )
        else:
            raise StatusException(
                code=StatusCode.PERMISSION_DENIED,
                message="'ColorSpace' property cannot be modify during streaming.",
            )

    def get_format(self) -> ImageFormat:
        image_format = ImageFormat()
        image_format.format = self._encode_format
        image_format.compression.value = self._compression_level
        return image_format

    def set_format(self, image_format: ImageFormat):
        if image_format.format == ImageFormats.Value("JPEG"):
            self._encode_format = ImageFormats.Value("JPEG")
        elif image_format.format == ImageFormats.Value("PNG"):
            self._encode_format = ImageFormats.Value("PNG")
        elif image_format.format == ImageFormats.Value("WebP"):
            self._encode_format = ImageFormats.Value("WebP")
        else:
            raise StatusException(
                code=StatusCode.FAILED_PRECONDITION,
                message="'ImageFormat' property only accept JPEG, PNG or WebP values.",
            )
        if image_format.compression.value > 0 and image_format.compression.value < 1:
            self._compression_level = image_format.compression.value
        else:
            raise StatusException(
                code=StatusCode.FAILED_PRECONDITION,
                message="Compression value must be greater than zero and less than one.",
            )

    def get_region_of_interest(self) -> BoundingPoly:
        roi = BoundingPoly()
        top_left = roi.vertices.add()
        top_left.x = get_op_int(self._camera.GetNodeMap(), "OffsetX")
        top_left.y = get_op_int(self._camera.GetNodeMap(), "OffsetY")
        bottom_right = roi.vertices.add()
        bottom_right.x = top_left.x + get_op_int(self._camera.GetNodeMap(), "Width")
        bottom_right.y = top_left.y + get_op_int(self._camera.GetNodeMap(), "Height")
        return roi

    def set_region_of_interest(self, roi: BoundingPoly):
        if not self._camera.IsStreaming():
            if (len(roi.vertices) > 2) or (len(roi.vertices) < 2):
                raise StatusException(
                    code=StatusCode.INVALID_ARGUMENT,
                    message="'RegionOfInterest' property must have 2 vertices.",
                )
            max_height = get_op_int(self._camera.GetNodeMap(), "HeightMax")
            max_width = get_op_int(self._camera.GetNodeMap(), "WidthMax")
            top_left = roi.vertices[0]
            bottom_right = roi.vertices[1]
            if (top_left.x >= bottom_right.x) or (top_left.y >= bottom_right.y):
                raise StatusException(
                    code=StatusCode.INVALID_ARGUMENT,
                    message="'RegionOfInterest' property must have acceptable vertices.",
                )
            width = int(bottom_right.x - top_left.x)
            height = int(bottom_right.y - top_left.y)
            set_op_int(self._camera.GetNodeMap(), "Width", min(width, max_width))
            set_op_int(self._camera.GetNodeMap(), "Height", min(height, max_height))
            offset_x_range = minmax_op_int(self._camera.GetNodeMap(), "OffsetX")
            offset_y_range = minmax_op_int(self._camera.GetNodeMap(), "OffsetY")
            set_op_int(self._camera.GetNodeMap(), "OffsetX", min(offset_x_range[1],
                                                                 int(top_left.x)))
            set_op_int(self._camera.GetNodeMap(), "OffsetY", min(offset_y_range[1],
                                                                 int(top_left.y)))
        else:
            raise StatusException(
                code=StatusCode.PERMISSION_DENIED,
                message="'RegionOfInterest' property cannot be modify during streaming.",
            )

    # def get_resolution(self) -> Resolution:
    #     resolution = Resolution()
    #     width = get_op_int(self._camera.GetNodeMap(), "Width")
    #     height = get_op_int(self._camera.GetNodeMap(), "Height")
    #     resolution.width = width
    #     resolution.height = height
    #     return resolution

    def set_gain(self, gain: CameraSetting):
        if gain.automatic:
            set_op_enum(self._camera.GetNodeMap(), "GainAuto", "Continuous")
        else:
            set_op_enum(self._camera.GetNodeMap(), "GainAuto", "Off")
            value_range = minmax_op_float(self._camera.GetNodeMap(), "Gain")
            value = get_value(gain.ratio, value_range[0], value_range[1])
            set_op_float(self._camera.GetNodeMap(), "Gain", value)

    def get_gain(self) -> CameraSetting:
        setting = CameraSetting()
        auto = get_op_enum(self._camera.GetNodeMap(), "GainAuto")
        if auto == "Continuous":
            setting.automatic = True
        else:
            setting.automatic = False
            value = get_op_float(self._camera.GetNodeMap(), "Gain")
            value_range = minmax_op_float(self._camera.GetNodeMap(), "Gain")
            setting.ratio = get_ratio(value, value_range[0], value_range[1])
        return setting

    def get_brightness(self):
        setting = CameraSetting()
        value = get_op_float(self._camera.GetNodeMap(), "BlackLevel")
        value_range = minmax_op_float(self._camera.GetNodeMap(), "BlackLevel")
        setting.ratio = get_ratio(value, value_range[0], value_range[1])
        setting.automatic = False
        return setting

    def set_brightness(self, brightness: CameraSetting) -> CameraSetting:
        value_range = minmax_op_float(self._camera.GetNodeMap(), "BlackLevel")
        value = get_value(brightness.ratio, value_range[0], value_range[1])
        set_op_float(self._camera.GetNodeMap(), "BlackLevel", value)

    def set_reverse_x(self, reverse_x: bool) -> Status:
        set_op_bool(self._camera.GetNodeMap(), "ReverseX", reverse_x)

    def set_packet_size(self, packet_size: int) -> Status:
        set_op_int(self._camera.GetNodeMap(), "GevSCPSPacketSize", packet_size)

    def set_packet_delay(self, packet_delay: int) -> Status:
        set_op_int(self._camera.GetNodeMap(), "GevSCPD", packet_delay)

    def set_packet_resend(self, packet_resend: bool) -> Status:
        set_op_bool(self._camera.GetTLStreamNodeMap(), "StreamPacketResendEnable", packet_resend)

    def set_packet_resend_timeout(self, timeout: int) -> Status:
        set_op_int(self._camera.GetTLStreamNodeMap(), "StreamPacketResendTimeout", timeout)

    def set_packet_resend_max_requests(self, max_requests: int) -> Status:
        set_op_int(self._camera.GetTLStreamNodeMap(), "StreamPacketResendMaxRequests",
                   max_requests)
