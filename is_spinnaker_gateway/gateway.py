import re
import socket
import time
from typing import Any, Tuple, Union

from dateutil import parser as dp
from google.protobuf.empty_pb2 import Empty
from is_msgs.camera_pb2 import CameraConfig, CameraConfigFields
from is_msgs.common_pb2 import FieldSelector
from is_wire.core import AsyncTransport, Channel, Message, Status, Tracer
from is_wire.rpc import LogInterceptor, ServiceProvider, TracingInterceptor
from is_wire.rpc.context import Context
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from opencensus.trace.span import Span

from is_spinnaker_gateway.conf.options_pb2 import Camera
from is_spinnaker_gateway.driver.spinnaker.spinnaker import SpinnakerDriver
from is_spinnaker_gateway.exceptions import StatusException
from is_spinnaker_gateway.logger import Logger


class CameraGateway:

    def __init__(
        self,
        logger: Logger,
        broker_uri: str,
        zipkin_uri: str,
        enable_tracing: bool,
        camera: Camera,
    ) -> None:
        self.logger = logger
        self.camera = camera
        self.broker_uri = broker_uri
        self.zipkin_uri = zipkin_uri
        self.enable_tracing = enable_tracing
        self.config = self.camera.initial_config
        self.driver = SpinnakerDriver(
            compression_level=0.8,
            use_turbojpeg=self.camera.use_turbojpeg,
            color_algorithm=self.camera.algorithm,
            onboard_color_processing=self.camera.onboard_color_processing,
        )
        self.restart_period = self.camera.restart_period
        self.driver.connect(ip=self.camera.ip)

        self.driver.set_reverse_x(reverse_x=self.camera.reverse_x)
        self.driver.set_packet_size(self.camera.packet_size)
        self.driver.set_packet_delay(self.camera.packet_delay)
        self.driver.set_packet_resend(self.camera.packet_resend)
        self.driver.set_packet_resend_timeout(self.camera.packet_resend_timeout)
        self.driver.set_packet_resend_max_requests(self.camera.packet_resend_max_requests)

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
                try:
                    value = self.driver.get_resolution()
                    config.image.resolution.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_color_space()
                    config.image.color_space.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_format()
                    config.image.format.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_region_of_interest()
                    config.image.region.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
            if field == CameraConfigFields.Value("SAMPLING_SETTINGS"):
                try:
                    value = self.driver.get_sampling_rate()
                    config.sampling.frequency.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_delay()
                    config.sampling.delay.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
            if field == CameraConfigFields.Value("CAMERA_SETTINGS"):
                try:
                    value = self.driver.get_brightness()
                    config.camera.brightness.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_exposure()
                    config.camera.exposure.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_focus()
                    config.camera.focus.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_gain()
                    config.camera.gain.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_gamma()
                    config.camera.gamma.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_hue()
                    config.camera.hue.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_iris()
                    config.camera.iris.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_saturation()
                    config.camera.saturation.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_sharpness()
                    config.camera.sharpness.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_shutter()
                    config.camera.shutter.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_white_balance_bu()
                    config.camera.white_balance_bu.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_white_balance_rv()
                    config.camera.white_balance_rv.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
                try:
                    value = self.driver.get_zoom()
                    config.camera.white_balance_rv.CopyFrom(value)
                except (StatusException, TypeError):
                    pass
        return config

    def set_config(self, config: CameraConfig, ctx: Context) -> Union[Empty, Status]:
        try:
            if config.HasField("image"):
                image = config.image
                if image.HasField("resolution"):
                    self.driver.set_resolution(image.resolution)
                if image.HasField("color_space"):
                    self.driver.set_color_space(image.color_space)
                if image.HasField("format"):
                    self.driver.set_format(image.format)
                if image.HasField("region"):
                    self.driver.set_region_of_interest(image.region)
            if config.HasField("sampling"):
                sampling = config.sampling
                if sampling.HasField("frequency"):
                    self.driver.set_sampling_rate(sampling.frequency)
                if sampling.HasField("delay"):
                    self.driver.set_delay(sampling.delay)
            if config.HasField("camera"):
                camera = config.camera
                if camera.HasField("brightness"):
                    self.driver.set_brightness(camera.brightness)
                if camera.HasField("exposure"):
                    self.driver.set_exposure(camera.exposure)
                if camera.HasField("focus"):
                    self.driver.set_focus(camera.focus)
                if camera.HasField("gain"):
                    self.driver.set_gain(camera.gain)
                if camera.HasField("gamma"):
                    self.driver.set_gamma(camera.gamma)
                if camera.HasField("hue"):
                    self.driver.set_hue(camera.hue)
                if camera.HasField("iris"):
                    self.driver.set_iris(camera.iris)
                if camera.HasField("saturation"):
                    self.driver.set_saturation(camera.saturation)
                if camera.HasField("sharpness"):
                    self.driver.set_sharpness(camera.sharpness)
                if camera.HasField("shutter"):
                    self.driver.set_shutter(camera.shutter)
                if camera.HasField("white_balance_bu"):
                    self.driver.set_white_balance_bu(camera.white_balance_bu)
                if camera.HasField("white_balance_rv"):
                    self.driver.set_white_balance_rv(camera.white_balance_rv)
                if camera.HasField("zoom"):
                    self.driver.set_zoom(camera.zoom)
            return Empty()
        except StatusException as ex:
            return ex.status

    def restart(self) -> None:
        # get current configuration
        selector = FieldSelector(fields=[CameraConfigFields.Value("ALL")])
        config = self.get_config(field_selector=selector, ctx=None)
        # stop and restart driver
        self.driver.stop_capture()
        self.driver.close()
        del self.driver
        self.driver = SpinnakerDriver(
            compression_level=0.8,
            use_turbojpeg=self.camera.use_turbojpeg,
            color_algorithm=self.camera.algorithm,
            onboard_color_processing=self.camera.onboard_color_processing,
        )
        self.driver.connect(ip=self.camera.ip)
        self.driver.set_reverse_x(reverse_x=self.camera.reverse_x)
        self.driver.set_packet_size(self.camera.packet_size)
        self.driver.set_packet_delay(self.camera.packet_delay)
        self.driver.set_packet_resend(self.camera.packet_resend)
        self.driver.set_packet_resend_timeout(self.camera.packet_resend_timeout)
        self.driver.set_packet_resend_max_requests(self.camera.packet_resend_max_requests)
        # apply last configuration
        maybe_ok = self.set_config(config=config, ctx=None)
        if isinstance(maybe_ok, Status):
            self.logger.critical(
                "Failed to set previous configuration.\nCode={}, why={}",
                maybe_ok.code,
                maybe_ok.why,
            )
        self.driver.start_capture()

    def get_zipkin(  # type: ignore[return]
        self,
        uri: str,
    ) -> Tuple[Union[str, Any], Union[str, Any]]:
        zipkin_ok = re.match("http:\\/\\/([a-zA-Z0-9\\.]+)(:(\\d+))?", uri)
        if not zipkin_ok:
            self.logger.critical("Invalid zipkin uri {}, expected http://<hostname>:<port>", uri)
        else:
            return zipkin_ok.group(1), int(zipkin_ok.group(3))

    @staticmethod
    def span_duration_ms(span: Span) -> float:
        dt = dp.parse(span.end_time) - dp.parse(span.start_time)
        return dt.total_seconds() * 1000.0

    def run(self) -> None:
        service_name = "CameraGateway"
        maybe_ok = self.set_config(config=self.config, ctx=None)
        if isinstance(maybe_ok, Status):
            self.logger.critical(
                "Failed to set initial configuration.\nCode={}, why={}",
                maybe_ok.code,
                maybe_ok.why,
            )
        time.sleep(2)

        publish_channel = Channel(self.broker_uri)
        rpc_channel = Channel(self.broker_uri)

        server = ServiceProvider(channel=rpc_channel)
        logging = LogInterceptor()
        logging.log.logger.propagate = False
        server.add_interceptor(interceptor=logging)
        server.delegate(
            topic=f"{service_name}.{self.camera.id}.GetConfig",
            request_type=FieldSelector,
            reply_type=CameraConfig,
            function=self.get_config,
        )
        server.delegate(
            topic=f"{service_name}.{self.camera.id}.SetConfig",
            request_type=CameraConfig,
            reply_type=Empty,
            function=self.set_config,
        )
        if self.enable_tracing:
            zipkin_uri, zipkin_port = self.get_zipkin(uri=self.zipkin_uri)
            exporter = ZipkinExporter(
                service_name=service_name,
                host_name=zipkin_uri,
                port=int(zipkin_port),
                transport=AsyncTransport,
            )
            tracing = TracingInterceptor(exporter=exporter)
            server.add_interceptor(interceptor=tracing)
        self.logger.info("RPC listening for requests")
        self.driver.start_capture()

        timeout = time.perf_counter() + self.camera.restart_period
        while True:
            now = time.perf_counter()
            if now >= timeout:
                self.logger.info("Restarting...")
                self.restart()
                timeout = time.perf_counter() + self.camera.restart_period
            image = self.driver.grab_image()
            if image is not None:
                if self.enable_tracing:
                    tracer = Tracer(exporter=exporter)
                    span = None
                    with tracer.span(name="frame") as _span:
                        message = Message()
                        message.topic = f"{service_name}.{self.camera.id}.Frame"
                        message.pack(self.driver.to_image(image))
                        message.inject_tracing(_span)
                        span = _span
                        publish_channel.publish(message=message)
                    took_ms = round(self.span_duration_ms(span), 2)
                    self.logger.info("Publish image, took_ms={}", took_ms)
                else:
                    ti = time.perf_counter()
                    message = Message()
                    message.topic = f"{service_name}.{self.camera.id}.Frame"
                    message.pack(self.driver.to_image(image))
                    publish_channel.publish(message=message)
                    took_ms = (time.perf_counter() - ti) * 1000
                    self.logger.info("Publish image, took_ms={}", took_ms)
                try:
                    message = rpc_channel.consume(timeout=0)
                    if server.should_serve(message):
                        server.serve(message)
                except socket.timeout:
                    pass
