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
# To change this template, choose Tools | Templates
# and open the template in the editor.
"Module implement SunOS specific mounts"

import os

import rcStatus
import rcMountsSunOS as rcMounts
import resMount as Res
import action as ex

class Mount(Res.Mount):
    """ define SunOS mount/umount doAction """
    def __init__(self, mountPoint, device, fsType, mntOpt):
        self.Mounts = rcMounts.Mounts()
        Res.Mount.__init__(self, mountPoint, device, fsType, mntOpt)

    def is_up(self):
        return self.Mounts.has_mount(self.device, self.mountPoint)

    def status(self):
        if self.is_up(): return rcStatus.UP
        else: return rcStatus.DOWN

    def start(self):
        Res.Mount.start(self)
        self.Mounts = rcMounts.Mounts()

        if self.is_up() is True:
            self.log.info("fs(%s %s) is already mounted"%
                (self.device, self.mountPoint))
            return

        if self.fsType == 'zfs' :
            ret, out = self.vcall(['zfs', 'set', \
                                    'mountpoint='+self.mountPoint , \
                                    self.device ])
            if ret != 0 :
                raise ex.excError

            ret, out = self.vcall(['zfs', 'mount', self.device ])
            if ret != 0:
                raise ex.excError
            return

        if not os.path.exists(self.mountPoint):
            os.makedirs(self.mountPoint, 0755)
        cmd = ['mount', '-F', self.fsType, '-o', self.mntOpt, self.device, \
            self.mountPoint]
        (ret, out) = self.vcall(cmd)
        if ret != 0:
            raise ex.excError

    def stop(self):
        if self.is_up() is False:
            self.log.info("fs(%s %s) is already umounted"%
                    (self.device, self.mountPoint))
            return

        (ret, out) = self.vcall(['umount', self.mountPoint])
        if ret == 0 :
            return

        if self.fsType != 'lofs' :
            (ret, out) = self.vcall(['umount', '-f', self.mountPoint])
            if ret == 0 :
                return

        self.log.error("failed")
        raise ex.excError


if __name__ == "__main__":
    for c in (Mount,) :
        help(c)

