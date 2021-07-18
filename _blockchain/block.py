from __future__ import annotations
from dataclasses import dataclass, astuple
from datetime import datetime
import hashlib
import typing

from .base import TupleComparable


@dataclass
class Block(TupleComparable):

    block_id: int
    timestamp: datetime
    data: typing.Any
    previous_hash: str
    hash: typing.Optional[str] = None

    def __post_init__(self) -> None:
        self.hash = self.get_hash()

    @property
    def fields(self) -> typing.Tuple:
        return (self.block_id, self.timestamp, self.previous_hash, self.hash)

    def get_hash(self) -> str:
        key = hashlib.sha256()
        for val in self.fields[:-1]:
            key.update(str(val).encode('utf-8'))

        return key.hexdigest()

    def verify(self) -> bool:
        '''
        Checks data types of all info in a block.
        '''
        for obj, _t in zip(self.fields, (int, datetime, str, str)):
            if not isinstance(obj, _t):
                return False
        return True
