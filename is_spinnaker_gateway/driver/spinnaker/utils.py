from typing import Tuple
from is_wire.core import StatusCode
from PySpin import (
    INode,
    INodeMap,
    IsReadable,
    IsWritable,
    IsAvailable,
    CFloatPtr,
    CStringPtr,
    CBooleanPtr,
    CIntegerPtr,
    CEnumerationPtr,
    SpinnakerException,
)

from is_spinnaker_gateway.exceptions import StatusException


def is_readable(node: INode):
    if not IsAvailable(node):
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Property '{node.GetName()}' not available.",
        )
    if not IsReadable(node):
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Property '{node.GetName()}' not readable.",
        )


def is_writible(node: INode):
    if not IsAvailable(node):
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Property '{node.GetName()}' not available.",
        )
    if not IsWritable(node):
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Property '{node.GetName()}' not writable.",
        )


def get_op_bool(node_map: INodeMap, name: str) -> bool:
    node = CBooleanPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return node.GetValue()
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def set_op_bool(node_map: INodeMap, name: str, value: bool):
    node = CBooleanPtr(node_map.GetNode(name))
    is_writible(node)
    try:
        node.SetValue(value)
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to set property '{name}' to '{value}'",
        ) from ex


def get_op_int(node_map: INodeMap, name: str) -> int:
    node = CIntegerPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return node.GetValue()
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def set_op_int(node_map: INodeMap, name: str, value: int):
    node = CIntegerPtr(node_map.GetNode(name))
    is_writible(node)
    min_value = node.GetMin()
    max_value = node.GetMax()
    if (value < min_value) or (value > max_value):
        raise StatusException(
            code=StatusCode.FAILED_PRECONDITION,
            message=f"Property '{name}' must be in interval [{min_value}, {max_value}]",
        )
    else:
        try:
            node.SetValue(value)
        except SpinnakerException as ex:
            raise StatusException(
                code=StatusCode.INTERNAL_ERROR,
                message=f"Failed to set property '{name}' to '{value}'",
            ) from ex


def get_op_float(node_map: INodeMap, name: str) -> float:
    node = CFloatPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return node.GetValue()
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def set_op_float(node_map: INodeMap, name: str, value: float):
    node = CFloatPtr(node_map.GetNode(name))
    is_writible(node)
    min_value = node.GetMin()
    max_value = node.GetMax()
    if (value < min_value) or (value > max_value):
        raise StatusException(
            code=StatusCode.FAILED_PRECONDITION,
            message=f"'Property '{name}' must be in interval [{min_value}, {max_value}]",
        )
    else:
        try:
            node.SetValue(value)
        except SpinnakerException as ex:
            raise StatusException(
                code=StatusCode.INTERNAL_ERROR,
                message=f"Failed to set property '{name}' to '{value}'",
            ) from ex


def get_op_str(node_map: INodeMap, name: str) -> str:
    node = CStringPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return node.GetValue()
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def set_op_enum(node_map: INodeMap, name: str, value: str):
    node = CEnumerationPtr(node_map.GetNode(name))
    is_writible(node)
    try:
        node_value = node.GetEntryByName(value)
        node.SetIntValue(node_value.GetValue())
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to set property '{name}' to '{value}'",
        ) from ex


def get_op_enum(node_map: INodeMap, name: str) -> str:
    node = CEnumerationPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return node.GetCurrentEntry().GetSymbolic()
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def minmax_op_float(node_map: INodeMap, name: str) -> Tuple[float, float]:
    node = CFloatPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return (node.GetMin(), node.GetMax())
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def minmax_op_int(node_map: INodeMap, name: str) -> Tuple[int, int]:
    node = CIntegerPtr(node_map.GetNode(name))
    is_readable(node)
    try:
        return (node.GetMin(), node.GetMax())
    except SpinnakerException as ex:
        raise StatusException(
            code=StatusCode.INTERNAL_ERROR,
            message=f"Failed to get property '{name}'",
        ) from ex


def get_value(ratio: float, min_value: float, max_value: float):
    return (ratio * ((max_value - min_value))) + min_value


def get_ratio(value: float, min_value: float, max_value: float):
    return (value - min_value) / (max_value - min_value)
