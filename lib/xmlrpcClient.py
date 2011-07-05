#!/usr/bin/python
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
from datetime import datetime, timedelta
import xmlrpclib
import os
from rcGlobalEnv import rcEnv
import rcStatus
import socket
import httplib

hostId = __import__('hostid'+rcEnv.sysname)
hostid = hostId.hostid()
rcEnv.warned = False

import logging
import logging.handlers
log = logging.getLogger("xml")
fileformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
filehandler = logging.handlers.RotatingFileHandler("/tmp/xml.log")
filehandler.setFormatter(fileformatter)
log.addHandler(filehandler)
log.setLevel(logging.DEBUG)
log.debug("logger setup")

class Collector(object):
    proxy = None
    proxy_method = None
    comp_proxy = None
    comp_proxy_method = None

    def split_url(self, url):
        if url == 'None':
            return 'https', '127.0.0.1', '443', '/'
        if url.startswith('https'):
            transport = 'https'
            url = url.replace('https://', '')
        elif url.startswith('http'):
            transport = 'http'
            url = url.replace('http://', '')
        l = url.split('/')
        if len(l) < 2:
            raise
        app = l[1]
        l = l[0].split(':')
        if len(l) == 1:
            host = l[0]
            if transport == 'http':
                port = '80'
            else:
                port = '443'
        elif len(l) == 2:
            host = l[0]
            port = l[1]
        else:
            raise
        return transport, host, port, app
    
    def setNodeEnv(self):
        import ConfigParser
        pathetc = os.path.join(os.path.dirname(__file__), '..', 'etc')
        nodeconf = os.path.join(pathetc, 'node.conf')
        config = ConfigParser.RawConfigParser()
        config.read(nodeconf)
        if config.has_option('node', 'dbopensvc'):
            rcEnv.dbopensvc = config.get('node', 'dbopensvc')
            try:
                rcEnv.dbopensvc_transport, rcEnv.dbopensvc_host, rcEnv.dbopensvc_port, rcEnv.dbopensvc_app = self.split_url(rcEnv.dbopensvc)
            except:
                import sys
                print >>sys.stderr, "malformed dbopensvc url: %s"%rcEnv.dbopensvc
        if config.has_option('node', 'dbcompliance'):
            rcEnv.dbcompliance = config.get('node', 'dbcompliance')
            try:
                rcEnv.dbcompliance_transport, rcEnv.dbcompliance_host, rcEnv.dbcompliance_port, rcEnv.dbcompliance_app = self.split_url(rcEnv.dbcompliance)
            except:
                import sys
                print >>sys.stderr, "malformed dbcompliance url: %s"%rcEnv.dbcompliance
        if config.has_option('node', 'uuid'):
            rcEnv.uuid = config.get('node', 'uuid')
        else:
            rcEnv.uuid = ""
        del(config)
    
    def call_dummy(self, *args):
        pass
    
    def call(self, *args, **kwargs):
        fn = args[0]
        self.init(fn)
        if len(args) > 1:
            args = args[1:]
        else:
            args = []
        if fn == "register_node" and \
           'register_node' not in self.proxy_methods:
            import sys
            print >>sys.stderr, "collector does not support node registration"
            return
        if rcEnv.uuid == "" and \
           rcEnv.dbopensvc is not None and \
           not rcEnv.warned and \
           self.auth_node and \
           fn != "register_node":
            import sys
            print >>sys.stderr, "this node is not registered. try 'nodemgr register'"
            print >>sys.stderr, "to disable this warning, set 'dbopensvc = None' in node.conf"
            rcEnv.warned = True
            return
        try:
            return getattr(self, fn)(*args, **kwargs)
        except (socket.error, xmlrpclib.ProtocolError):
            """ normal for collector communications disabled
                through 127.0.0.1 == dbopensvc
            """
            pass
        except socket.timeout:
            print "connection to collector timed out"
        except:
            import sys
            import traceback
            e = sys.exc_info()
            print e[0], e[1], traceback.print_tb(e[2])
    
    def __init__(self):
        self.comp_fns = ['comp_get_moduleset_modules',
                         'comp_get_moduleset',
                         'comp_attach_moduleset',
                         'comp_detach_moduleset',
                         'comp_get_ruleset',
                         'comp_get_dated_ruleset',
                         'comp_attach_ruleset',
                         'comp_detach_ruleset',
                         'comp_list_ruleset',
                         'comp_list_moduleset',
                         'comp_log_action']

    def init(self, fn):
        if fn in self.comp_fns and self.comp_proxy is not None:
            return
        elif self.proxy is not None:
            return

        self.setNodeEnv()
    
        try:
            a = socket.getaddrinfo(rcEnv.dbopensvc_host, None)
            if len(a) == 0:
                raise Exception
        except:
            import sys
            print >>sys.stderr, "could not resolve %s to an ip address. disable collector updates."%rcEnv.dbopensvc
            self.call = self.call_dummy

        if fn not in self.comp_fns:
            socket.setdefaulttimeout(20)
            try:
                self.proxy = xmlrpclib.ServerProxy(rcEnv.dbopensvc)
                self.proxy_methods = self.proxy.system.listMethods()
            except:
                self.proxy = xmlrpclib.ServerProxy("https://127.0.0.1/")
                self.proxy_methods = []
            
            log.debug("%d methods found on collector"%len(self.proxy_methods))

            if len(self.proxy_methods) == 0:
                self.auth_node = True
            elif "register_node" in self.proxy_methods:
                self.auth_node = True
            else:
                self.auth_node = False
        else:
            socket.setdefaulttimeout(30)
            try:
                self.comp_proxy = xmlrpclib.ServerProxy(rcEnv.dbcompliance)
                self.comp_proxy_methods = self.comp_proxy.system.listMethods()
            except:
                self.comp_proxy = xmlrpclib.ServerProxy("https://127.0.0.1/")
                self.comp_proxy_methods = []
            
            log.debug("%d comp methods found on collector"%len(self.comp_proxy_methods))

            if len(self.comp_proxy_methods) == 0:
                self.auth_node = True
            elif "register_node" in self.comp_proxy_methods:
                self.auth_node = True
            else:
                self.auth_node = False

        socket.setdefaulttimeout(120)
        
   
    def begin_action(self, svc, action, begin):
        try:
            import version
            version = version.version
        except:
            version = "0";
    
        args = [['svcname',
             'action',
             'hostname',
             'hostid',
             'version',
             'begin',
             'cron'],
            [repr(svc.svcname),
             repr(action),
             repr(rcEnv.nodename),
             repr(hostid),
             repr(version),
             repr(str(begin)),
             '1' if svc.cron else '0']
        ]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.begin_action(*args)
    
    def end_action(self, svc, action, begin, end, logfile):
        err = 'ok'
        dateprev = None
        lines = open(logfile, 'r').read()
        pids = set([])
    
        """Example logfile line:
        2009-11-11 01:03:25,252;;DISK.VG;;INFO;;unxtstsvc01_data is already up;;10200;;EOL
        """
        vars = ['svcname',
                'action',
                'hostname',
                'hostid',
                'pid',
                'begin',
                'end',
                'status_log',
                'status',
                'cron']
        vals = []
        for line in lines.split(';;EOL\n'):
            if line.count(';;') != 4:
                continue
            date = line.split(';;')[0]
    
            """Push to database the previous line, so that begin and end
            date are available.
            """
            if dateprev is not None:
                res = res.lower()
                res = res.replace(svc.svcname+'.','')
                vals.append([svc.svcname,
                             res+' '+action,
                             rcEnv.nodename,
                             hostid,
                             pid,
                             dateprev,
                             date,
                             msg,
                             res_err,
                             '1' if svc.cron else '0'])
    
            res_err = 'ok'
            (date, res, lvl, msg, pid) = line.split(';;')
    
            # database overflow protection
            trim_lim = 10000
            trim_tag = ' <trimmed> '
            trim_head = int(trim_lim/2)
            trim_tail = trim_head-len(trim_tag)
            if len(msg) > trim_lim:
                msg = msg[:trim_head]+' <trimmed> '+msg[-trim_tail:]
    
            pids |= set([pid])
            if lvl is None or lvl == 'DEBUG':
                continue
            if lvl == 'ERROR':
                err = 'err'
                res_err = 'err'
            if lvl == 'WARNING' and err != 'err':
                err = 'warn'
            if lvl == 'WARNING' and res_err != 'err':
                res_err = 'warn'
            dateprev = date
    
        """Push the last log entry, using 'end' as end date
        """
        if dateprev is not None:
            res = res.lower()
            res = res.replace(svc.svcname+'.','')
            vals.append([svc.svcname,
                         res+' '+action,
                         rcEnv.nodename,
                         hostid,
                         pid,
                         dateprev,
                         date,
                         msg,
                         res_err,
                         '1' if svc.cron else '0'])
    
        if len(vals) > 0:
            args = [vars, vals]
            if self.auth_node:
                args += [(rcEnv.uuid, rcEnv.nodename)]
            self.proxy.res_action_batch(*args)
    
        """Complete the wrap-up database entry
        """
    
        """ If logfile is empty, default to current process pid
        """
        if len(pids) == 0:
            pids = set([os.getpid()])
    
        args = [
            ['svcname',
             'action',
             'hostname',
             'hostid',
             'pid',
             'begin',
             'end',
             'time',
             'status',
             'cron'],
            [repr(svc.svcname),
             repr(action),
             repr(rcEnv.nodename),
             repr(hostid),
             repr(','.join(map(str, pids))),
             repr(str(begin)),
             repr(str(end)),
             repr(str(end-begin)),
             repr(str(err)),
             '1' if svc.cron else '0']
        ]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.end_action(*args)
    
    def svcmon_update_combo(self, g_vars, g_vals, r_vars, r_vals):
        log.debug("enter svcmon_update_combo")
        if 'svcmon_update_combo' in self.proxy_methods:
            args = [g_vars, g_vals, r_vars, r_vals]
            if self.auth_node:
                args += [(rcEnv.uuid, rcEnv.nodename)]
            log.debug("proxy.svcmon_update_combo: %s"%str(args))
            self.proxy.svcmon_update_combo(*args)
        else:
            args = [g_vars, g_vals]
            if self.auth_node:
                args += [(rcEnv.uuid, rcEnv.nodename)]
            log.debug("proxy.svcmon_update: %s"%str(args))
            self.proxy.svcmon_update(*args)
            args = [r_vars, r_vals]
            if self.auth_node:
                args += [(rcEnv.uuid, rcEnv.nodename)]
            log.debug("proxy.resmon_update: %s"%str(args))
            self.proxy.resmon_update(*args)
        log.debug("leave svcmon_update_combo")
    
    def push_service(self, svc):
        def envfile(svc):
            envfile = os.path.join(rcEnv.pathsvc, 'etc', svc+'.env')
            if not os.path.exists(envfile):
                return
            with open(envfile, 'r') as f:
                buff = ""
                for line in f.readlines():
                    l = line.strip()
                    if len(l) == 0:
                        continue
                    if l[0] == '#' or l[0] == ';':
                        continue
                    buff += line
                return buff
            return
    
        try:
            import version
            version = version.version
        except:
            version = "0";
    
        if hasattr(svc, "guestos"):
            guestos = svc.guestos
        else:
            guestos = ""
    
        vars = ['svc_hostid',
                'svc_name',
                'svc_vmname',
                'svc_cluster_type',
                'svc_flex_min_nodes',
                'svc_flex_max_nodes',
                'svc_flex_cpu_low_threshold',
                'svc_flex_cpu_high_threshold',
                'svc_type',
                'svc_nodes',
                'svc_drpnode',
                'svc_drpnodes',
                'svc_comment',
                'svc_drptype',
                'svc_autostart',
                'svc_app',
                'svc_containertype',
                'svc_envfile',
                'svc_version',
                'svc_drnoaction',
                'svc_guestos',
                'svc_ha']
    
        vals = [repr(hostid),
                repr(svc.svcname),
                repr(svc.vmname),
                repr(svc.clustertype),
                repr(svc.flex_min_nodes),
                repr(svc.flex_max_nodes),
                repr(svc.flex_cpu_low_threshold),
                repr(svc.flex_cpu_high_threshold),
                repr(svc.svctype),
                repr(' '.join(svc.nodes)),
                repr(svc.drpnode),
                repr(' '.join(svc.drpnodes)),
                repr(svc.comment),
                repr(svc.drp_type),
                repr(' '.join(svc.autostart_node)),
                repr(svc.app),
                repr(svc.svcmode),
                repr(envfile(svc.svcname)),
                repr(version),
                repr(svc.drnoaction),
                repr(guestos),
                '1' if svc.ha else '0']
    
        if 'container' in svc.resources_by_id:
            container_info = svc.resources_by_id['container'].get_container_info()
            vars += ['svc_vcpus', 'svc_vmem']
            vals += [container_info['vcpus'],
                     container_info['vmem']]
    
        args = [vars, vals]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.update_service(*args)
    
    def delete_services(self):
        args = [hostid]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.delete_services(*args)
    
    def push_disks(self, svc):
        def disk_dg(dev, svc):
            for rset in svc.get_res_sets("disk.vg"):
                for vg in rset.resources:
                    if vg.is_disabled():
                        continue
                    if not vg.name in disklist_cache:
                        disklist_cache[vg.name] = vg.disklist()
                    if dev in disklist_cache[vg.name]:
                        return vg.name
            return ""
    
        di = __import__('rcDiskInfo'+rcEnv.sysname)
        disks = di.diskInfo()
        disklist_cache = {}
    
        args = [svc.svcname, rcEnv.nodename]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.delete_disks(*args)
    
        for d in svc.disklist():
            if disks.disk_id(d) is None or disks.disk_id(d) == "":
                """ no point pushing to db an empty entry
                """
                continue
            args = [['disk_id',
                 'disk_svcname',
                 'disk_size',
                 'disk_vendor',
                 'disk_model',
                 'disk_dg',
                 'disk_nodename'],
                [repr(disks.disk_id(d)),
                 repr(svc.svcname),
                 repr(disks.disk_size(d)),
                 repr(disks.disk_vendor(d)),
                 repr(disks.disk_model(d)),
                 repr(disk_dg(d, svc)),
                 repr(rcEnv.nodename)]
            ]
            if self.auth_node:
                args += [(rcEnv.uuid, rcEnv.nodename)]
            self.proxy.register_disk(*args)
    
    def push_stats_fs_u(self, l):
        args = [l[0], l[1]]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.insert_stats_fs_u(*args)
    
    def push_pkg(self):
        p = __import__('rcPkg'+rcEnv.sysname)
        vars = ['pkg_nodename',
                'pkg_name',
                'pkg_version',
                'pkg_arch']
        vals = p.listpkg()
        args = [rcEnv.nodename]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.delete_pkg(*args)
        args = [vars, vals]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.insert_pkg(*args)
    
    def push_patch(self):
        p = __import__('rcPkg'+rcEnv.sysname)
        vars = ['patch_nodename',
                'patch_num',
                'patch_rev']
        vals = p.listpatch()
        args = [rcEnv.nodename]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.delete_patch(*args)
        args = [vars, vals]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.insert_patch(*args)
    
    def push_stats(self, force=False, interval=None, stats_dir=None, stats_start=None, stats_end=None):
        try:
            s = __import__('rcStats'+rcEnv.sysname)
        except ImportError:
            return
        sp = s.StatsProvider(interval=interval,
                             stats_dir=stats_dir,
                             stats_start=stats_start,
                             stats_end=stats_end)
        h = {}
        for stat in ['cpu', 'mem_u', 'proc', 'swap', 'block',
                     'blockdev', 'netdev', 'netdev_err']:
            h[stat] = sp.get(stat)
        import cPickle
        args = [cPickle.dumps(h)]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.insert_stats(*args)
    
    def push_asset(self, node):
        try:
            m = __import__('rcAsset'+rcEnv.sysname)
        except ImportError:
            print "pushasset methods not implemented on", rcEnv.sysname
            return
        if "update_asset" not in self.proxy_methods:
            print "'update_asset' method is not exported by the collector"
            return
        d = m.Asset(node).get_asset_dict()
        args = [d.keys(), d.values()]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.update_asset(*args)
    
    def push_sym(self):
        if 'update_sym_xml' not in self.proxy_methods:
    	    print "'update_sym_xml' method is not exported by the collector"
    	    return
        m = __import__('rcSymmetrix')
        try:
            syms = m.Syms()
        except:
            return
        for sym in syms:
            vals = []
            for key in sym.keys:
                vals.append(getattr(sym, 'get_'+key)())
            sym_proxy = ServerProxy(rcEnv.dbopensvc)
            args = [sym.sid, sym.keys, vals]
            if self.auth_node:
                args += [(rcEnv.uuid, rcEnv.nodename)]
            sym_proxy.update_sym_xml(*args)
    
    def push_all(self, svcs):
        args = [[svc.svcname for svc in svcs]]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.delete_service_list(*args)
        for svc in svcs:
            self.push_disks(svc)
            self.push_service(svc)
    
    def push_checks(self, vars, vals):
        if "push_checks" not in self.proxy_methods:
            print "'push_checks' method is not exported by the collector"
            return
        args = [vars, vals]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        self.proxy.push_checks(*args)
    
    def register_node(self):
        return self.proxy.register_node(rcEnv.nodename)
    
    def comp_get_moduleset_modules(self, moduleset):
        args = [moduleset]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_get_moduleset_modules(*args)
    
    def comp_get_moduleset(self):
        args = [rcEnv.nodename]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_get_moduleset(*args)
    
    def comp_attach_moduleset(self, moduleset):
        args = [rcEnv.nodename, moduleset]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_attach_moduleset(*args)
    
    def comp_detach_moduleset(self, moduleset):
        args = [rcEnv.nodename, moduleset]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_detach_moduleset(*args)
    
    def comp_get_ruleset(self):
        args = [rcEnv.nodename]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_get_ruleset(*args)
    
    def comp_get_dated_ruleset(self, date):
        args = [rcEnv.nodename, date]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_get_dated_ruleset(*args)
    
    def comp_attach_ruleset(self, ruleset):
        args = [rcEnv.nodename, ruleset]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_attach_ruleset(*args)
    
    def comp_detach_ruleset(self, ruleset):
        args = [rcEnv.nodename, ruleset]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_detach_ruleset(*args)
    
    def comp_list_ruleset(self, pattern='%'):
        args = [pattern, rcEnv.nodename]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_list_rulesets(*args)
    
    def comp_list_moduleset(self, pattern='%'):
        args = [pattern]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_list_modulesets(*args)
    
    def comp_log_action(self, vars, vals):
        args = [vars, vals]
        if self.auth_node:
            args += [(rcEnv.uuid, rcEnv.nodename)]
        return self.comp_proxy.comp_log_action(*args)


if __name__ == "__main__":
    x = Collector()
    x.init()
    print x.proxy_methods
    print x.comp_proxy_methods
