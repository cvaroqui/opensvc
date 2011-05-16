#
# Copyright (c) 2010 Christophe Varoqui <christophe.varoqui@opensvc.com>'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import os
import datetime
from rcUtilities import call, which
from rcGlobalEnv import rcEnv

today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)

def sarfile(day):
    f = os.path.join(os.sep, 'var', 'adm', 'sa', 'sa'+day)
    if os.path.exists(f):
        return f
    return None

def twodays(fn):
    if which('sar') is None:
        return []
    lines = fn(yesterday)
    lines += fn(today)
    return lines

def stats_cpu():
    return twodays(stats_cpu_day)

def stats_cpu_day(t):
    d = t.strftime("%Y-%m-%d")
    day = t.strftime("%d")
    f = sarfile(day)
    if f is None:
        return []
    cmd = ['sar', '-u', '-P', 'ALL', '-f', f]
    (ret, buff, err) = call(cmd, errlog=False)
    lines = []
    for line in buff.split('\n'):
        l = line.split()
        if len(l) != 6:
            continue
        if l[1] == '%usr':
            continue
        if l[0] == 'Average':
            continue
        # SunOS:  date    %usr     %sys %wio                       %idle
        # xmlrpc: date cpu usr nice sys iowait steal irq soft guest idle nodename
        x = ['%s %s'%(d, l[0]), 'all', '0', '0', '0', '0', '0', '0', '0', '0', '0', rcEnv.nodename]
        x[1] = l[1].replace('-', 'all')
        x[2] = l[2]
        x[4] = l[3]
        x[5] = l[4]
        x[10] = l[5]
        lines.append(x)
    return lines

def stats_mem_u(file, collect_date=None):
    return twodays(stats_mem_u_day)

def stats_mem_u_day(t):
    return []

def stats_proc(file, collect_date=None):
    return twodays(stats_proc_day)

def stats_proc_day(t):
    d = t.strftime("%Y-%m-%d")
    day = t.strftime("%d")
    f = sarfile(day)
    if f is None:
        return []
    cmd = ['sar', '-q', '-f', f]
    (ret, buff, err) = call(cmd)
    lines = []
    for line in buff.split('\n'):
        l = line.split()
        if len(l) < 3:
            continue
        if ':' not in l[0]:
            continue
        """ xmlrpc: date runq_sz plist_sz ldavg_1 ldavg_5 ldavg_15 nodename
        """
        x = ['%s %s'%(d, l[0]), l[1], '0', '0', '0', '0', rcEnv.nodename]
        lines.append(x)
    return lines

def stats_swap(file, collect_date=None):
    return twodays(stats_swap_day)

def stats_swap_day(t):
    return []

def stats_block(file, collect_date=None):
    return twodays(stats_block_day)

def stats_block_day(t):
    d = t.strftime("%Y-%m-%d")
    day = t.strftime("%d")
    f = sarfile(day)
    if f is None:
        return []
    cmd = ['sar', '-b', '-f', f]
    (ret, buff, err) = call(cmd)
    lines = []
    for line in buff.split('\n'):
        l = line.split()
        if len(l) != 9:
            continue
        if ':' not in l[1]:
            continue

        """ xmlrpc: date tps rtps wtps rbps wbps nodename
        """
        x = ['%s %s'%(d, l[0]), '0', '0', '0', l[1], l[4], rcEnv.nodename]

        lines.append(x)
    return lines

def stats_blockdev(file, collect_date=None):
    return twodays(stats_blockdev_day)

def stats_blockdev_day(t):
    d = t.strftime("%Y-%m-%d")
    day = t.strftime("%d")
    f = sarfile(day)
    if f is None:
        return []
    cmd = ['sar', '-d', '-f', f]
    (ret, buff, err) = call(cmd, errlog=False)
    lines = []
    for line in buff.split('\n'):
        l = line.split()
        if len(l) == 8:
            date = l[0]
        if len(l) == 7:
            l = [date] + l
        if len(l) != 8:
            continue
        if l[1] == 'device':
            continue
        if l[0] == 'Average':
            continue
        """ xmlrpc: 22:05:01 DEV tps rd_sec/s wr_sec/s avgrq-sz avgqu-sz await svctm %util
                    00:00:00 device %busy avque r+w/s blks/s avwait avserv
        """
        x = ['%s %s'%(d, l[0]), l[1], l[4], '0', '0', '0', l[3], l[6], l[7], l[2], rcEnv.nodename]
        lines.append(x)
    return lines

def stats_netdev(file, collect_date=None):
    return twodays(stats_netdev_day)

def stats_netdev_day(t):
    return []

def stats_netdev_err(file, collect_date=None):
    return twodays(stats_netdev_err_day)

def stats_netdev_err_day(t):
    return []

