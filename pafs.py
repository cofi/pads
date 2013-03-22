from __future__ import division

import subprocess
from collections import defaultdict


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
