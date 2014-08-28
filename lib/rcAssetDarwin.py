#
# Copyright (c) 2010 Christophe Varoqui <christophe.varoqui@free.fr>'
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
from rcUtilities import justcall, which
from rcGlobalEnv import rcEnv
import rcAsset

class Asset(rcAsset.Asset):
    def __init__(self, node):
        rcAsset.Asset.__init__(self, node)
        self.info = {}
        (out, err, ret) = justcall(['system_profiler', 'SPHardwareDataType', 'SPSoftwareDataType'])
        if ret == 0:
            for line in out.split('\n'):
                l = line.split(':')
                if len(l) != 2: continue
                self.info[l[0].strip()] = l[1].strip()

    def _get_mem_bytes(self):
        if 'Memory' not in self.info:
            return '0'
        m = self.info['Memory'].split()
        size = int(m[0])
        unit = m[1]
        if unit == 'GB':
            size = size * 1024
        elif unit == 'MB':
            pass
        else:
            raise
        return str(size)

    def _get_mem_banks(self):
        return '0'

    def _get_mem_slots(self):
        return '0'

    def _get_os_vendor(self):
        return 'Apple'

    def _get_os_release(self):
        if 'System Version' in self.info:
            return self.info['System Version']
        (out, err, ret) = justcall(['uname', '-r'])
        if ret != 0:
            return 'Unknown'
        return out.split()[0]

    def _get_os_kernel(self):
        if 'Kernel Version' not in self.info:
            return '0'
        return self.info['Kernel Version']

    def _get_os_arch(self):
        cmd = ['uname', '-m']
        (out, err, ret) = justcall(cmd)
        if ret != 0:
            return 'Unknown'
        return out.split('\n')[0]

    def _get_cpu_freq(self):
        if 'Processor Speed' not in self.info:
            return '0'
        return self.info['Processor Speed']

    def _get_cpu_cores(self):
        if 'Total Number of Cores' not in self.info:
            return '0'
        return self.info['Total Number of Cores']

    def _get_cpu_dies(self):
        if 'Number of Processors' not in self.info:
            return '0'
        return self.info['Number of Processors']

    def _get_cpu_model(self):
        if 'Processor Name' not in self.info:
            return '0'
        return self.info['Processor Name']

    def _get_serial(self):
        if 'Hardware UUID' not in self.info:
            return '0'
        return self.info['Hardware UUID']

    def _get_model(self):
        if 'Model Name' not in self.info:
            return '0'
        return self.info['Model Name']

