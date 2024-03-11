import time
from queue import Empty, Queue
from threading import Thread
from typing import List, Optional

import cv2
import numpy as np
import numpy.typing as npt
import PySpin
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.wrappers_pb2 import FloatValue, Int64Value
from is_msgs.camera_pb2 import CameraSetting
from is_msgs.image_pb2 import (
    BoundingPoly,
    ColorSpace,
    ColorSpaces,
    Image,
    ImageFormat,
    ImageFormats,
    Resolution,
)
from is_wire.core import Logger, StatusCode
from turbojpeg import TurboJPEG

from is_spinnaker_gateway.conf.options_pb2 import ColorProcessingAlgorithm
from is_spinnaker_gateway.driver.interface import (
    CameraDriver,
    CameraEthernet,
    CameraInfo,
)
from is_spinnaker_gateway.driver.spinnaker.nodes import (
    get_op_enum,
    get_op_float,
    get_op_int,
    get_op_str,
    minmax_op_float,
    minmax_op_int,
    set_op_bool,
    set_op_enum,
    set_op_float,
    set_op_int,
)
from is_spinnaker_gateway.driver.spinnaker.utils import (
    ALGORITHM_MAP,
    get_ratio,
    get_value,
    make_ip_address,
    make_mac_address,
    make_subnet_mask,
)
from is_spinnaker_gateway.exceptions import StatusException


