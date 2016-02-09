#
# Copyright (c) 2009 Christophe Varoqui <christophe.varoqui@opensvc.com>'
# Copyright (c) 2009 Cyril Galibern <cyril.galibern@opensvc.com>'
# Copyright (c) 2014 Arnaud Veron <arnaud.veron@opensvc.com>'
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

class Mount:
    def __init__(self, dev, mnt, type, mnt_opt):
        self.dev = dev.rstrip('/')
        self.mnt = mnt.rstrip('/')
        if mnt is '/':
            self.mnt = mnt
        self.type = type
        self.mnt_opt = mnt_opt

    def __str__(self):
        return "Mount: dev[%s] mnt[%s] type[%s] options[%s]" % \
            (self.dev,self.mnt,self.type,self.mnt_opt)

class Mounts:
    def __init__(self):
        """ OS dependent """
        self.mounts = []

    def __iter__(self):
        return iter(self.mounts)

    def match_mount(self):
        """ OS dependent """
        pass

    def mount(self, dev, mnt):
        for i in self.mounts:
            if self.match_mount(i, dev, mnt):
                return i
        return None

    def has_mount(self, dev, mnt):
        for i in self.mounts:
            if self.match_mount(i, dev, mnt):
                return True
        return False

    def has_param(self, param, value):
        for i in self.mounts:
            if getattr(i, param) == value:
                return i
        return None

    def sort(self, key='mnt', reverse=False):
        if len(self.mounts) == 0:
            return
        if key not in ('mnt', 'dev', 'type'):
            return
        self.mounts.sort(lambda x, y: cmp(getattr(x, key), getattr(y, key)), reverse=reverse)

    def get_fpath_dev(self, fpath):
        last = False
        d = fpath
        while not last:
            d = os.path.dirname(d)
            m = self.has_param("mnt", d)
            if m:
                return m.dev
            if d == os.sep:
                last = True

    def __str__(self):
        output="%s" % (self.__class__.__name__)
        for m in self.mounts:
            output+="\n  %s" % m.__str__()
        return output
