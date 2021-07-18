import abc
import typing
from dataclasses import astuple


class Comparable(abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    def __eq__(self, other: typing.Any) -> bool: ...


class DictComparable(Comparable):
    __slots__ = ()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return False


class TupleComparable(Comparable):
    __slots__ = ()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, type(self)):
            return astuple(self) == astuple(other)
        return False
