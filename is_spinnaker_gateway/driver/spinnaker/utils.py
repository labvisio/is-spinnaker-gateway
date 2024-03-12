import ipaddress
import re

import PySpin

from is_spinnaker_gateway.conf.options_pb2 import ColorProcessingAlgorithm as CPA

ALGORITHM_MAP = {
    CPA.Value("NEAREST_NEIGHBOR"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_NEAREST_NEIGHBOR,
    CPA.Value("NEAREST_NEIGHBOR_AVERAGE"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_NEAREST_NEIGHBOR_AVG,
    CPA.Value("EDGE_SENSING"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_EDGE_SENSING,
    CPA.Value("HQ_LINEAR"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR,
    CPA.Value("BILINEAR"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_BILINEAR,
    CPA.Value("DIRECTIONAL_FILTER"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_DIRECTIONAL_FILTER,
    CPA.Value("WEIGHTED_DIRECTIONAL_FILTER"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_WEIGHTED_DIRECTIONAL_FILTER,
    CPA.Value("RIGOROUS"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_RIGOROUS,
    CPA.Value("IPP"): PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_IPP,
}


def make_mac_address(integer_mac: int) -> str:
    return ":".join(re.findall("..", "%012x" % integer_mac))


def make_ip_address(integer_ip: int) -> str:
    return str(ipaddress.ip_address(integer_ip))


def make_subnet_mask(integer_mask: int) -> int:
    return integer_mask


def get_value(ratio: float, min_value: float, max_value: float) -> float:
    return (ratio * ((max_value - min_value))) + min_value


def get_ratio(value: float, min_value: float, max_value: float) -> float:
    return (value - min_value) / (max_value - min_value)
