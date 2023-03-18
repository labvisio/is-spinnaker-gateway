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
)


def is_readable(node: INode) -> bool:
    return IsReadable(node) and IsAvailable(node)


def is_writible(node: INode) -> bool:
    return IsWritable(node) and IsAvailable(node)


def get_op_bool(node_map: INodeMap, name: str) -> Tuple[StatusCode, bool]:
    node = CBooleanPtr(node_map.GetNode(name))
    if is_readable(node):
        return StatusCode.OK, node.GetValue()
    else:
        return StatusCode.INTERNAL_ERROR, False


def set_op_bool(node_map: INodeMap, name: str, value: bool) -> StatusCode:
    node = CBooleanPtr(node_map.GetNode(name))
    if is_writible(node):
        node.SetValue(value)
        return StatusCode.OK
    else:
        return StatusCode.INTERNAL_ERROR


def get_op_int(node_map: INodeMap, name: str) -> Tuple[StatusCode, int]:
    node = CIntegerPtr(node_map.GetNode(name))
    if is_readable(node):
        return StatusCode.OK, node.GetValue()
    else:
        return StatusCode.INTERNAL_ERROR, 0


def set_op_int(node_map: INodeMap, name: str, value: int) -> StatusCode:
    node = CIntegerPtr(node_map.GetNode(name))
    if is_writible(node):
        min_value = node.GetMin()
        max_value = node.GetMax()
        if (value < min_value) or (value > max_value):
            return StatusCode.FAILED_PRECONDITION
        else:
            node.SetValue(value)
            return StatusCode.OK
    else:
        return StatusCode.INTERNAL_ERROR


def get_op_float(node_map: INodeMap, name: str) -> Tuple[StatusCode, float]:
    node = CFloatPtr(node_map.GetNode(name))
    if is_readable(node):
        return StatusCode.OK, node.GetValue()
    else:
        return StatusCode.INTERNAL_ERROR, 0.0


def set_op_float(node_map: INodeMap, name: str, value: float) -> StatusCode:
    node = CFloatPtr(node_map.GetNode(name))
    if is_writible(node):
        min_value = node.GetMin()
        max_value = node.GetMax()
        if (value < min_value) or (value > max_value):
            return StatusCode.FAILED_PRECONDITION
        else:
            node.SetValue(value)
            return StatusCode.OK
    else:
        return StatusCode.INTERNAL_ERROR


def get_op_str(node_map: INodeMap, name: str) -> Tuple[StatusCode, str]:
    node = CStringPtr(node_map.GetNode(name))
    if is_readable(node):
        return StatusCode.OK, node.GetValue()
    else:
        return StatusCode.INTERNAL_ERROR, ""


def set_op_enum(node_map: INodeMap, name: str, value: str) -> StatusCode:
    node = CEnumerationPtr(node_map.GetNode(name))
    if is_writible(node):
        node_value = node.GetEntryByName(value)
        node.SetIntValue(node_value.GetValue())
        return StatusCode.OK
    else:
        return StatusCode.INTERNAL_ERROR


def get_op_enum(node_map: INodeMap, name: str) -> Tuple[StatusCode, str]:
    node = CEnumerationPtr(node_map.GetNode(name))
    if is_readable(node):
        return StatusCode.OK, node.GetCurrentEntry().GetSymbolic()
    else:
        return StatusCode.INTERNAL_ERROR, ""


def minmax_op_float(node_map: INodeMap, name: str) -> Tuple[StatusCode, Tuple[float, float]]:
    node = CFloatPtr(node_map.GetNode(name))
    if is_readable(node):
        return StatusCode.OK, (node.GetMin(), node.GetMax())
    else:
        return StatusCode.INTERNAL_ERROR, (0, 0)
