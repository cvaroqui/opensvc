"""
Monitor Thread
"""
import os
import sys
import time
import datetime
import codecs
import glob
import logging
import hashlib
import json
import tempfile
import shutil
from subprocess import Popen, PIPE

import osvcd_shared as shared
from comm import Crypt
from rcGlobalEnv import rcEnv, Storage
from rcUtilities import bdecode, purge_cache
from svcBuilder import build, fix_app_link, fix_exe_link

MON_WAIT_READY = datetime.timedelta(seconds=16)

STARTED_STATES = (
    "n/a",
    "up",
)
STOPPED_STATES = (
    "n/a",
    "down",
    "stdby up",
    "stdby down",
)

class Monitor(shared.OsvcThread, Crypt):
    """
    The monitoring thread collecting local service states and taking decisions.
    """
    monitor_period = 5
    default_stdby_nb_restart = 2

    def __init__(self):
        shared.OsvcThread.__init__(self)
        self._shutdown = False

    def run(self):
        self.log = logging.getLogger(rcEnv.nodename+".osvcd.monitor")
        self.last_run = 0
        self.log.info("monitor started")

        while True:
            self.do()
            if self.stopped():
                self.join_threads()
                self.terminate_procs()
                sys.exit(0)

    def do(self):
        self.janitor_threads()
        self.janitor_procs()
        self.reload_config()
        self.last_run = time.time()
        if self._shutdown:
            if len(self.procs) == 0:
                self.stop()
        else:
            self.merge_hb_data()
            self.orchestrator()
            self.sync_services_conf()
        self.update_hb_data()

        with shared.MON_TICKER:
            shared.MON_TICKER.wait(self.monitor_period)

    def shutdown(self):
        with shared.SERVICES_LOCK:
            for svc in shared.SERVICES.values():
                self.service_shutdown(svc.svcname)
        self._shutdown = True
        shared.wake_monitor()

    #########################################################################
    #
    # Service config exchange
    #
    #########################################################################
    def sync_services_conf(self):
        """
        For each service, decide if we have an outdated configuration file
        and fetch the most recent one if needed.
        """
        confs = self.get_services_configs()
        for svcname, data in confs.items():
            new_service = False
            with shared.SERVICES_LOCK:
                if svcname not in shared.SERVICES:
                    new_service = True
            if rcEnv.nodename not in data:
                # need to check if we should have this config ?
                new_service = True
            if new_service:
                ref_conf = Storage({
                    "cksum": "",
                    "updated": "0",
                })
                ref_nodename = rcEnv.nodename
            else:
                ref_conf = data[rcEnv.nodename]
                ref_nodename = rcEnv.nodename
            for nodename, conf in data.items():
                if rcEnv.nodename == nodename:
                    continue
                if rcEnv.nodename not in conf.get("scope", []):
                    # we are not a service node
                    continue
                if conf.cksum != ref_conf.cksum and \
                   conf.updated > ref_conf.updated:
                    ref_conf = conf
                    ref_nodename = nodename
            if ref_nodename == rcEnv.nodename:
                # we already have the most recent version
                continue
            with shared.SERVICES_LOCK:
                if svcname in shared.SERVICES and \
                   rcEnv.nodename in shared.SERVICES[svcname].nodes and \
                   ref_nodename in shared.SERVICES[svcname].drpnodes:
                    # don't fetch drp config from prd nodes
                    return
            self.log.info("node %s has the most recent service %s config",
                          ref_nodename, svcname)
            self.fetch_service_config(svcname, ref_nodename)
            if new_service:
                fix_exe_link(rcEnv.paths.svcmgr, svcname)
                fix_app_link(svcname)

    def fetch_service_config(self, svcname, nodename):
        """
        Fetch and install the most recent service configuration file, using
        the remote node listener.
        """
        request = {
            "action": "get_service_config",
            "options": {
                "svcname": svcname,
            },
        }
        resp = self.daemon_send(request, nodename=nodename)
        if resp.get("status", 1) != 0:
            self.log.error("unable to fetch service %s config from node %s: "
                           "received %s", svcname, nodename, resp)
            return
        with tempfile.NamedTemporaryFile(dir=rcEnv.paths.pathtmp, delete=False) as filep:
            tmpfpath = filep.name
        with codecs.open(tmpfpath, "w", "utf-8") as filep:
            filep.write(resp["data"])
        try:
            with shared.SERVICES_LOCK:
                if svcname in shared.SERVICES:
                    svc = shared.SERVICES[svcname]
                else:
                    svc = None
            if svc:
                results = svc._validate_config(path=filep.name)
            else:
                results = {"errors": 0}
            if results["errors"] == 0:
                dst = os.path.join(rcEnv.paths.pathetc, svcname+".conf")
                shutil.copy(filep.name, dst)
            else:
                self.log.error("the service %s config fetched from node %s is "
                               "not valid", svcname, nodename)
                return
        finally:
            os.unlink(tmpfpath)
        shared.SERVICES[svcname] = build(svcname, node=shared.NODE)
        self.log.info("the service %s config fetched from node %s is now "
                      "installed", svcname, nodename)

    #########################################################################
    #
    # Node and Service Commands
    #
    #########################################################################
    def generic_callback(self, svcname, status, local_expect):
        self.set_smon(svcname, status, local_expect)
        self.update_hb_data()

    def service_start_resources(self, svcname, rids):
        self.set_smon(svcname, "restarting")
        proc = self.service_command(svcname, ["start", "--rid", ",".join(rids)])
        self.push_proc(
            proc=proc,
            on_success="service_start_resources_on_success",
            on_success_args=[svcname, rids],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )

    def service_start_resources_on_success(self, svcname, rids):
        self.set_smon(svcname, status="idle", local_expect="started")
        for rid in rids:
            self.reset_smon_retries(svcname, rid)
        self.update_hb_data()

    def service_toc(self, svcname):
        proc = self.service_command(svcname, ["toc"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", None],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )

    def service_start(self, svcname):
        self.set_smon(svcname, "starting")
        proc = self.service_command(svcname, ["start"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", "started"],
            on_error="generic_callback", on_error_args=[svcname, "start failed", None],
        )

    def service_stop(self, svcname):
        self.set_smon(svcname, "stopping")
        proc = self.service_command(svcname, ["stop"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", "unset"],
            on_error="generic_callback", on_error_args=[svcname, "stop failed", None],
        )

    def service_shutdown(self, svcname):
        self.set_smon(svcname, "shutdown")
        proc = self.service_command(svcname, ["shutdown"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", "unset"],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )

    def service_provision(self, svcname):
        self.set_smon(svcname, "provisioning")
        proc = self.service_command(svcname, ["provision"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", None],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )

    def service_unprovision(self, svcname):
        self.set_smon(svcname, "unprovisioning", local_expect="unset")
        proc = self.service_command(svcname, ["unprovision"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", "unset"],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )

    def service_freeze(self, svcname):
        self.set_smon(svcname, "freezing")
        proc = self.service_command(svcname, ["freeze"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", None],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )

    def service_thaw(self, svcname):
        self.set_smon(svcname, "thawing")
        proc = self.service_command(svcname, ["thaw"])
        self.push_proc(
            proc=proc,
            on_success="generic_callback", on_success_args=[svcname, "idle", None],
            on_error="generic_callback", on_error_args=[svcname, "idle", None],
        )


    #########################################################################
    #
    # Orchestration
    #
    #########################################################################
    def orchestrator(self):
        self.node_orchestrator()
        with shared.SERVICES_LOCK:
            svcs = shared.SERVICES.values()
        for svc in svcs:
            self.service_orchestrator(svc)
            self.resources_orchestrator(svc)

    def resources_orchestrator(self, svc):
        if svc.frozen() or self.freezer.node_frozen():
            #self.log.info("resource %s orchestrator out (frozen)", svc.svcname)
            return
        if svc.disabled:
            #self.log.info("resource %s orchestrator out (disabled)", svc.svcname)
            return
        try:
            with shared.CLUSTER_DATA_LOCK:
                resources = shared.CLUSTER_DATA[rcEnv.nodename]["services"]["status"][svc.svcname]["resources"]
        except KeyError:
            return

        def monitored_resource(svc, rid, resource):
            if not resource["monitor"]:
                return []
            if resource["disable"]:
                return []
            if smon.local_expect != "started":
                return []
            nb_restart = svc.get_resource(rid).nb_restart
            retries = self.get_smon_retries(svc.svcname, rid)
            if retries > nb_restart:
                return []
            if retries >= nb_restart:
                self.inc_smon_retries(svc.svcname, rid)
                self.log.info("max retries (%d) reached for resource %s.%s",
                              nb_restart, svc.svcname, rid)
                self.service_toc(svc.svcname)
                return []
            self.inc_smon_retries(svc.svcname, rid)
            self.log.info("restart resource %s.%s %d/%d", svc.svcname, rid,
                          retries+1, nb_restart)
            return [rid]

        def stdby_resource(svc, rid):
            resource = svc.get_resource(rid)
            if resource is None or rcEnv.nodename not in resource.always_on:
                return []
            nb_restart = resource.nb_restart
            if nb_restart == 0:
                nb_restart = self.default_stdby_nb_restart
            retries = self.get_smon_retries(svc.svcname, rid)
            if retries > nb_restart:
                return []
            if retries >= nb_restart:
                self.inc_smon_retries(svc.svcname, rid)
                self.log.info("max retries (%d) reached for stdby resource "
                              "%s.%s", nb_restart, svc.svcname, rid)
                return []
            self.inc_smon_retries(svc.svcname, rid)
            self.log.info("start stdby resource %s.%s %d/%d", svc.svcname, rid,
                          retries+1, nb_restart)
            return [rid]

        smon = self.get_service_monitor(svc.svcname)
        if smon.status != "idle":
            return

        rids = []
        for rid, resource in resources.items():
            if resource["status"] not in ("down", "stdby down"):
                continue
            if resource.get("provisioned", {}).get("state") is False:
                continue
            rids += monitored_resource(svc, rid, resource)
            rids += stdby_resource(svc, rid)

        if len(rids) > 0:
            self.service_start_resources(svc.svcname, rids)

    def node_orchestrator(self):
        nmon = self.get_node_monitor()
        if nmon.status != "idle":
            return
        self.set_nmon_g_expect_from_status()
        if nmon.global_expect == "frozen":
            if not self.freezer.node_frozen():
                self.log.info("freeze node")
                self.freezer.node_freeze()
        elif nmon.global_expect == "thawed":
            if self.freezer.node_frozen():
                self.log.info("thaw node")
                self.freezer.node_thaw()

    def service_orchestrator(self, svc):
        if svc.disabled:
            #self.log.info("service %s orchestrator out (disabled)", svc.svcname)
            return
        smon = self.get_service_monitor(svc.svcname)
        if smon.status not in ("ready", "idle"):
            #self.log.info("service %s orchestrator out (mon status %s)", svc.svcname, smon.status)
            return
        status = self.get_agg_avail(svc.svcname)
        self.set_smon_g_expect_from_status(svc.svcname, smon, status)
        if smon.global_expect:
            self.service_orchestrator_manual(svc, smon, status)
        else:
            self.service_orchestrator_auto(svc, smon, status)

    def service_orchestrator_auto(self, svc, smon, status):
        """
        Automatic instance start decision.
        Verifies hard and soft affinity and anti-affinity, then routes to
        failover and flex specific policies.
        """
        if svc.frozen() or self.freezer.node_frozen():
            #self.log.info("service %s orchestrator out (frozen)", svc.svcname)
            return
        if status in (None, "undef", "n/a"):
            #self.log.info("service %s orchestrator out (agg avail status %s)",
            #              svc.svcname, status)
            return
        if svc.hard_anti_affinity:
            intersection = set(self.get_local_svcnames()) & set(svc.hard_anti_affinity)
            if len(intersection) > 0:
                #self.log.info("service %s orchestrator out (hard anti-affinity with %s)",
                #              svc.svcname, ','.join(intersection))
                return
        if svc.hard_affinity:
            intersection = set(self.get_local_svcnames()) & set(svc.hard_affinity)
            if len(intersection) < len(set(svc.hard_affinity)):
                #self.log.info("service %s orchestrator out (hard affinity with %s)",
                #              svc.svcname, ','.join(intersection))
                return
        candidates = self.placement_candidates(svc)
        if candidates != [rcEnv.nodename]:
            # the local node is not the only candidate, we can apply soft
            # affinity filtering
            if svc.soft_anti_affinity:
                intersection = set(self.get_local_svcnames()) & set(svc.soft_anti_affinity)
                if len(intersection) > 0:
                    #self.log.info("service %s orchestrator out (soft anti-affinity with %s)",
                    #              svc.svcname, ','.join(intersection))
                    return
            if svc.soft_affinity:
                intersection = set(self.get_local_svcnames()) & set(svc.soft_affinity)
                if len(intersection) < len(set(svc.soft_affinity)):
                    #self.log.info("service %s orchestrator out (soft affinity with %s)",
                    #              svc.svcname, ','.join(intersection))
                    return

        if svc.clustertype == "failover":
            self.service_orchestrator_auto_failover(svc, smon, status, candidates)
        elif svc.clustertype == "flex":
            self.service_orchestrator_auto_flex(svc, smon, status, candidates)

    def service_orchestrator_auto_failover(self, svc, smon, status, candidates):
        instance = self.get_service_instance(svc.svcname, rcEnv.nodename)
        if smon.status == "ready":
            if instance.avail is "up":
                self.log.info("abort 'ready' because the local instance "
                              "has started")
                self.set_smon(svc.svcname, "idle")
                return
            if status == "up":
                self.log.info("abort 'ready' because an instance has started")
                self.set_smon(svc.svcname, "idle")
                return
            peer = self.better_peer_ready(svc, candidates)
            if peer:
                self.log.info("abort 'ready' because node %s has a better "
                              "placement score for service %s and is also "
                              "ready", peer, svc.svcname)
                self.set_smon(svc.svcname, "idle")
                return
            peer = self.peer_transitioning(svc)
            if peer:
                self.log.info("abort 'ready' because node %s is already "
                              "acting on service %s", peer, svc.svcname)
                self.set_smon(svc.svcname, "idle")
                return
            now = datetime.datetime.utcnow()
            if smon.status_updated < (now - MON_WAIT_READY):
                self.log.info("failover service %s status %s/ready for "
                              "%s", svc.svcname, status,
                              now-smon.status_updated)
                self.service_start(svc.svcname)
                return
            self.log.info("service %s will start in %s",
                          svc.svcname,
                          str(smon.status_updated+MON_WAIT_READY-now))
        elif smon.status == "idle":
            if status not in ("down", "stdby down", "stdby up"):
                return
            if len(svc.peers) == 1:
                self.log.info("failover service %s status %s/idle and "
                              "single node", svc.svcname, status)
                self.service_start(svc.svcname)
                return
            if not self.placement_leader(svc, candidates):
                return
            self.log.info("failover service %s status %s", svc.svcname,
                          status)
            self.set_smon(svc.svcname, "ready")

    def service_orchestrator_auto_flex(self, svc, smon, status, candidates):
        instance = self.get_service_instance(svc.svcname, rcEnv.nodename)
        n_up = self.count_up_service_instances(svc.svcname)
        if smon.status == "ready":
            if (n_up - 1) >= svc.flex_min_nodes:
                self.log.info("flex service %s instance count reached "
                              "required minimum while we were ready",
                              svc.svcname)
                self.set_smon(svc.svcname, "idle")
                return
            now = datetime.datetime.utcnow()
            if smon.status_updated < (now - MON_WAIT_READY):
                self.log.info("flex service %s status %s/ready for %s",
                              svc.svcname, status, now-smon.status_updated)
                self.service_start(svc.svcname)
            else:
                self.log.info("service %s will start in %s", svc.svcname,
                              str(smon.status_updated+MON_WAIT_READY-now))
        elif smon.status == "idle":
            if n_up >= svc.flex_min_nodes:
                return
            if instance.avail not in STOPPED_STATES:
                return
            if not self.placement_leader(svc, candidates):
                return
            self.log.info("flex service %s started, starting or ready to "
                          "start instances: %d/%d. local status %s",
                          svc.svcname, n_up, svc.flex_min_nodes,
                          instance.avail)
            self.set_smon(svc.svcname, "ready")

    def service_orchestrator_manual(self, svc, smon, status):
        """
        Take actions to meet global expect target, set by user or by
        service_orchestrator_auto()
        """
        instance = self.get_service_instance(svc.svcname, rcEnv.nodename)
        if smon.global_expect == "frozen":
            if not svc.frozen():
                self.log.info("freeze service %s", svc.svcname)
                self.service_freeze(svc.svcname)
        elif smon.global_expect == "thawed":
            if svc.frozen():
                self.log.info("thaw service %s", svc.svcname)
                self.service_thaw(svc.svcname)
        elif smon.global_expect == "stopped":
            if not svc.frozen():
                self.log.info("freeze service %s", svc.svcname)
                self.service_freeze(svc.svcname)
            if instance.avail not in STOPPED_STATES:
                thawed_on = self.service_instances_thawed(svc.svcname)
                if thawed_on:
                    self.log.info("service %s still has thawed instances on "
                                  "nodes %s, delay stop", svc.svcname,
                                  ", ".join(thawed_on))
                else:
                    self.service_stop(svc.svcname)
        elif smon.global_expect == "started":
            if svc.frozen():
                self.log.info("thaw service %s", svc.svcname)
                self.service_thaw(svc.svcname)
            elif status not in STARTED_STATES:
                self.service_orchestrator_auto(svc, smon, status)
        elif smon.global_expect == "unprovisioned":
            if not self.service_unprovisioned(instance):
                self.service_unprovision(svc.svcname)
        elif smon.global_expect == "provisioned":
            if not self.service_provisioned(instance):
                self.service_provision(svc.svcname)

    def count_up_service_instances(self, svcname):
        n_up = 0
        for instance in self.get_service_instances(svcname).values():
            if instance["avail"] == "up":
                n_up += 1
            elif instance["monitor"]["status"] in ("restarting", "starting", "ready"):
                n_up += 1
        return n_up

    def peer_transitioning(self, svc):
        """
        Return the nodename of the first peer with the service in a transition
        state.
        """
        for nodename, instance in self.get_service_instances(svc.svcname).items():
            if nodename == rcEnv.nodename:
                continue
            if instance["monitor"]["status"].endswith("ing"):
                return nodename

    def better_peer_ready(self, svc, candidates):
        """
        Return the nodename of the first peer with the service in ready state, or
        None if we are placement leader or no peer is in ready state.
        """
        if self.placement_leader(svc, candidates):
            return
        for nodename, instance in self.get_service_instances(svc.svcname).items():
            if nodename == rcEnv.nodename:
                continue
            if instance["monitor"]["status"] == "ready":
                return nodename

    #########################################################################
    #
    # Cluster nodes aggregations
    #
    #########################################################################
    @staticmethod
    def get_clu_agg_frozen():
        fstatus = "undef"
        fstatus_l = []
        n_instances = 0
        with shared.CLUSTER_DATA_LOCK:
            for node in shared.CLUSTER_DATA.values():
                try:
                    fstatus_l.append(node["frozen"])
                except KeyError:
                    # sender daemon outdated
                    continue
                n_instances += 1
        n_frozen = fstatus_l.count(True)
        if n_instances == 0:
            fstatus = 'n/a'
        elif n_frozen == n_instances:
            fstatus = 'frozen'
        elif n_frozen == 0:
            fstatus = 'thawed'
        else:
            fstatus = 'mixed'
        return fstatus

    #########################################################################
    #
    # Service instances status aggregation
    #
    #########################################################################
    def get_agg_avail(self, svcname):
        svc = self.get_service(svcname)
        if svc is None:
            return "unknown"
        if svc.clustertype == "failover":
            return self.get_agg_avail_failover(svc)
        elif svc.clustertype == "flex":
            return self.get_agg_avail_flex(svc)
        else:
            return "unknown"

    def get_agg_overall(self, svcname):
        ostatus = 'undef'
        ostatus_l = []
        n_instances = 0
        for instance in self.get_service_instances(svcname).values():
            ostatus_l.append(instance["overall"])
            n_instances += 1
        ostatus_s = set(ostatus_l)

        if n_instances == 0:
            ostatus = 'n/a'
        elif ostatus_s == set(['n/a']):
            ostatus = 'n/a'
        elif 'warn' in ostatus_s or 'stdby down' in ostatus_s:
            ostatus = 'warn'
        elif set(['up']) == ostatus_s or \
             set(['up', 'down']) == ostatus_s or \
             set(['up', 'stdby up']) == ostatus_s or \
             set(['up', 'down', 'stdby up']) == ostatus_s or \
             set(['up', 'down', 'stdby up', 'n/a']) == ostatus_s:
            ostatus = 'up'
        elif set(['down']) == ostatus_l or \
             set(['down', 'stdby up']) == ostatus_s or \
             set(['down', 'stdby up', 'n/a']) == ostatus_s:
            ostatus = 'down'
        return ostatus

    def get_agg_frozen(self, svcname):
        frozen = 0
        total = 0
        for instance in self.get_service_instances(svcname).values():
            if instance["frozen"]:
                frozen += 1
            total += 1
        if total == 0:
            return "n/a"
        elif frozen == total:
            return "frozen"
        elif frozen == 0:
            return "thawed"
        else:
            return "mixed"

    def get_agg_avail_failover(self, svc):
        astatus = 'undef'
        astatus_l = []
        n_instances = 0
        for instance in self.get_service_instances(svc.svcname).values():
            astatus_l.append(instance["avail"])
            n_instances += 1
        astatus_s = set(astatus_l)

        n_up = astatus_l.count("up")
        if n_instances == 0:
            astatus = 'n/a'
        elif astatus_s == set(['n/a']):
            astatus = 'n/a'
        elif 'warn' in astatus_l:
            astatus = 'warn'
        elif n_up > 1:
            astatus = 'warn'
        elif n_up == 1:
            astatus = 'up'
        else:
            astatus = 'down'
        return astatus

    def get_agg_avail_flex(self, svc):
        astatus = 'undef'
        astatus_l = []
        n_instances = 0
        for instance in self.get_service_instances(svc.svcname).values():
            astatus_l.append(instance["avail"])
            n_instances += 1
        astatus_s = set(astatus_l)

        n_up = astatus_l.count("up")
        if n_instances == 0:
            astatus = 'n/a'
        elif astatus_s == set(['n/a']):
            astatus = 'n/a'
        elif n_up == 0:
            astatus = 'down'
        elif 'warn' in astatus_l:
            astatus = 'warn'
        elif n_up > svc.flex_max_nodes:
            astatus = 'warn'
        elif n_up < svc.flex_min_nodes:
            astatus = 'warn'
        else:
            astatus = 'up'
        return astatus

    def get_agg_placement(self, svcname):
        svc = self.get_service(svcname)
        for instance in self.get_service_instances(svc.svcname).values():
            if instance["avail"] != "up" and instance["monitor"].get("placement") == "leader":
                return "non-optimal"
        return "optimal"

    def get_agg_provisioned(self, svcname):
        svc = self.get_service(svcname)
        provisioned = 0
        total = 0
        for instance in self.get_service_instances(svc.svcname).values():
            total += 1
            if instance["provisioned"]:
                provisioned += 1
        if provisioned == total:
            return True
        elif provisioned == 0:
            return False
        return "mixed"

    #
    def service_instances_frozen(self, svcname):
        """
        Return the nodenames with a frozen instance of the specified service.
        """
        return [nodename for (nodename, instance) in \
                self.get_service_instances(svcname).items() if \
                instance["frozen"]]

    def service_instances_thawed(self, svcname):
        """
        Return the nodenames with a frozen instance of the specified service.
        """
        return [nodename for (nodename, instance) in \
                self.get_service_instances(svcname).items() if \
                not instance["frozen"]]

    @staticmethod
    def get_local_svcnames():
        """
        Extract service instance names from the locally maintained hb data.
        """
        svcnames = []
        try:
            with shared.CLUSTER_DATA_LOCK:
                for svcname in shared.CLUSTER_DATA[rcEnv.nodename]["services"]["status"]:
                    if shared.CLUSTER_DATA[rcEnv.nodename]["services"]["status"][svcname]["avail"] == "up":
                        svcnames.append(svcname)
        except KeyError:
            return []
        return svcnames

    @staticmethod
    def get_services_configs():
        """
        Return a hash indexed by svcname and nodename, containing the services
        configuration mtime and checksum.
        """
        data = {}
        with shared.CLUSTER_DATA_LOCK:
            for nodename in shared.CLUSTER_DATA:
                try:
                    for svcname in shared.CLUSTER_DATA[nodename]["services"]["config"]:
                        if svcname not in data:
                            data[svcname] = {}
                        data[svcname][nodename] = Storage(shared.CLUSTER_DATA[nodename]["services"]["config"][svcname])
                except KeyError:
                    pass
        return data

    @staticmethod
    def get_service_instances(svcname):
        """
        Return the specified service status structures on all nodes.
        """
        instances = {}
        with shared.CLUSTER_DATA_LOCK:
            for nodename in shared.CLUSTER_DATA:
                try:
                    if svcname in shared.CLUSTER_DATA[nodename]["services"]["status"]:
                        instances[nodename] = shared.CLUSTER_DATA[nodename]["services"]["status"][svcname]
                except KeyError:
                    continue
        return instances

    @staticmethod
    def fsum(fpath):
        """
        Return a file content checksum
        """
        with codecs.open(fpath, "r", "utf-8") as filep:
            buff = filep.read()
        cksum = hashlib.md5(buff.encode("utf-8"))
        return cksum.hexdigest()

    @staticmethod
    def get_last_svc_config(svcname):
        with shared.CLUSTER_DATA_LOCK:
            try:
                return shared.CLUSTER_DATA[rcEnv.nodename]["services"]["config"][svcname]
            except KeyError:
                return

    def get_services_config(self):
        config = {}
        for cfg in glob.glob(os.path.join(rcEnv.paths.pathetc, "*.conf")):
            svcname = os.path.basename(cfg[:-5])
            if svcname == "node":
                continue
            linkp = os.path.join(rcEnv.paths.pathetc, svcname)
            if not os.path.exists(linkp):
                continue
            try:
                mtime = os.path.getmtime(cfg)
            except Exception as exc:
                self.log.warning("failed to get %s mtime: %s", cfg, str(exc))
                mtime = 0
            mtime = datetime.datetime.utcfromtimestamp(mtime)
            last_config = self.get_last_svc_config(svcname)
            if last_config is None or mtime > datetime.datetime.strptime(last_config["updated"], shared.DATEFMT):
                self.log.info("compute service %s config checksum", svcname)
                cksum = self.fsum(cfg)
                try:
                    with shared.SERVICES_LOCK:
                        shared.SERVICES[svcname] = build(svcname, node=shared.NODE)
                except Exception as exc:
                    self.log.error("%s build error: %s", svcname, str(exc))
                    continue
            else:
                cksum = last_config["cksum"]
            if last_config is None:
                self.log.info("purge %s status cache" % svcname)
                shared.SERVICES[svcname].purge_status_caches()
            with shared.SERVICES_LOCK:
                scope = sorted(list(shared.SERVICES[svcname].nodes | shared.SERVICES[svcname].drpnodes))
            config[svcname] = {
                "updated": mtime.strftime(shared.DATEFMT),
                "cksum": cksum,
                "scope": scope,
            }

        # purge deleted services
        with shared.SERVICES_LOCK:
            for svcname in list(shared.SERVICES.keys()):
                if svcname not in config:
                    self.log.info("purge deleted service %s", svcname)
                    del shared.SERVICES[svcname]
        return config

    def get_last_svc_status_mtime(self, svcname):
        """
        Return the mtime of the specified service configuration file on the
        local node. If unknown, return 0.
        """
        instance = self.get_service_instance(svcname, rcEnv.nodename)
        if instance is None:
            return 0
        return instance["mtime"]

    def service_status_fallback(self, svcname):
        """
        Return the specified service status structure fetched from an execution
        of svcmgr -s <svcname> json status". As we arrive here when the
        status.json doesn't exist, we don't have to specify --refresh.
        """
        self.log.info("slow path service status eval: %s", svcname)
        try:
            with shared.SERVICES_LOCK:
                return shared.SERVICES[svcname].print_status_data(mon_data=False)
        except KeyboardInterrupt:
            return

    def get_services_status(self, svcnames):
        """
        Return the local services status data, fetching data from status.json
        caches if their mtime changed or from CLUSTER_DATA[rcEnv.nodename] if
        not.

        Also update the monitor 'local_expect' field for each service.
        """
        purge_cache()
        with shared.CLUSTER_DATA_LOCK:
            try:
                data = shared.CLUSTER_DATA[rcEnv.nodename]["services"]["status"]
            except KeyError:
                data = {}
        for svcname in svcnames:
            fpath = os.path.join(rcEnv.paths.pathvar, svcname, "status.json")
            try:
                mtime = os.path.getmtime(fpath)
            except Exception:
                # force service status refresh
                mtime = time.time() + 1
            last_mtime = self.get_last_svc_status_mtime(svcname)
            if svcname not in data or mtime > last_mtime and svcname in data:
                #self.log.info("service %s status changed", svcname)
                try:
                    with open(fpath, 'r') as filep:
                        try:
                            data[svcname] = json.load(filep)
                        except ValueError:
                            data[svcname] = self.service_status_fallback(svcname)
                except Exception:
                    data[svcname] = self.service_status_fallback(svcname)
            if not data[svcname]:
                del data[svcname]
                continue
            with shared.SERVICES_LOCK:
                data[svcname]["frozen"] = shared.SERVICES[svcname].frozen()
            self.set_smon_l_expect_from_status(data, svcname)
            data[svcname]["monitor"] = self.get_service_monitor(svcname,
                                                                datestr=True)

        # purge deleted services
        for svcname in set(data.keys()) - set(svcnames):
            del data[svcname]

        return data

    #########################################################################
    #
    # Service-specific monitor data helpers
    #
    #########################################################################
    @staticmethod
    def reset_smon_retries(svcname, rid):
        with shared.SMON_DATA_LOCK:
            if svcname not in shared.SMON_DATA:
                return
            if "restart" not in shared.SMON_DATA[svcname]:
                return
            if rid in shared.SMON_DATA[svcname].restart:
                del shared.SMON_DATA[svcname].restart[rid]
            if len(shared.SMON_DATA[svcname].restart.keys()) == 0:
                del shared.SMON_DATA[svcname].restart

    @staticmethod
    def get_smon_retries(svcname, rid):
        with shared.SMON_DATA_LOCK:
            if svcname not in shared.SMON_DATA:
                return 0
            if "restart" not in shared.SMON_DATA[svcname]:
                return 0
            if rid not in shared.SMON_DATA[svcname].restart:
                return 0
            else:
                return shared.SMON_DATA[svcname].restart[rid]

    @staticmethod
    def inc_smon_retries(svcname, rid):
        with shared.SMON_DATA_LOCK:
            if svcname not in shared.SMON_DATA:
                return
            if "restart" not in shared.SMON_DATA[svcname]:
                shared.SMON_DATA[svcname].restart = Storage()
            if rid not in shared.SMON_DATA[svcname].restart:
                shared.SMON_DATA[svcname].restart[rid] = 1
            else:
                shared.SMON_DATA[svcname].restart[rid] += 1

    def all_nodes_frozen(self):
        with shared.CLUSTER_DATA_LOCK:
             for data in shared.CLUSTER_DATA.values():
                 if not data["frozen"]:
                     return False
        return True

    def all_nodes_thawed(self):
        with shared.CLUSTER_DATA_LOCK:
             for data in shared.CLUSTER_DATA.values():
                 if data["frozen"]:
                     return False
        return True

    def set_nmon_g_expect_from_status(self):
        nmon = self.get_node_monitor()
        if nmon.global_expect is None:
            return
        if nmon.global_expect == "frozen" and self.all_nodes_frozen():
            self.log.info("node global expect is %s and is frozen",
                          nmon.global_expect)
            self.set_nmon(global_expect="unset")
        elif nmon.global_expect == "thawed" and self.all_nodes_thawed():
            self.log.info("node global expect is %s and is thawed",
                          nmon.global_expect)
            self.set_nmon(global_expect="unset")

    def set_smon_g_expect_from_status(self, svcname, smon, status):
        """
        Align global_expect with the actual service states.
        """
        if smon.global_expect is None:
            return
        instance = self.get_service_instance(svcname, rcEnv.nodename)
        local_frozen = instance["frozen"]
        frozen = self.get_agg_frozen(svcname)
        provisioned = self.get_agg_provisioned(svcname)
        if smon.global_expect == "stopped" and status in STOPPED_STATES and \
           local_frozen:
            self.log.info("service %s global expect is %s and its global "
                          "status is %s", svcname, smon.global_expect, status)
            self.set_smon(svcname, global_expect="unset")
        elif smon.global_expect == "started" and \
             status in STARTED_STATES and not local_frozen:
            self.log.info("service %s global expect is %s and its global "
                          "status is %s", svcname, smon.global_expect, status)
            self.set_smon(svcname, global_expect="unset")
        elif smon.global_expect == "frozen" and frozen == "frozen":
            self.log.info("service %s global expect is %s and is frozen",
                          svcname, smon.global_expect)
            self.set_smon(svcname, global_expect="unset")
        elif smon.global_expect == "thawed" and frozen == "thawed":
            self.log.info("service %s global expect is %s and is thawed",
                          svcname, smon.global_expect)
            self.set_smon(svcname, global_expect="unset")
        elif smon.global_expect == "unprovisioned" and provisioned is False:
            self.log.info("service %s global expect is %s and is unprovisioned",
                          svcname, smon.global_expect)
            self.set_smon(svcname, global_expect="unset")
        elif smon.global_expect == "provisioned" and provisioned is True:
            self.log.info("service %s global expect is %s and is provisioned",
                          svcname, smon.global_expect)
            self.set_smon(svcname, global_expect="unset")

    def set_smon_l_expect_from_status(self, data, svcname):
        if svcname not in data:
            return
        with shared.SMON_DATA_LOCK:
            if svcname not in shared.SMON_DATA:
                return
            if data[svcname]["avail"] == "up" and \
               shared.SMON_DATA[svcname].local_expect != "started":
                self.log.info("service %s monitor local_expect change "
                              "%s => %s", svcname,
                              shared.SMON_DATA[svcname].local_expect, "started")
                shared.SMON_DATA[svcname].local_expect = "started"

    def getloadavg(self):
        try:
            return round(os.getloadavg()[2], 1)
        except:
            # None < 0 == True
            return

    def update_hb_data(self):
        """
        Update the heartbeat payload we send to other nodes.
        Crypt it so the tx threads don't have to do it on their own.
        """
        #self.log.info("update heartbeat data to send")
        load_avg = self.getloadavg()
        config = self.get_services_config()
        status = self.get_services_status(config.keys())

        try:
            with shared.CLUSTER_DATA_LOCK:
                shared.CLUSTER_DATA[rcEnv.nodename] = {
                    "frozen": self.freezer.node_frozen(),
                    "env": rcEnv.node_env,
                    "monitor": self.get_node_monitor(datestr=True),
                    "updated": datetime.datetime.utcfromtimestamp(time.time())\
                                                .strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "services": {
                        "config": config,
                        "status": status,
                    },
                    "load": {
                        "15m": load_avg,
                    },
                }
            with shared.HB_MSG_LOCK:
                shared.HB_MSG = self.encrypt(shared.CLUSTER_DATA[rcEnv.nodename])
                if shared.HB_MSG is None:
                    shared.HB_MSG_LEN = 0
                else:
                    shared.HB_MSG_LEN = len(shared.HB_MSG)
            shared.wake_heartbeat_tx()
        except ValueError:
            self.log.error("failed to refresh local cluster data: invalid json")

    def merge_hb_data(self):
        self.merge_hb_data_monitor()
        self.merge_hb_data_provision()

    def merge_hb_data_monitor(self):
        """
        Set the global expect received through heartbeats as local expect, if
        the service instance is not already in the expected status.
        """
        with shared.CLUSTER_DATA_LOCK:
            nodenames = list(shared.CLUSTER_DATA.keys())
        if rcEnv.nodename not in nodenames:
            return
        nodenames.remove(rcEnv.nodename)
        with shared.CLUSTER_DATA_LOCK:
            # merge node monitors
            for nodename in nodenames:
                try:
                    global_expect = shared.CLUSTER_DATA[nodename]["monitor"].get("global_expect")
                except KeyError:
                    # sender daemon is outdated
                    continue
                if global_expect is None:
                    continue
                local_frozen = shared.CLUSTER_DATA[rcEnv.nodename]["frozen"]
                if (global_expect == "frozen" and not local_frozen) or \
                   (global_expect == "thawed" and local_frozen):
                    self.log.info("node %s wants local node %s", nodename, global_expect)
                    self.set_nmon(global_expect=global_expect)
                else:
                    self.log.info("node %s wants local node %s, already is", nodename, global_expect)

            # merge every service monitors
            for svcname, instance in shared.CLUSTER_DATA[rcEnv.nodename]["services"]["status"].items():
                for nodename in nodenames:
                    rinstance = self.get_service_instance(svcname, nodename)
                    if rinstance is None:
                        continue
                    global_expect = rinstance["monitor"].get("global_expect")
                    if global_expect is None:
                        continue
                    current_global_expect = instance["monitor"].get("global_expect")
                    if global_expect == current_global_expect:
                        self.log.info("node %s wants service %s %s, already targeting that",
                                      nodename, svcname, global_expect)
                        continue
                    local_avail = instance["avail"]
                    local_frozen = instance["frozen"]
                    frozen = self.get_agg_frozen(svcname)
                    status = self.get_agg_avail(svcname)
                    provisioned = self.get_agg_provisioned(svcname)
                    if (global_expect == "stopped" and (local_avail not in STOPPED_STATES or not local_frozen)) or \
                       (global_expect == "started" and (status not in STARTED_STATES or local_frozen)) or \
                       (global_expect == "frozen" and frozen != "frozen") or \
                       (global_expect == "thawed" and frozen != "thawed") or \
                       (global_expect == "provisioned" and provisioned is not True) or \
                       (global_expect == "unprovisioned" and provisioned is not False):
                        self.log.info("node %s wants service %s %s", nodename, svcname, global_expect)
                        self.set_smon(svcname, global_expect=global_expect)
                    else:
                        self.log.info("node %s wants service %s %s, already is", nodename, svcname, global_expect)

    def merge_hb_data_provision(self):
        """
        Merge the resource provisioned state from the peer with the most
        up-to-date change time.
        """
        with shared.SERVICES_LOCK, shared.CLUSTER_DATA_LOCK:
            for svc in shared.SERVICES.values():
                changed = False
                for resource in svc.shared_resources:
                    try:
                        local = Storage(shared.CLUSTER_DATA[rcEnv.nodename]["services"]["status"][svc.svcname]["resources"][resource.rid]["provisioned"])
                    except KeyError:
                        local = Storage()
                    for nodename in svc.peers:
                        try:
                            remote = Storage(shared.CLUSTER_DATA[nodename]["services"]["status"][svc.svcname]["resources"][resource.rid]["provisioned"])
                        except KeyError:
                            continue
                        if remote.state is None:
                            continue
                        elif remote.mtime > local.mtime + 0.00001:
                            self.log.info("switch %s.%s provisioned flag to %s (merged from %s)",
                                          svc.svcname, resource.rid, str(remote.state), 
                                          nodename)
                            resource.write_is_provisioned_flag(remote.state, remote.mtime)
                            changed = True
                if changed:
                    svc.purge_status_data_dump()

    def service_provisioned(self, instance):
        return instance.get("provisioned")

    def service_unprovisioned(self, instance):
        for resource in instance["resources"].values():
            if resource.get("provisioned", {}).get("state") is True:
                return False
        return True

    def status(self):
        self.update_hb_data()
        data = shared.OsvcThread.status(self)
        with shared.CLUSTER_DATA_LOCK:
            data.nodes = dict(shared.CLUSTER_DATA)
        data["services"] = {}
        data["frozen"] = self.get_clu_agg_frozen()
        for svcname in data.nodes[rcEnv.nodename]["services"]["config"]:
            if svcname not in data["services"]:
                data["services"][svcname] = Storage()
            data["services"][svcname].avail = self.get_agg_avail(svcname)
            data["services"][svcname].frozen = self.get_agg_frozen(svcname)
            data["services"][svcname].overall = self.get_agg_overall(svcname)
            data["services"][svcname].placement = self.get_agg_placement(svcname)
            data["services"][svcname].provisioned = self.get_agg_provisioned(svcname)
        return data
