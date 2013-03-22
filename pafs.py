#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import subprocess
from collections import defaultdict


MAX_VOLUME = 2 ** 16


def volume_percent(hex_value):
    return (int(hex_value, 16) / MAX_VOLUME) * 100


def volume_hex(percent):
    return hex(int((percent / 100) * MAX_VOLUME))


def pa_info():
    p = subprocess.Popen('pacmd dump'.split(), stdout=subprocess.PIPE)
    out, _ = p.communicate()
    relevant = [line.split() for line in out.splitlines()
                if line.startswith('set-')]
    relevant = [x + [None] if len(x) == 2 else x
                for x in relevant]
    info = defaultdict(dict)
    for cmd, device, value in relevant:
        if 'sink' in cmd:
            info[device]['type'] = 'sink'
        if 'source' in cmd:
            info[device]['type'] = 'source'
        if 'volume' in cmd:
            info[device]['volume'] = volume_percent(value)
        if 'mute' in cmd:
            info[device]['muted'] = value
        if 'default' in cmd:
            info[device]['default'] = True
    for dev in info:
        info[dev].setdefault('default', False)

    return info


def default_streams():
    info = pa_info()
    for dev, prop in info.iteritems():
        if prop['default']:
            if prop['type'] == 'sink':
                default_sink = dev, prop
            if prop['type'] == 'source':
                default_source = dev, prop

    return default_source, default_sink


def mute(stream):
    name, props = stream
    cmd = 'set-%s-mute' % props['type']
    if props['muted'] == 'yes':
        value = 'no'
    else:
        value = 'yes'
    subprocess.call(['pactl', cmd, name, value])


def change_volume(stream, change):
    name, props = stream
    cmd = 'set-%s-volume' % props['type']
    volume = props['volume'] + change
    subprocess.call(['pactl', cmd, name, volume_hex(volume)])


def print_info(info):
    pass


if __name__ == '__main__':
    def usage():
        print """\
Pulse audio default stream manipulation

Commands:
info                  -- show information about default streams
up [percentage]       -- increase by percentage
down [percentage]     -- decrease by percentage
mute                  -- toggle mute of stream
in-up [percentage]    -- increase by percentage
in-down [percentage]  -- decrease by percentage
in-mute               -- toggle mute of stream
"""
    import sys
    cmd = sys.argv[1]
    args = sys.argv[2:]

    source, sink = default_streams()

    if cmd in ('up', 'down', 'in-up', 'in-down'):
        volume = float(args[0])
    if cmd in ('down', 'in-down'):
        volume = - volume
    if cmd in ('up', 'down', 'mute'):
        stream = sink
    if cmd in ('in-up', 'in-down', 'in-mute'):
        stream = souce
    if cmd in ('up', 'down', 'in-up', 'in-down'):
        change_volume(stream, volume)
    elif cmd in ('mute', 'in-mute'):
        mute(stream)
    elif cmd == 'info':
        print_info()
    else:
        usage()
