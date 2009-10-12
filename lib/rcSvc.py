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
import os
import sys
import ConfigParser
import logging
import glob
import re

from rcGlobalEnv import *
from rcFreeze import Freezer
from rcNode import discover_node
import rcOptParser
import rcApp
import rcLogger
import rcAddService
import ResRsync

def svcmode_mod_name(svcmode=''):
	"""Returns the name of the module implementing the specificities
	of a service mode. For example:
	lxc    => rcSvcLxc
	hosted => rcSvcHosted
	"""
	if svcmode == 'lxc':
		return 'rcSvcLxc'
	elif svcmode == 'hosted':
		return 'rcSvcHosted'
	return 1 # raise something instead ?

def add_ips(self):
	"""Parse the configuration file and add an ip object for each [ip#n]
	section. Ip objects are stored in a list in the service object.
	"""
	for s in self.conf.sections():
		if re.match('ip#[0-9]', s, re.I) is None:
			continue
		ipname = self.conf.get(s, "ipname")
		ipdev = self.conf.get(s, "ipdev")
		self.add_ip(ipname, ipdev)

def add_loops(self):
	"""Parse the configuration file and add a loop object for each [loop#n]
	section. Loop objects are stored in a list in the service object.
	"""
	for s in self.conf.sections():
		if re.match('loop#[0-9]', s, re.I) is None:
			continue
		file = self.conf.get(s, "file")
		self.add_loop(file)

def add_volumegroups(self):
	"""Parse the configuration file and add a vg object for each [vg#n]
	section. Vg objects are stored in a list in the service object.
	"""
	for s in self.conf.sections():
		if re.match('vg#[0-9]', s, re.I) is None:
			continue
		name = self.conf.get(s, "vgname")
		if self.conf.has_option(s, 'optional'):
			optional = self.conf.getboolean(s, "optional")
		else:
			optional = False
		self.add_volumegroup(name, optional)

def add_filesystems(self):
	"""Parse the configuration file and add a fs object for each [fs#n]
	section. Fs objects are stored in a list in the service object.
	"""
	for s in self.conf.sections():
		if re.match('fs#[0-9]', s, re.I) is None:
			continue
		dev = self.conf.get(s, "dev")
		mnt = self.conf.get(s, "mnt")
		type = self.conf.get(s, "type")
		mnt_opt = self.conf.get(s, "mnt_opt")
		if self.conf.has_option(s, 'optional'):
			optional = self.conf.getboolean(s, "optional")
		else:
			optional = False
		self.add_filesystem(dev, mnt, type, mnt_opt, optional)

def add_syncs(self):
	"""Add mandatory node-to-nodes and node-to-drpnode synchronizations, plus
	the those described in the config file.
	"""
	for s in self.conf.sections():
		if re.match('sync#[0-9]', s, re.I) is None:
			continue
		if not self.conf.has_option(s, 'src') or \
		   not self.conf.has_option(s, 'dst'):
			log.error("config file section %s must have src and dst set" % s)
			return 1
		src = self.conf.get(s, "src")
		dst = self.conf.get(s, "dst")
		if self.conf.has_option(s, 'exclude'):
			exclude = self.conf.get(s, 'exclude')
		else:
			exclude = ''
		if self.conf.has_option(s, 'target'):
			target = self.conf.get(s, 'target').split()
		else:
			target = ['nodes', 'drpnode']

		self.add_sync(src, dst, exclude, target)

