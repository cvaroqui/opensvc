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

import sys
import os
import re
from rcUtilities import call, which
import rcDiskInfo
import math
from rcGlobalEnv import rcEnv

class diskInfo(rcDiskInfo.diskInfo):
    disk_ids = {}

    def prefix_local(self, id):
        return '.'.join((rcEnv.nodename, id))

    def disk_id(self, dev):
        if 'cciss' in dev:
            return self.cciss_id(dev)
        else:
            return self.scsi_id(dev)

    def cciss_id(self, dev):
        if dev in self.disk_ids:
            return self.disk_ids[dev]
        if which('cciss_id'):
            cciss_id = 'cciss_id'
        else:
            return ""
        cmd = [cciss_id, dev]
        (ret, out, err) = call(cmd)
        if ret == 0:
            id = out.split('\n')[0]
            if id.startswith('3'):
                id = id[1:]
            else:
                id = self.prefix_local(id)
            self.disk_ids[dev] = id
            return id
        return ""

    def scsi_id(self, dev):
        if dev in self.disk_ids:
            return self.disk_ids[dev]
        if which('scsi_id'):
            scsi_id = 'scsi_id'
        elif which('/lib/udev/scsi_id'):
            scsi_id = '/lib/udev/scsi_id'
        else:
            return ""
        cmd = [scsi_id, '-g', '-u', '-d', dev]
        (ret, out, err) = call(cmd)
        if ret == 0:
            id = out.split('\n')[0]
            if id.startswith('3'):
                id = id[1:]
            else:
                id = self.prefix_local(id)
            self.disk_ids[dev] = id
            return id
        sdev = dev.replace("/dev/", "/block/")
        cmd = [scsi_id, '-g', '-u', '-s', sdev]
        (ret, out, err) = call(cmd, errlog=False)
        if ret == 0:
            id = out.split('\n')[0]
            if id.startswith('3'):
                id = id[1:]
            else:
                id = self.prefix_local(id)
            self.disk_ids[dev] = id
            return id
        return ""

    def disk_vendor(self, dev):
        if 'cciss' in dev:
            return 'HP'
        s = ''
        dev = re.sub("[0-9]+$", "", dev)
        path = dev.replace('/dev/', '/sys/block/')+'/device/vendor'
        if not os.path.exists(path):
            return ""
        with open(path, 'r') as f:
            s = f.read()
            f.close()
        return s.strip()

    def disk_model(self, dev):
        if 'cciss' in dev:
            return 'VOLUME'
        s = ''
        dev = re.sub("[0-9]+$", "", dev)
        path = dev.replace('/dev/', '/sys/block/')+'/device/model'
        if not os.path.exists(path):
            return ""
        with open(path, 'r') as f:
            s = f.read()
            f.close()
        return s.strip()

    def disk_size(self, dev):
        size = 0
        if '/dev/mapper/' in dev:
            try:
                statinfo = os.stat(dev)
            except:
                self.log.error("can not stat %s" % dev)
                raise
            dm = 'dm-' + str(os.minor(statinfo.st_rdev))
            path = '/sys/block/' + dm + '/size'
            if not os.path.exists(path):
                return 0
        else:
            path = dev.replace('/dev/', '/sys/block/')+'/size'
            if not os.path.exists(path):
                cmd = ['blockdev', '--getsize', dev]
                (ret, out, err) = call(cmd)
                if ret != 0:
                    return 0
                return int(math.ceil(1.*int(out)/2097152))

        with open(path, 'r') as f:
            size = f.read()
            f.close()
        return int(math.ceil(1.*int(size)/2097152))