class SpinnakerDriver(CameraDriver):

    def __init__(
        self,
        use_turbojpeg: bool,
        compression_level: float,
        onboard_color_processing: bool,
        color_algorithm: ColorProcessingAlgorithm,
    ) -> None:
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
            if color_algorithm not in ALGORITHM_MAP:
                self._processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_BILINEAR)
            else:
                self._processor.SetColorProcessing(ALGORITHM_MAP[color_algorithm])
        else:
            self._processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_NONE)

        self._camera: PySpin.CameraPtr = None
        self._cam_info: CameraInfo = None  # type: ignore[assignment]
        self._timestamp = Timestamp()
        self._queue: Queue = Queue()
        self._running = False
        self._thread: Thread = None  # type: ignore[assignment]

    def find_cameras(self) -> List[CameraInfo]:
        cam_infos: List[CameraInfo] = []
        cam_list = self._system.GetCameras()
        n_cameras = cam_list.GetSize()
        for i in range(n_cameras):
            camera = cam_list.GetByIndex(i)
            try:
                ip_address = get_op_int(camera.GetTLDeviceNodeMap(), "GevDeviceIPAddress")
            except (PySpin.SpinnakerException, StatusException):
                continue
            try:
                subnet_mask = get_op_int(camera.GetTLDeviceNodeMap(), "GevDeviceSubnetMask")
            except (PySpin.SpinnakerException, StatusException):
                continue
            try:
                mac_addrees = get_op_int(camera.GetTLDeviceNodeMap(), "GevDeviceMACAddress")
            except (PySpin.SpinnakerException, StatusException):
                continue
            try:
                link_speed = get_op_int(camera.GetTLDeviceNodeMap(), "DeviceLinkSpeed")
            except (PySpin.SpinnakerException, StatusException):
                continue
            try:
                model_name = get_op_str(camera.GetTLDeviceNodeMap(), "DeviceModelName")
            except (PySpin.SpinnakerException, StatusException):
                continue
            try:
                serial_number = get_op_str(camera.GetTLDeviceNodeMap(), "DeviceSerialNumber")
            except (PySpin.SpinnakerException, StatusException):
                continue
            info = CameraInfo(
                interface=CameraEthernet(
                    ip_address=make_ip_address(ip_address),
                    subnet_mask=make_subnet_mask(subnet_mask),
                    mac_address=make_mac_address(mac_addrees),
                ),
                model_name=model_name,
                link_speed=link_speed,
                serial_number=serial_number,
            )
            cam_infos.append(info)
        cam_list.Clear()
        return cam_infos

    def connect(self, cam_info: CameraInfo, max_retries: int) -> None:
        self._cam_info = cam_info
        attempts = 0
        not_connected = True
        while not_connected:
            try:
                cam_list = self._system.GetCameras()
                self._camera = cam_list.GetBySerial(cam_info["serial_number"])
                self._camera.Init()
                cam_list.Clear()
                not_connected = False
            except PySpin.SpinnakerException as ex:
                attempts += 1
                if attempts > max_retries:
                    self._logger.critical("[Camera Initialize]: {}", ex)
                self._logger.warn("[Camera Initiliaze]: {}", ex)
                time.sleep(5)
        try:
            set_op_enum(node_map=self._camera.GetNodeMap(), name="UserSetSelector", value="Default")
            self._camera.UserSetLoad()
            set_op_enum(node_map=self._camera.GetNodeMap(), name="AcquisitionMode", value="Continuous")
            set_op_enum(node_map=self._camera.GetTLStreamNodeMap(), name="StreamBufferHandlingMode", value="OldestFirst")
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.critical("[Camera Initial Config]: {}", ex)

    def disconnect(self) -> None:
        try:
            self.stop_capture()
            self._camera.DeInit()
            del self._camera
            if not self._system.IsInUse():
                self._system.ReleaseInstance()
        except PySpin.SpinnakerException:
            pass

    def start_capture(self) -> None:
        try:
            if not self._camera.IsStreaming():
                self._camera.BeginAcquisition()
                self._running = True
                self._thread = Thread(target=self._reader, daemon=True)
                self._thread.start()
        except PySpin.SpinnakerException as ex:
            self._logger.critical("[Start Capture]: {}", ex)

    def stop_capture(self) -> None:
        try:
            if self._camera.IsStreaming():
                self._camera.EndAcquisition()
                self._running = False
                self._thread.join()
        except PySpin.SpinnakerException as ex:
            self._logger.critical("[Stop Capture]: {}", ex)

    def _to_array(self, image: PySpin.ImagePtr) -> npt.NDArray[np.uint8]:
        if not self._onboard_color_processing:
            if self._color_space == ColorSpaces.Value("RGB"):
                bgr = self._processor.Convert(image, PySpin.PixelFormat_BGR8)
            else:
                bgr = self._processor.Convert(image, PySpin.PixelFormat_Mono8)
            array = bgr.GetNDArray()
            # bgr.Release()
            return array
        array = image.GetNDArray()
        # image.Release()
        return array

    def _to_image(self, image: PySpin.ImagePtr) -> Image:
        array = self._to_array(image=image)
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

    def _reader(self) -> None:
        while self._running:
            image = self._grab_image()
            if not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except Empty:
                    pass
            self._queue.put(image)

    def _grab_image(self) -> Image:
        try:
            image = self._camera.GetNextImage(3000)
            is_incomplete = image.IsIncomplete()
            self._timestamp.GetCurrentTime()
            if is_incomplete:
                self._logger.warn("[Grab Image]: Image incomplete.")
                return Image()
            image_pb = self._to_image(image)
            return image_pb
        except PySpin.SpinnakerException as ex:
            self._logger.warn("[Grab Image]: Timeouted.", ex)
            return Image()

    def grab_image(self) -> Image:
        return self._queue.get()

    def last_timestamp(self) -> Timestamp:
        return self._timestamp

    def get_sampling_rate(self) -> FloatValue:
        value = get_op_float(self._camera.GetNodeMap(), "AcquisitionFrameRate")
        rate = FloatValue()
        rate.value = value
        return rate

    def set_sampling_rate(self, sampling_rate: FloatValue) -> None:
        if "BFS" in self._cam_info["model_name"]:
            set_op_bool(self._camera.GetNodeMap(), "AcquisitionFrameRateEnable", True)
        else:
            set_op_enum(self._camera.GetNodeMap(), "AcquisitionFrameRateAuto", "Off")
            set_op_bool(self._camera.GetNodeMap(), "AcquisitionFrameRateEnabled", True)
        set_op_float(self._camera.GetNodeMap(), "AcquisitionFrameRate", sampling_rate.value)

    def get_delay(self) -> FloatValue:
        msg = "'Delay' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_delay(self, delay: FloatValue) -> None:
        msg = "'Delay' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_resolution(self) -> Resolution:
        msg = "'Resolution' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_resolution(self, resolution: Resolution) -> None:
        msg = "'Resolution' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_format(self) -> ImageFormat:
        image_format = ImageFormat()
        image_format.format = self._encode_format
        image_format.compression.value = self._compression_level
        return image_format

    def set_format(self, image_format: ImageFormat) -> None:
        if image_format.format == ImageFormats.Value("JPEG"):
            self._encode_format = ImageFormats.Value("JPEG")
        elif image_format.format == ImageFormats.Value("PNG"):
            self._encode_format = ImageFormats.Value("PNG")
        elif image_format.format == ImageFormats.Value("WebP"):
            self._encode_format = ImageFormats.Value("WebP")
        else:
            msg = "'ImageFormat' property only accept JPEG, PNG or WebP values."
            raise StatusException(code=StatusCode.FAILED_PRECONDITION, message=msg)
        if image_format.compression.value > 0 and image_format.compression.value < 1:
            self._compression_level = image_format.compression.value
        else:
            msg = "Compression value must be greater than zero and less than one."
            raise StatusException(code=StatusCode.FAILED_PRECONDITION, message=msg)

    def get_color_space(self) -> ColorSpace:
        color_space = ColorSpace()
        color_space.value = self._color_space
        return color_space

    def set_color_space(self, color_space: ColorSpace) -> None:
        if not self._camera.IsStreaming():
            if color_space.value == ColorSpaces.Value("RGB"):
                self._color_space = color_space.value
                if self._onboard_color_processing:
                    set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "RGB8Packed")
                else:
                    set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "BayerRG8")
            elif color_space.value == ColorSpaces.Value("GRAY"):
                set_op_enum(self._camera.GetNodeMap(), "PixelFormat", "Mono8")
                self._color_space = color_space.value
            else:
                msg = "'ColorSpace' property only accept RGB or GRAY values."
                raise StatusException(code=StatusCode.FAILED_PRECONDITION, message=msg)
        else:
            msg = "'ColorSpace' property cannot be modify during streaming."
            raise StatusException(code=StatusCode.PERMISSION_DENIED, message=msg)

    def get_region_of_interest(self) -> BoundingPoly:
        roi = BoundingPoly()
        top_left = roi.vertices.add()
        top_left.x = get_op_int(self._camera.GetNodeMap(), "OffsetX")
        top_left.y = get_op_int(self._camera.GetNodeMap(), "OffsetY")
        bottom_right = roi.vertices.add()
        bottom_right.x = top_left.x + get_op_int(self._camera.GetNodeMap(), "Width")
        bottom_right.y = top_left.y + get_op_int(self._camera.GetNodeMap(), "Height")
        return roi

    def set_region_of_interest(self, roi: BoundingPoly) -> None:
        if not self._camera.IsStreaming():
            if (len(roi.vertices) > 2) or (len(roi.vertices) < 2):
                msg = "'RegionOfInterest' property must have 2 vertices."
                raise StatusException(code=StatusCode.INVALID_ARGUMENT, message=msg)
            max_height = get_op_int(self._camera.GetNodeMap(), "HeightMax")
            max_width = get_op_int(self._camera.GetNodeMap(), "WidthMax")
            top_left = roi.vertices[0]
            bottom_right = roi.vertices[1]
            if (top_left.x >= bottom_right.x) or (top_left.y >= bottom_right.y):
                msg = "'RegionOfInterest' property must have acceptable vertices."
                raise StatusException(code=StatusCode.INVALID_ARGUMENT, message=msg)
            width = int(bottom_right.x - top_left.x)
            height = int(bottom_right.y - top_left.y)
            set_op_int(self._camera.GetNodeMap(), "Width", min(width, max_width))
            set_op_int(self._camera.GetNodeMap(), "Height", min(height, max_height))
            offset_x_range = minmax_op_int(self._camera.GetNodeMap(), "OffsetX")
            offset_y_range = minmax_op_int(self._camera.GetNodeMap(), "OffsetY")
            set_op_int(self._camera.GetNodeMap(), "OffsetX", min(offset_x_range[1], int(top_left.x)))
            set_op_int(self._camera.GetNodeMap(), "OffsetY", min(offset_y_range[1], int(top_left.y)))
        else:
            msg = "'RegionOfInterest' property cannot be modify during streaming."
            raise StatusException(code=StatusCode.PERMISSION_DENIED, message=msg)

    def get_brightness(self) -> CameraSetting:
        setting = CameraSetting()
        value = get_op_float(self._camera.GetNodeMap(), "BlackLevel")
        value_range = minmax_op_float(self._camera.GetNodeMap(), "BlackLevel")
        setting.ratio = get_ratio(value, value_range[0], value_range[1])
        setting.automatic = False
        return setting

    def set_brightness(self, brightness: CameraSetting) -> None:
        value_range = minmax_op_float(self._camera.GetNodeMap(), "BlackLevel")
        value = get_value(brightness.ratio, value_range[0], value_range[1])
        set_op_float(self._camera.GetNodeMap(), "BlackLevel", value)

    def get_exposure(self) -> CameraSetting:
        msg = "'Exposure' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_exposure(self, exposure: CameraSetting) -> None:
        msg = "'Exposure' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_focus(self) -> CameraSetting:
        msg = "'Focus' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_focus(self, focus: CameraSetting) -> None:
        msg = "'Exposure' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_gain(self) -> CameraSetting:
        setting = CameraSetting()
        auto = get_op_enum(self._camera.GetNodeMap(), "GainAuto")
        setting.automatic = auto == "Continuous"
        value = get_op_float(self._camera.GetNodeMap(), "Gain")
        value_range = minmax_op_float(self._camera.GetNodeMap(), "Gain")
        setting.ratio = get_ratio(value, value_range[0], value_range[1])
        return setting

    def set_gain(self, gain: CameraSetting) -> None:
        if gain.automatic:
            set_op_enum(self._camera.GetNodeMap(), "GainAuto", "Continuous")
        else:
            set_op_enum(self._camera.GetNodeMap(), "GainAuto", "Off")
            value_range = minmax_op_float(self._camera.GetNodeMap(), "Gain")
            value = get_value(gain.ratio, value_range[0], value_range[1])
            set_op_float(self._camera.GetNodeMap(), "Gain", value)

    def get_gamma(self) -> CameraSetting:
        msg = "'Gamma' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_gamma(self, gamma: CameraSetting) -> None:
        msg = "'Gamma' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_hue(self) -> CameraSetting:
        msg = "'Hue' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_hue(self, hue: CameraSetting) -> None:
        msg = "'Hue' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_iris(self) -> CameraSetting:
        msg = "'Iris' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_iris(self, iris: CameraSetting) -> None:
        msg = "'Iris' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_saturation(self) -> CameraSetting:
        msg = "'Saturation' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_saturation(self, saturation: CameraSetting) -> None:
        msg = "'Saturation' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_sharpness(self) -> CameraSetting:
        msg = "'Sharpness' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_sharpness(self, sharpness: CameraSetting) -> None:
        msg = "'Sharpness' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_shutter(self) -> CameraSetting:
        setting = CameraSetting()
        auto = get_op_enum(self._camera.GetNodeMap(), "ExposureAuto")
        setting.automatic = auto == "Continuous"
        value_range = minmax_op_float(self._camera.GetNodeMap(), "ExposureTime")
        value = get_op_float(self._camera.GetNodeMap(), "ExposureTime")
        setting.ratio = get_ratio(value, value_range[0], value_range[1])
        return setting

    def set_shutter(self, shutter: CameraSetting) -> None:
        if shutter.automatic:
            set_op_enum(self._camera.GetNodeMap(), "ExposureAuto", "Continuous")
        else:
            set_op_enum(self._camera.GetNodeMap(), "ExposureAuto", "Off")
            value_range = minmax_op_float(self._camera.GetNodeMap(), "ExposureTime")
            value = get_value(shutter.ratio, value_range[0], value_range[1])
            set_op_float(self._camera.GetNodeMap(), "ExposureTime", value)

    def get_white_balance(self, choice: str) -> CameraSetting:
        if self._color_space != ColorSpaces.Value("RGB"):
            msg = "'WhiteBalance' property availabe just on RGB color space"
            raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)
        setting = CameraSetting()
        auto = get_op_enum(self._camera.GetNodeMap(), "BalanceWhiteAuto")
        if auto == "Continuous":
            setting.automatic = True
        else:
            setting.automatic = False
            set_op_enum(self._camera.GetNodeMap(), "BalanceRatioSelector", choice)
            value = get_op_float(self._camera.GetNodeMap(), "BalanceRatio")
            value_range = minmax_op_float(self._camera.GetNodeMap(), "BalanceRatio")
            setting.ratio = get_ratio(value, value_range[0], value_range[1])
        return setting

    def set_white_balance(self, white_balance: CameraSetting, choice: str) -> None:
        if self._color_space != ColorSpaces.Value("RGB"):
            msg = "'WhiteBalance' property availabe just on RGB color space"
            raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)
        if white_balance.automatic:
            set_op_enum(self._camera.GetNodeMap(), "BalanceWhiteAuto", "Continuous")
        else:
            set_op_enum(self._camera.GetNodeMap(), "BalanceWhiteAuto", "Off")
            set_op_enum(self._camera.GetNodeMap(), "BalanceRatioSelector", choice)
            value_range = minmax_op_float(self._camera.GetNodeMap(), "BalanceRatio")
            value = get_value(white_balance.ratio, value_range[0], value_range[1])
            set_op_float(self._camera.GetNodeMap(), "BalanceRatio", value)

    def get_white_balance_bu(self) -> CameraSetting:
        return self.get_white_balance(choice="Blue")

    def set_white_balance_bu(self, white_balance_bu: CameraSetting) -> None:
        self.set_white_balance(white_balance=white_balance_bu, choice="Blue")

    def get_white_balance_rv(self) -> CameraSetting:
        return self.get_white_balance(choice="Red")

    def set_white_balance_rv(self, white_balance_rv: CameraSetting) -> None:
        self.set_white_balance(white_balance=white_balance_rv, choice="Red")

    def get_zoom(self) -> CameraSetting:
        msg = "'Zoom' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_zoom(self, zoom: CameraSetting) -> None:
        msg = "'Zoom' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def get_stream_channel_id(self) -> Int64Value:
        msg = "'StreamChannelID' property not implemented for this camera."
        raise StatusException(code=StatusCode.UNIMPLEMENTED, message=msg)

    def set_stream_channel_id(self, stream_channel_id: Int64Value) -> None:
        msg = "'StreamChannelID' property not implemented for this camera."
        raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg)

    def set_reverse_x(self, reverse_x: bool) -> None:
        try:
            set_op_bool(self._camera.GetNodeMap(), "ReverseX", reverse_x)
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.warn("[ReverseX]: {}", ex)

    def set_packet_size(self, packet_size: int) -> None:
        try:
            set_op_int(self._camera.GetNodeMap(), "GevSCPSPacketSize", packet_size)
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.warn("[PacketSize]: {}", ex)

    def set_packet_delay(self, packet_delay: int) -> None:
        try:
            set_op_int(self._camera.GetNodeMap(), "GevSCPD", packet_delay)
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.warn("[PacketDelay]: {}", ex)

    def set_packet_resend(self, packet_resend: bool) -> None:
        try:
            set_op_bool(self._camera.GetTLStreamNodeMap(), "StreamPacketResendEnable", packet_resend)
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.warn("[PacketResend]: {}", ex)

    def set_packet_resend_timeout(self, timeout: int) -> None:
        try:
            set_op_int(self._camera.GetTLStreamNodeMap(), "StreamPacketResendTimeout", timeout)
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.warn("[PacketResendTimeout]: {}", ex)

    def set_packet_resend_max_requests(self, max_requests: int) -> None:
        try:
            set_op_int(self._camera.GetTLStreamNodeMap(), "StreamPacketResendMaxRequests", max_requests)
        except (PySpin.SpinnakerException, StatusException) as ex:
            self._logger.warn("[PacketResendMaxRequests]: {}", ex)