def install_actions(self):
	"""Setup the class svc methods as per node capabilities and
	service configuration.
	"""
	if self.conf is None:
		self.create = self.rcMode.create
		return None

	self.status = self.rcMode.status
	self.frozen = self.rcMode.frozen

	if not Freezer(self.svcname).frozen():
		self.freeze = self.rcMode.freeze
	else:
		self.thaw = self.rcMode.thaw
		return None

	# generic actions
	self.start = self.rcMode.start
	self.stop = self.rcMode.stop
	self.startapp = self.rcMode.startapp
	self.stopapp = self.rcMode.stopapp

	if self.conf.has_section("fs#1") is True:
		self.mount = self.rcMode.mount
		self.umount = self.rcMode.umount
		self.diskstop = self.rcMode.diskstop
		self.diskstart = self.rcMode.diskstart
	if self.conf.has_section("loop#1") is True:
		self.startloop = self.rcMode.startloop
		self.stoploop = self.rcMode.stoploop
		self.diskstop = self.rcMode.diskstop
		self.diskstart = self.rcMode.diskstart
	if self.conf.has_section("vg#1") is True:
		self.startvg = self.rcMode.startvg
		self.stopvg = self.rcMode.stopvg
		self.diskstop = self.rcMode.diskstop
		self.diskstart = self.rcMode.diskstart
	if self.conf.has_section("ip#1") is True:
		self.startip = self.rcMode.startip
		self.stopip = self.rcMode.stopip
	if self.svcmode == 'lxc':
		self.startlxc = self.rcMode.startlxc
		self.stoplxc = self.rcMode.stoplxc
	if rcEnv.nodename in self.nodes:
		if len(self.nodes) > 1:
			self.syncnodes = syncnodes
		if len(self.drpnode) > 0:
			self.syncdrp = syncdrp
	return 0

def setup_logging():
	"""Setup logging to stream + logfile, and logfile rotation
	class Logger instance name: 'log'
	"""
	logging.setLoggerClass(rcLogger.Logger)
	global log
	log = logging.getLogger('INIT')
	if '--debug' in sys.argv:
		rcEnv.loglevel = logging.DEBUG
		log.setLevel(logging.DEBUG)
	elif '--warn' in sys.argv:
		rcEnv.loglevel = logging.WARNING
		log.setLevel(logging.WARNING)
	elif '--error' in sys.argv:
		rcEnv.loglevel = logging.ERROR
		log.setLevel(logging.ERROR)
	else:
		rcEnv.loglevel = logging.INFO
		log.setLevel(logging.INFO)

def syncnodes(self):
	"""Run all sync jobs to peer nodes for the service
	"""
	for s in self.syncs:
		if s.syncnodes() != 0: return 1

def syncdrp(self):
	"""Run all sync jobs to drp nodes for the service
	"""
	for s in self.syncs:
		if s.syncdrp() != 0: return 1

