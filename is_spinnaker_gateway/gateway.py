import re
import time
import socket

from typing import Tuple, Any, Union

from dateutil import parser as dp

from google.protobuf.empty_pb2 import Empty
from google.protobuf.json_format import Parse

from opencensus.trace.span import Span
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter

from is_wire.rpc.context import Context
from is_wire.rpc import ServiceProvider, LogInterceptor, TracingInterceptor
from is_wire.core import Channel, Message, AsyncTransport, Tracer, Status, StatusCode

from is_msgs.common_pb2 import FieldSelector
from is_msgs.camera_pb2 import CameraConfig, CameraConfigFields

from is_spinnaker_gateway.logger import Logger
from is_spinnaker_gateway.conf.options_pb2 import Camera
from is_spinnaker_gateway.driver.spinnaker.spinnaker import SpinnakerDriver


class CameraGateway:
    def __init__(self, logger: Logger, broker_uri: str, zipkin_uri: str, camera: Camera):
        self.logger = logger

        self.id = camera.id
        self.broker_uri = broker_uri
        self.zipkin_uri = zipkin_uri
        self.config_path = camera.initial_config
        self.driver = SpinnakerDriver(
            use_turbojpeg=camera.use_turbojpeg,
            color_algorithm=camera.algorithm,
            onboard_color_processing=camera.onboard_color_processing,
        )
        self.logger.set_critical_callback(callback=self.driver.close)
        self.driver.connect(ip=camera.ip)

        self.driver.set_packet_size(camera.packet_size)
        self.driver.set_packet_delay(camera.packet_delay)
        self.driver.set_packet_resend(camera.packet_resend)
        self.driver.set_packet_resend_timeout(camera.packet_resend_timeout)
        self.driver.set_packet_resend_max_requests(camera.packet_resend_max_requests)

        self.driver.set_reverse_x(reverse_x=camera.reverse_x)

    def load_json(self, path: str = "/etc/is-spinnaker-gateway/camera_0.json") -> CameraConfig:
        try:
            with open(path, 'r') as f:
                try:
                    op = Parse(f.read(), CameraConfig())
                    self.logger.info('CameraConfig: \n{}', op)
                    return op
                except Exception as ex:
                    self.logger.critical('Unable to load options from \'{}\'. \n{}', path, ex)
        except Exception:
            self.logger.critical('Unable to open file \'{}\'', path)

    @staticmethod
    def check_status_get(status: Status) -> bool:
        if (status.code == StatusCode.UNIMPLEMENTED) or (status.code == StatusCode.OK):
            return True
        else:
            return False

    @staticmethod
    def set_attribute(field: Any, value: Any, status: Status) -> None:
        if status.code == StatusCode.OK:
            field.CopyFrom(value)

    def get_config(self, field_selector: FieldSelector, ctx: Context) -> CameraConfig:
        fields = field_selector.fields
        if CameraConfigFields.Value("ALL") in fields:
            if CameraConfigFields.Value("IMAGE_SETTINGS") not in fields:
                fields.extend([CameraConfigFields.Value("IMAGE_SETTINGS")])
            if CameraConfigFields.Value("CAMERA_SETTINGS") not in fields:
                fields.extend([CameraConfigFields.Value("CAMERA_SETTINGS")])
            if CameraConfigFields.Value("SAMPLING_SETTINGS") not in fields:
                fields.extend([CameraConfigFields.Value("SAMPLING_SETTINGS")])
        config = CameraConfig()
        for field in fields:
            if field == CameraConfigFields.Value("IMAGE_SETTINGS"):
                status, value = self.driver.get_resolution()
                self.set_attribute(config.image.resolution, value, status)
                status, value = self.driver.get_color_space()
                self.set_attribute(config.image.color_space, value, status)
                status, value = self.driver.get_format()
                self.set_attribute(config.image.format, value, status)
                status, value = self.driver.get_region_of_interest()
                self.set_attribute(config.image.region, value, status)
            if field == CameraConfigFields.Value("SAMPLING_SETTINGS"):
                status, value = self.driver.get_sampling_rate()
                self.set_attribute(config.sampling.frequency, value, status)
                status, value = self.driver.get_delay()
                self.set_attribute(config.sampling.delay, value, status)
            if field == CameraConfigFields.Value("CAMERA_SETTINGS"):
                status, value = self.driver.get_brightness()
                self.set_attribute(config.camera.brightness, value, status)
                status, value = self.driver.get_exposure()
                self.set_attribute(config.camera.exposure, value, status)
                status, value = self.driver.get_focus()
                self.set_attribute(config.camera.focus, value, status)
                status, value = self.driver.get_gain()
                self.set_attribute(config.camera.gain, value, status)
                status, value = self.driver.get_gamma()
                self.set_attribute(config.camera.gamma, value, status)
                status, value = self.driver.get_hue()
                self.set_attribute(config.camera.hue, value, status)
                status, value = self.driver.get_iris()
                self.set_attribute(config.camera.iris, value, status)
                status, value = self.driver.get_saturation()
                self.set_attribute(config.camera.saturation, value, status)
                status, value = self.driver.get_sharpness()
                self.set_attribute(config.camera.sharpness, value, status)
                status, value = self.driver.get_shutter()
                self.set_attribute(config.camera.shutter, value, status)
                status, value = self.driver.get_white_balance_bu()
                self.set_attribute(config.camera.white_balance_bu, value, status)
                status, value = self.driver.get_white_balance_rv()
                self.set_attribute(config.camera.white_balance_rv, value, status)
                status, value = self.driver.get_zoom()
                self.set_attribute(config.camera.zoom, value, status)
        return config

    @staticmethod
    def check_status_set(obj: Any, field: str, status: Status) -> bool:
        if (status.code == StatusCode.OK) and (obj.HasField(field)):
            return True
        else:
            return False

    def set_config(self, config: CameraConfig, ctx: Context) -> Union[Empty, Status]:
        status = Status(code=StatusCode.OK)
        if config.HasField("image"):
            image = config.image
            if self.check_status_set(image, "resolution", status):
                status = self.driver.set_resolution(image.resolution)
            if self.check_status_set(image, "color_space", status):
                status = self.driver.set_color_space(image.color_space)
            if self.check_status_set(image, "format", status):
                status = self.driver.set_format(image.format)
            if self.check_status_set(image, "region", status):
                status = self.driver.set_region_of_interest(image.region)
        if self.check_status_set(config, "sampling", status):
            sampling = config.sampling
            if self.check_status_set(sampling, "frequency", status):
                status = self.driver.set_sampling_rate(sampling.frequency)
            if self.check_status_set(sampling, "delay", status):
                status = self.driver.set_delay(sampling.delay)
        if self.check_status_set(config, "camera", status):
            camera = config.camera
            if self.check_status_set(camera, "brightness", status):
                status = self.driver.set_brightness(camera.brightness)
            if self.check_status_set(camera, "exposure", status):
                status = self.driver.set_exposure(camera.exposure)
            if self.check_status_set(camera, "focus", status):
                status = self.driver.set_focus(camera.focus)
            if self.check_status_set(camera, "gain", status):
                status = self.driver.set_gain(camera.gain)
            if self.check_status_set(camera, "gamma", status):
                status = self.driver.set_gamma(camera.gamma)
            if self.check_status_set(camera, "hue", status):
                status = self.driver.set_hue(camera.hue)
            if self.check_status_set(camera, "iris", status):
                status = self.driver.set_iris(camera.iris)
            if self.check_status_set(camera, "saturation", status):
                status = self.driver.set_saturation(camera.saturation)
            if self.check_status_set(camera, "sharpness", status):
                status = self.driver.set_sharpness(camera.sharpness)
            if self.check_status_set(camera, "shutter", status):
                status = self.driver.set_shutter(camera.shutter)
            if self.check_status_set(camera, "white_balance_bu", status):
                status = self.driver.set_white_balance_bu(camera.white_balance_bu)
            if self.check_status_set(camera, "white_balance_rv", status):
                status = self.driver.set_white_balance_rv(camera.white_balance_rv)
            if self.check_status_set(camera, "zoom", status):
                status = self.driver.set_zoom(camera.zoom)
        if status.code == StatusCode.OK:
            return Empty()
        else:
            return status

    def get_zipkin(self, uri: str) -> Tuple[str, str]:
        zipkin_ok = re.match("http:\\/\\/([a-zA-Z0-9\\.]+)(:(\\d+))?", uri)
        if not zipkin_ok:
            self.logger.critical("Invalid zipkin uri {}, \
                                 expected http://<hostname>:<port>".format(uri))
        return zipkin_ok.group(1), int(zipkin_ok.group(3))

    @staticmethod
    def span_duration_ms(span: Span) -> float:
        dt = dp.parse(span.end_time) - dp.parse(span.start_time)
        return dt.total_seconds() * 1000.0

    def run(self) -> None:
        service_name = "CameraGateway"
        config = self.load_json(path=self.config_path)
        ok = self.set_config(config=config, ctx=None)
        if not isinstance(ok, Empty):
            self.logger.critical("Failed to set initial configuration.\n \
                                  Code={}, why={}".format(ok.code, ok.why))
        time.sleep(2)

        publish_channel = Channel(self.broker_uri)
        rpc_channel = Channel(self.broker_uri)

        zipkin_uri, zipkin_port = self.get_zipkin(uri=self.zipkin_uri)
        exporter = ZipkinExporter(
            service_name=service_name,
            host_name=zipkin_uri,
            port=zipkin_port,
            transport=AsyncTransport,
        )

        server = ServiceProvider(channel=rpc_channel)
        logging = LogInterceptor()
        tracing = TracingInterceptor(exporter=exporter)
        server.add_interceptor(interceptor=logging)
        server.add_interceptor(interceptor=tracing)
        server.delegate(
            topic="{}.{}.GetConfig".format(service_name, self.id),
            request_type=FieldSelector,
            reply_type=CameraConfig,
            function=self.get_config,
        )
        server.delegate(
            topic="{}.{}.SetConfig".format(service_name, self.id),
            request_type=CameraConfig,
            reply_type=Empty,
            function=self.set_config,
        )
        self.logger.info("RPC listening for requests")
        self.driver.start_capture()
        while True:
            image = self.driver.grab_image()
            if image is not None:
                tracer = Tracer(exporter=exporter)
                span = None
                with tracer.span(name="frame") as _span:
                    message = Message()
                    message.topic = "{}.{}.Frame".format(service_name, self.id)
                    message.pack(self.driver.to_image(image))
                    message.inject_tracing(_span)
                    span = _span
                    publish_channel.publish(message=message)
                took_ms = round(self.span_duration_ms(span), 2)
                self.logger.info("Publish image, took_ms={}".format(took_ms))
                try:
                    message = rpc_channel.consume(timeout=0)
                    if server.should_serve(message):
                        server.serve(message)
                except socket.timeout:
                    pass
