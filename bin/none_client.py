#!/usr/bin/env python3
import asyncio
import socket
import logging

RFB_VER = b'RFB 003.008\n'
RFB_AUTH_NONE = b'\x01'
RFB_AUTH_OK = b'\x00\x00\x00\x00'


async def _try_connect(target):
    while True:
        try:
            reader, writer = await asyncio.open_connection(target, 5900)
            return reader, writer
        except:
            await asyncio.sleep(0.5)


async def handshake(target):
    logging.info(f'{target}: handshake begin')
    async with asyncio.timeout(30):
        reader, writer = await _try_connect(target)

    s_ver = await reader.readexactly(12)
    assert s_ver == RFB_VER

    writer.write(RFB_VER)
    await writer.drain()

    s_n = int.from_bytes(await reader.readexactly(1), 'big')
    assert 0 < s_n

    s_list = await reader.readexactly(s_n)

    writer.write(RFB_AUTH_NONE)
    await writer.drain()

    s_ok = await reader.readexactly(4)
    assert s_ok == RFB_AUTH_OK
    logging.info(f'{target}: handshake done')

    return reader, writer


if __name__ == '__main__':
    asyncio.run(handshake('test-rbi'))
