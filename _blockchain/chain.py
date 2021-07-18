from __future__ import annotations
import typing
import copy
from dataclasses import dataclass, field
from datetime import datetime

from collections import deque

from .base import TupleComparable
from .errors import ChainValidationError
from .block import Block


@dataclass
class Chain(TupleComparable):

    blocks = field(default_factory=deque)  # Gonna fail!
    # blocks: typing.MutableSequence[typing.Any] = field(default_factory=deque)

    def __post_init__(self) -> None:
        self.add_genesis_block()

    def add_genesis_block(self) -> None:
        self.add_block(
            'Genesis',
            block_id=0,
            timestamp=datetime.utcnow(),
            previous_hash='arbitrary',
        )

    def add_block(
            self,
            data: typing.Any,
            /,
            block_id: typing.Optional[int] = None,
            timestamp: typing.Optional[datetime] = None,
            previous_hash: typing.Optional[str] = None
            ) -> None:

        _kwargs = {
            'block_id': block_id or len(self.blocks),
            'timestamp': timestamp or datetime.utcnow(),
            'data': data,
            'previous_hash': previous_hash or self.last_block.hash,
        }

        self.blocks.append(Block(**_kwargs))

    @property
    def size(self) -> int:
        '''
        Returns a full length of a block sequence
        '''
        return len(self.blocks)

    @property
    def chain_size(self) -> int:
        '''
        Returns full length minus genesis block
        '''
        # exclude genesis block
        return self.size - 1

    @property
    def last_block(self) -> Block:
        return self.blocks[self.chain_size] if self.blocks else None

    def verify(self, verbose: typing.Optional[bool] = True) -> bool:
        try:
            self._verify()
        except ChainValidationError as exc:
            if verbose:
                print(str(exc))
            return False
        return True

    def _verify(self) -> None:
        for block_id in range(1, self.size):
            _current = self.blocks[block_id]
            _prev = self.blocks[block_id - 1]
            # assume Genesis block integrity
            if not _current.verify():
                raise ChainValidationError(
                    f'Wrong data type(s) at block: {block_id!r}.'
                )
            if _current.block_id != block_id:
                raise ChainValidationError(
                    f'Wrong block block_id at block: {block_id!r}'
                )
            if _current.previous_hash != _prev.hash:
                raise ChainValidationError(
                    f'Wrong previous hash at block: {block_id!r}'
                )
            if _current.hash != _current.get_hash():
                raise ChainValidationError(
                    f'Wrong hash at block: {block_id!r}.'
                )
            if _current.timestamp <= _prev.timestamp:
                raise ChainValidationError(
                    f'Backdating at block: {block_id!r}.'
                )

    def fork(self, head: typing.Union[str, int] = 'latest') -> Chain:
        if head in ('latest', 'whole', 'all'):
            # deepcopy since they are mutable
            return copy.deepcopy(self)
        chain_copy: Chain = copy.deepcopy(self)
        chain_copy.blocks = chain_copy.blocks[:int(head) + 1]
        return chain_copy

    def get_root(self, other_chain: Chain) -> Chain:
        min_chain_size = min(self.chain_size, other_chain.chain_size)
        for seq in range(1, min_chain_size + 1):
            if self.blocks[seq] != other_chain.blocks[seq]:
                return self.fork(seq - 1)

        return self.fork(min_chain_size)
