import hashlib
from unittest import mock

from datetime import datetime, timedelta
from _blockchain.chain import Chain


def test_chain():
    '''
    Initial functional testing of chain and blocks verification.
    '''

    chain = Chain()

    fixed_dt = datetime.utcnow()

    data: str = 'This is block {} of my first chain.'

    with mock.patch('_blockchain.chain.datetime') as mock_dt:

        mock_dt.utcnow.return_value = fixed_dt

        for num in range(1, 21):

            chain.add_block(data.format(num))
            mock_dt.utcnow.return_value += timedelta(seconds=1)

    assert chain.blocks[3].timestamp == fixed_dt + timedelta(seconds=2)
    assert chain.blocks[7].data == data.format(7)

    ninth_hash = hashlib.sha256()

    for val in chain.blocks[9].fields[:-1]:
        ninth_hash.update(str(val).encode('utf-8'))

    assert chain.blocks[9].hash == ninth_hash.hexdigest()

    assert chain.chain_size == 20
    assert chain.verify(verbose=False)

    c_forked = chain.fork('latest')
    assert chain == c_forked

    c_forked.add_block('New block for forked chain!')
    assert chain.chain_size == 20
    assert c_forked.chain_size == 21

    c_forked = chain.fork('latest')
    c_forked.blocks[9].block_id = -9
    assert not c_forked.verify(verbose=False)

    c_forked = chain.fork('latest')
    c_forked.blocks[16].timestamp = datetime(2000, 1, 1, 0, 0, 0, 0)
    assert not c_forked.verify(verbose=False)

    c_forked = chain.fork('latest')
    c_forked.blocks[5].previous_hash = c_forked.blocks[1].hash
    assert not c_forked.verify(verbose=False)
