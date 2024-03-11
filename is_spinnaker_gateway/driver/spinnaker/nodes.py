import functools
from typing import Tuple, TypeVar, ParamSpec, Callable

from is_wire.core import StatusCode
from PySpin import (
    CBooleanPtr,
    CEnumerationPtr,
    CFloatPtr,
    CIntegerPtr,
    CStringPtr,
    INodeMap,
    SpinnakerException,
)

from is_spinnaker_gateway.exceptions import StatusException

R = TypeVar("R")
P = ParamSpec("P")


def get_status(func: Callable[P, R]) -> Callable[P, R]:

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except SpinnakerException as ex:
            msg = f"Failed to set property '{kwargs['name']}'"
            raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg) from ex

    return wrapper


def set_status(func: Callable[P, R]) -> Callable[P, R]:

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except SpinnakerException as ex:
            msg = f"Failed to set property '{kwargs['name']}' with to '{kwargs['value']}'"
            raise StatusException(code=StatusCode.INTERNAL_ERROR, message=msg) from ex

    return wrapper


@get_status
def get_op_bool(node_map: INodeMap, name: str) -> bool:
    node = CBooleanPtr(node_map.GetNode(name))
    return node.GetValue()


@set_status
def set_op_bool(node_map: INodeMap, name: str, value: bool) -> None:
    node = CBooleanPtr(node_map.GetNode(name))
    node.SetValue(value)


@get_status
def get_op_int(node_map: INodeMap, name: str) -> int:
    node = CIntegerPtr(node_map.GetNode(name))
    return node.GetValue()


@set_status
def set_op_int(node_map: INodeMap, name: str, value: int) -> None:
    node = CIntegerPtr(node_map.GetNode(name))
    min_value = node.GetMin()
    max_value = node.GetMax()
    if (value < min_value) or (value > max_value):
        why = f"Property '{name}' must be in interval [{min_value}, {max_value}]"
        raise StatusException(code=StatusCode.FAILED_PRECONDITION, message=why)
    node.SetValue(value)


@get_status
def get_op_float(node_map: INodeMap, name: str) -> float:
    node = CFloatPtr(node_map.GetNode(name))
    return node.GetValue()


@set_status
def set_op_float(node_map: INodeMap, name: str, value: float) -> None:
    node = CFloatPtr(node_map.GetNode(name))
    min_value = node.GetMin()
    max_value = node.GetMax()
    if (value < min_value) or (value > max_value):
        why = f"Property '{name}' must be in interval [{min_value}, {max_value}]"
        raise StatusException(code=StatusCode.FAILED_PRECONDITION, message=why)
    node.SetValue(value)


@get_status
def get_op_str(node_map: INodeMap, name: str) -> str:
    node = CStringPtr(node_map.GetNode(name))
    return node.GetValue()


@set_status
def set_op_enum(node_map: INodeMap, name: str, value: str) -> None:
    node = CEnumerationPtr(node_map.GetNode(name))
    node_value = node.GetEntryByName(value)
    node.SetIntValue(node_value.GetValue())


@get_status
def get_op_enum(node_map: INodeMap, name: str) -> str:
    node = CEnumerationPtr(node_map.GetNode(name))
    return node.GetCurrentEntry().GetSymbolic()


@get_status
def minmax_op_float(node_map: INodeMap, name: str) -> Tuple[float, float]:
    node = CFloatPtr(node_map.GetNode(name))
    return node.GetMin(), node.GetMax()


@get_status
def minmax_op_int(node_map: INodeMap, name: str) -> Tuple[int, int]:
    node = CIntegerPtr(node_map.GetNode(name))
    return node.GetMin(), node.GetMax()
