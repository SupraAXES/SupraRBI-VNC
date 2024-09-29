#!/usr/bin/env python3
import asyncio
from asyncio.streams import StreamReader, StreamWriter
import ssl
import logging
import json
import uuid
import random
import os
import traceback

#set log level
log_level = os.environ.get('LOG_LEVEL')
if log_level == 'debug':
    logging.basicConfig(level=logging.DEBUG)
elif log_level == 'info':
    logging.basicConfig(level=logging.INFO)
elif log_level == 'warning':
    logging.basicConfig(level=logging.WARNING)
elif log_level == 'error':
    logging.basicConfig(level=logging.ERROR)
elif log_level == 'critical':
    logging.basicConfig(level=logging.CRITICAL)
else:
    log_level = 'info'
    logging.basicConfig(level=logging.INFO)
print(f'vncd log level: {log_level}')

import app_man
import none_client

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='/supra/cert/server.crt', keyfile='/supra/cert/server.key')
context.set_ciphers('ALL:@SECLEVEL=0')

RFB_VER = b'RFB 003.008\n'
RFB_AUTH_LIST = b'\x01\x13'
RFB_AUTH_VENCRYPT = b'\x13'
RFB_AUTH_VER = b'\x00\x02'
RFB_AUTH_VER_OK = b'\x00'
RFB_AUTH_SUBLIST = b'\x01\x00\x00\x01\x03'
RFB_AUTH_TLSPLAIN = b'\x00\x00\x01\x03'
RFB_AUTH_SUB_OK = b'\x01'
RFB_AUTH_OK = b'\x00\x00\x00\x00'


def _check_name(norm_name):
    chars_allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    if not all(char in chars_allowed for char in norm_name):
        raise Exception(f'malformed name: {norm_name}')


MISC_CONF_DEFAULT = {
    'id': {  # user provide composite id. except for anon type, make sure it is unique
        'name': '',
        'type': 'anon'  # anon/norm
    },
    'idle_connection': 0,  # ms >= 0 extra wait time
    'idle_user': 0,  # ms >=0, 0 means dont check idle

    'mounts': [''],  # string-list for generic mount string: host-source:container-target:rw

    'instance-settings': {},
}


def _norm_misc_conf(misc_conf):
    uid = misc_conf['id']

    if uid['type'] == 'anon':
        uid['name'] = ''
        uid['idle_connection'] = 0
    _check_name(uid['name'])

    assert misc_conf['instance-settings'] is not None, 'dont assign none to instance-settings'

    assert misc_conf['idle_connection'] >= 0, 'idle_connection should >= 0'
    assert misc_conf['idle_user'] >= 0, 'idle_user should >= 0'


g_cnt = random.randint(0, 65536)


def _gen_rbi_id(uid):
    idn = uid['name']
    idt = uid['type']
    suffix = ''
    assert idt in ['anon', 'norm']
    if idt == 'anon':
        global g_cnt
        g_cnt += 1
        suffix = f'{uuid.uuid4()}{g_cnt}'
    return f'rbi-{idt}-{idn}{suffix}'


async def _relay(reader: StreamReader, writer: StreamWriter):
    while True:
        bs = await reader.read(4096)
        if bs == b'':
            reader.feed_eof()
            if writer.can_write_eof():
                writer.write_eof()
            raise Exception('link down')
        else:
            writer.write(bs)
            await writer.drain()


async def _check_pulseaudio(target):
    while True:
        try:
            await asyncio.open_connection(target, 4713)  # pulseaudio
            logging.debug(f'pulseaudio checked')
            return
        except Exception:  # dont wait in case of system exception
            await asyncio.sleep(0.5)


async def _check_point(target):
    async with asyncio.timeout(30):
        await _check_pulseaudio(target)


async def handler(reader: StreamReader, writer: StreamWriter):
    try:
        writer.write(RFB_VER)
        await writer.drain()

        c_ver = await reader.readexactly(12)
        assert c_ver == RFB_VER

        writer.write(RFB_AUTH_LIST)
        await writer.drain()

        c_auth = await reader.readexactly(1)
        assert c_auth == RFB_AUTH_VENCRYPT

        writer.write(RFB_AUTH_VER)
        await writer.drain()

        c_ver = await reader.readexactly(2)
        assert(c_ver == RFB_AUTH_VER)

        writer.write(RFB_AUTH_VER_OK)
        await writer.drain()

        writer.write(RFB_AUTH_SUBLIST)
        await writer.drain()

        c_sub = await reader.readexactly(4)
        assert(c_sub == RFB_AUTH_TLSPLAIN)

        writer.write(RFB_AUTH_SUB_OK)
        await writer.drain()

        await writer.start_tls(context)
        c_name_len = int.from_bytes(await reader.readexactly(4), 'big')
        c_passwd_len = int.from_bytes(await reader.readexactly(4), 'big')
        c_name = (await reader.readexactly(c_name_len)).decode('utf-8')
        c_passwd = (await reader.readexactly(c_passwd_len)).decode('utf-8')

        url = c_name
        misc_conf = {**MISC_CONF_DEFAULT} if c_passwd == '' else {**MISC_CONF_DEFAULT, **json.loads(c_passwd)}
        _norm_misc_conf(misc_conf)
        rbi_id = _gen_rbi_id(misc_conf['id'])

        await app_man.run_rbi(rbi_id, url, misc_conf['idle_connection'], misc_conf['idle_user'],
                              misc_conf['mounts'], misc_conf['instance-settings'])

        back_reader, back_writer = await none_client.handshake(rbi_id)
        await _check_point(rbi_id)

        writer.write(RFB_AUTH_OK)
        await writer.drain()

        logging.info(f'relay begin')
        try:
            await asyncio.gather(_relay(reader, back_writer), _relay(back_reader, writer))
        finally:
            back_writer.close()
            await back_writer.wait_closed()
            logging.info(f'relay stop')

    except Exception as e:
        logging.debug(f'{traceback.format_exc()}')
    finally:
        writer.close()
        await writer.wait_closed()


async def run_server():
    server = await asyncio.start_server(handler, '0.0.0.0', 5900)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
