#
# Copyright (c) 2009 Christophe Varoqui <christophe.varoqui@free.fr>'
# Copyright (c) 2009 Cyril Galibern <cyril.galibern@free.fr>'
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

from subprocess import *

import rcIfconfig

class ifconfig(rcIfconfig.ifconfig):
    def parse(self, out):
        prev = ''
        prevprev = ''
        for w in out.split():
            if w == 'Link':
                i = rcIfconfig.interface(prev)
                self.intf.append(i)

                # defaults
                i.link_encap = ''
                i.scope = ''
                i.bcast = ''
                i.mask = ''
                i.mtu = ''
                i.ipaddr = ''
                i.ip6addr = []
                i.ip6mask = []
                i.hwaddr = ''
                i.flag_up = False
                i.flag_broadcast = False
                i.flag_running = False
                i.flag_multicast = False
                i.flag_loopback = False
            elif 'encap:' in w:
                (null, i.link_encap) = w.split(':')
            elif 'Scope:' in w:
                (null, i.scope) = w.split(':')
            elif 'Bcast:' in w:
                (null, i.bcast) = w.split(':')
            elif 'Mask:' in w:
                (null, i.mask) = w.split(':')
            elif 'MTU:' in w:
                (null, i.mtu) = w.split(':')

            if 'inet' == prev and 'addr:' in w:
                (null, i.ipaddr) = w.split(':')
            if 'inet6' == prevprev and 'addr:' == prev:
                (ip6addr, ip6mask) = w.split('/')
                i.ip6addr += [ip6addr]
                i.ip6mask += [ip6mask]
            if 'HWaddr' == prev:
                i.hwaddr = w
            if 'UP' == w:
                i.flag_up = True
            if 'BROADCAST' == w:
                i.flag_broadcast = True
            if 'RUNNING' == w:
                i.flag_running = True
            if 'MULTICAST' == w:
                i.flag_multicast = True
            if 'LOOPBACK' == w:
                i.flag_loopback = True

            prevprev = prev
            prev = w

    def __init__(self):
        self.intf = []
        out = Popen(['ifconfig', '-a'], stdout=PIPE).communicate()[0]
        self.parse(out)
