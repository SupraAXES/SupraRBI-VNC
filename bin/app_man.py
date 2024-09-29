#!/usr/bin/env python3
import os
import asyncio
import docker
import logging
import json
import base64

_proj_net = os.environ.get('SUPRA_PROJECTOR_NETWORK')
_proj_image = os.environ.get('SUPRA_PROJECTOR_IMAGE')

assert _proj_net is not None, 'please set SUPRA_PROJECTOR_NETWORK'
assert _proj_image is not None, 'please set SUPRA_PROJECTOR_IMAGE'

logging.info(f'projector network: {_proj_net}')
logging.info(f'projector image name: {_proj_image}')


def _append_mnts(to_mnts, from_mnts):
    for x in from_mnts:
        if x != '': to_mnts.append(x)


def _run_rbi(name, url, idle_connection, idle_user, mounts, instance_settings):
    client = docker.from_env()
    vm_mnts = []
    vm_caps = []
    vm_envs = dict()
    vm_ports = dict()

    _append_mnts(vm_mnts, ['/etc/localtime:/etc/localtime:ro'])

    _append_mnts(vm_mnts, mounts)

    if instance_settings != {}:
        vm_envs['SUPRA_INSTANCE_SETTINGS'] = base64.b64encode(json.dumps(instance_settings).encode()).decode()

    vm_envs['SUPRA_APPS'] = 'supra-rbi'
    vm_envs['SUPRA_RBI_URL'] = url
    if idle_connection > 0:
        vm_envs['SET_IDLE_CONNECTION'] = idle_connection
    if idle_user > 0:
        vm_envs['SET_IDLETIME'] = idle_user
    vm_envs['SUPRA_IM_ON'] = 1
    vm_envs['SUPRA_AUDIO_ON'] = 1
    vm_envs['SET_X11VNC_SHARED'] = 1

    #vm_ports['5900/tcp'] = '5999'

    #print(f'mnts: {vm_mnts}')
    #print(f'caps: {vm_caps}')
    #print(f'envs: {vm_envs}')
    #print(f'ports: {vm_ports}')
    #assert 0, 'test for check args to docker-run'
    try:
        container = client.containers.run(
            detach=True,
            remove=True,
            init=True,
            tty=True,
            network=_proj_net,
            ports = vm_ports,
            volumes=vm_mnts,
            cap_add=vm_caps,
            environment=vm_envs,
            name=name,
            image=_proj_image
        )
    except Exception as e:
        logging.debug(f'{e}')
    finally:
        client.close()


def _stop_rbi(name):
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        container.stop()
    except Exception as e:
        logging.debug(f'{e}')
        pass
    finally:
        client.close()


async def run_rbi(name, url, idle_connection, idle_user, mounts, instance_settings):
    logging.info(f'rbi run: name: {name}, url: {url}')
    logging.debug(f'rbi run: idle_connection: {idle_connection}, idle_user: {idle_user}, mounts: {mounts}, instance_settings: {instance_settings}')
    await asyncio.to_thread(_run_rbi, name, url, idle_connection, idle_user, mounts, instance_settings)


async def stop_rbi(name):
    logging.info(f'rbi stop: {name}')
    await asyncio.to_thread(_stop_rbi, name)


if __name__ == "__main__":
    #asyncio.run(run_rbi('test-rbi', 'https://www.baidu.com/', 0, 0, '/home/tmp/', [...], {...}))
    pass