class svc():
	"""This base class exposes actions available to all type of services,
	like stop, start, ...
	It's meant to be enriched by inheriting class for specialized services,
	like LXC containers, ...
	"""

	def add_ip(self, ipname, ipdev):
		"""Append an ip object the self.ips list
		"""
		log = logging.getLogger('INIT')
		ip = self.rcMode.Ip(self, ipname, ipdev)
		if ip is None:
			log.error("register failed for ip (%s@%s)" %
				 (ipname, ipdev))
			return 1
		log.debug("registered ip (%s@%s)" %
			 (ipname, ipdev))
		self.ips.append(ip)

	def add_loop(self, name):
		"""Append a loop object the self.loops list
		"""
		log = logging.getLogger('INIT')
		loop = self.rcMode.Loop(name)
		if loop is None:
			log.error("register failed for loop (%s)" %
				 (name))
			return 1
		log.debug("registered loop (%s)" %
			 (name))
		self.loops.append(loop)

	def add_volumegroup(self, name, optional):
		"""Append a vg object the self.volumegroups list
		"""
		log = logging.getLogger('INIT')
		vg = self.rcMode.Vg(name)
		if vg is None:
			log.error("register failed for vg (%s)" %
				 (name))
			return 1
		log.debug("registered vg (%s)" %
			 (name))
		self.volumegroups.append(vg)

	def add_filesystem(self, dev, mnt, type, mnt_opt, optional):
		"""Append a fs object the self.filesystems list
		"""
		log = logging.getLogger('INIT')
		fs = self.rcMode.Filesystem(dev, mnt, type, mnt_opt, optional)
		if fs is None:
			log.error("register failed for fs (%s %s %s %s)" %
				 (dev, mnt, type, mnt_opt))
			return 1
		log.debug("registered fs (%s %s %s %s)" %
			 (dev, mnt, type, mnt_opt))
		self.filesystems.append(fs)

	def add_sync(self, src, dst, exclude, target):
		"""Append a synchronization to the self.syncs list
		"""
		log = logging.getLogger('INIT')
		sync = ResRsync.Rsync(self, src, dst, exclude, target)
		log.debug("registered sync (%s => %s on %s)" % (src, dst, target))
		self.syncs.append(sync)

	def __init__(self, name):
		#
		# file tree abstraction
		#
		self.svcname = name
		rcEnv.pathsvc = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
		rcEnv.pathbin = os.path.join(rcEnv.pathsvc, 'bin')
		rcEnv.pathetc = os.path.join(rcEnv.pathsvc, 'etc')
		rcEnv.pathlib = os.path.join(rcEnv.pathsvc, 'lib')
		rcEnv.pathlog = os.path.join(rcEnv.pathsvc, 'log')
		rcEnv.pathtmp = os.path.join(rcEnv.pathsvc, 'tmp')
		rcEnv.pathvar = os.path.join(rcEnv.pathsvc, 'var')
		rcEnv.logfile = os.path.join(rcEnv.pathlog, self.svcname) + '.log'
		rcEnv.svcconf = os.path.join(rcEnv.pathetc, self.svcname) + '.env'
		rcEnv.svcinitd = os.path.join(rcEnv.pathetc, self.svcname) + '.d'
		rcEnv.sysname, rcEnv.nodename, x, x, rcEnv.machine = os.uname()

		setup_logging()
		if name == "rcService":
			log.error("do not execute rcService directly")
			return None

		#
		# print stuff we determined so far
		#
		log.debug('sysname = ' + rcEnv.sysname)
		log.debug('nodename = ' + rcEnv.nodename)
		log.debug('machine = ' + rcEnv.machine)
                log.debug('pathsvc = ' + rcEnv.pathsvc)
                log.debug('pathbin = ' + rcEnv.pathbin)
                log.debug('pathetc = ' + rcEnv.pathetc)
                log.debug('pathlib = ' + rcEnv.pathlib)
                log.debug('pathlog = ' + rcEnv.pathlog)
                log.debug('pathtmp = ' + rcEnv.pathtmp)
		log.debug('service name = ' + self.svcname)
		log.debug('service config file = ' + rcEnv.svcconf)
                log.debug('service log file = ' + rcEnv.logfile)
                log.debug('service init dir = ' + rcEnv.svcinitd)

		#
		# node discovery is hidden in a separate module to
		# keep it separate from the framework stuff
		#
		discover_node()

		#
		# parse service configuration file
		# class RawConfigParser instance name: 'conf'
		#
		self.svcmode = "hosted"
		self.conf = None
		if os.path.isfile(rcEnv.svcconf):
			self.conf = ConfigParser.RawConfigParser()
			self.conf.read(rcEnv.svcconf)
			if self.conf.has_option("default", "mode"):
				self.svcmode = self.conf.get("default", "mode")

		#
		# dynamically import the action class matching the service mode
		#
		log.debug('service mode = ' + self.svcmode)
		self.rcMode = __import__(svcmode_mod_name(self.svcmode), globals(), locals(), [], -1)


		#
		# Setup service properties from config file content
		#
		self.nodes = []
		self.drpnode = []
		if self.conf.has_option("default", "nodes"):
			self.nodes = self.conf.get("default", "nodes").split()
		if self.conf.has_option("default", "drpnode"):
			self.drpnode = self.conf.get("default", "drpnode").split()

		#
		# plug service methods
		#
		if install_actions(self) != 0: return None

		#
		# instanciate resources
		#
		self.lxc = None
		if self.svcmode == 'lxc': self.lxc = self.rcMode.Lxc(self)

		self.ips = []
		add_ips(self)

		self.loops = []
		add_loops(self)

		self.volumegroups = []
		add_volumegroups(self)

		self.filesystems = []
		add_filesystems(self)

		self.syncs = []
		add_syncs(self)

		self.apps = None
		self.apps = rcApp.Apps(self)

