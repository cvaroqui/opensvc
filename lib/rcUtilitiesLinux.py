import os
import re
from rcUtilities import call

def major(driver):
    path = os.path.join(os.path.sep, 'proc', 'devices')
    try:
        f = open(path)
    except:
        raise
    for line in f.readlines():
        words = line.split()
        if len(words) == 2 and words[1] == driver:
            f.close()
            return int(words[0])
    f.close()
    raise

def get_blockdev_sd_slaves(syspath):
    slaves = set()
    for s in os.listdir(syspath):
        if re.match('^sd[a-z]*', s) is not None:
            slaves.add('/dev/' + s)
            continue
        deeper = os.path.join(syspath, s, 'slaves')
        if os.path.isdir(deeper):
            slaves |= get_blockdev_sd_slaves(deeper)
    return slaves

def check_ping(addr, timeout=5, count=1):
    if ':' in addr:
        ping = 'ping6'
    else:
        ping = 'ping'
    cmd = [ping, '-c', repr(count),
                 '-W', repr(timeout),
                 '-w', repr(timeout),
                 addr]
    (ret, out) = call(cmd)
    if ret == 0:
        return True
    return False

