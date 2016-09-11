from __future__ import print_function
from stat import *
import os
import sys
import re
import datetime
import rcExceptions as ex
from rcGlobalEnv import rcEnv
from rcUtilities import is_exe, justcall, banner
from subprocess import *
from rcPrintTable import print_table

class Collector(object):
    def __init__(self, options=None, collector=None, svcname=None):
        self.options = options
        self.collector = collector
        self.svcname = svcname
        self.options = options

    def expand_list(self, d):
        if len(d) < 2:
            return []
        l = []
        titles = d[0]
        for _d in d[1:]:
            h = {}
            for a, b in zip(titles, _d):
                h[a] = b
            l.append(h)
        return l

    def rotate_root_pw(self, pw):
        opts = {}
        opts['pw'] = pw
        d = self.collector.call('collector_update_root_pw', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

    def collector_ack_unavailability(self):
        if self.svcname is None:
            return

        opts = {}
        opts['svcname'] = self.svcname
        if self.options.begin is not None:
            opts['begin'] = self.options.begin
        if self.options.end is not None:
            opts['end'] = self.options.end
        if self.options.author is not None:
            opts['author'] = self.options.author
        if self.options.comment is not None:
            opts['comment'] = self.options.comment
        if self.options.duration is not None:
            opts['duration'] = self.options.duration
        if self.options.account:
            opts['account'] = "1"
        else:
            opts['account'] = "0"

        d = self.collector.call('collector_ack_unavailability', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

    def collector_list_unavailability_ack(self):
        d = self._collector_list_unavailability_ack()
        print_table(d, table=self.options.table)

    def collector_json_list_unavailability_ack(self):
        d = self._collector_list_unavailability_ack()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_list_unavailability_ack(self):
        if self.svcname is None:
            return

        opts = {}
        opts['svcname'] = self.svcname
        if self.options.begin is not None:
            opts['begin'] = self.options.begin
        if self.options.end is not None:
            opts['end'] = self.options.end
        if self.options.author is not None:
            opts['author'] = self.options.author
        if self.options.comment is not None:
            opts['comment'] = self.options.comment
        if self.options.duration is not None:
            opts['duration'] = self.options.duration
        if self.options.account:
            opts['account'] = "1"
        else:
            opts['account'] = "0"

        d = self.collector.call('collector_list_unavailability_ack', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_list_actions(self):
        d = self._collector_list_actions()
        print_table(d, table=self.options.table)

    def collector_json_list_actions(self):
        d = self._collector_list_actions()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_list_actions(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        if self.options.begin is not None:
            opts['begin'] = self.options.begin
        if self.options.end is not None:
            opts['end'] = self.options.end
        if self.options.duration is not None:
            opts['duration'] = self.options.duration

        d = self.collector.call('collector_list_actions', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_ack_action(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        if self.options.author is not None:
            opts['author'] = self.options.author
        if self.options.comment is not None:
            opts['comment'] = self.options.comment
        if self.options.id == 0:
            raise ex.excError("--id is not set")
        else:
            opts['id'] = self.options.id

        d = self.collector.call('collector_ack_action', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

    def collector_status(self):
        d = self._collector_status()
        print_table(d, table=self.options.table)

    def collector_json_status(self):
        d = self._collector_status()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_status(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_status', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_networks(self, table=True):
        d = self._collector_networks()
        print_table(d, table=self.options.table)

    def collector_json_networks(self):
        d = self._collector_networks()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_networks(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_networks', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_asset(self, table=True):
        d = self._collector_asset()
        print_table(d, table=self.options.table)

    def collector_json_asset(self):
        d = self._collector_asset()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_asset(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_asset', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_checks(self, table=True):
        d = self._collector_checks()
        print_table(d, table=self.options.table)

    def collector_json_checks(self):
        d = self._collector_checks()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_checks(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_checks', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_disks(self):
        d = self._collector_disks()
        print_table(d, width=64, table=self.options.table)

    def collector_json_disks(self):
        d = self._collector_disks()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_disks(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_disks', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_alerts(self):
        d = self._collector_alerts()
        print_table(d, width=30, table=self.options.table)

    def collector_json_alerts(self):
        d = self._collector_alerts()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_alerts(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_alerts', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_events(self):
        d = self._collector_events()
        print_table(d, width=50, table=self.options.table)

    def collector_json_events(self):
        d = self._collector_events()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_events(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        if self.options.begin is not None:
            opts['begin'] = self.options.begin
        if self.options.end is not None:
            opts['end'] = self.options.end
        d = self.collector.call('collector_events', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_show_actions(self):
        d = self._collector_show_actions()
        print_table(d, width=50, table=self.options.table)

    def collector_json_show_actions(self):
        d = self._collector_show_actions()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(self.expand_list(d), indent=4, separators=(',', ': '))))

    def _collector_show_actions(self):
        opts = {}
        if self.svcname is not None:
            opts['svcname'] = self.svcname
        if self.options.id != 0:
            opts['id'] = self.options.id
        if self.options.begin is not None:
            opts['begin'] = self.options.begin
        if self.options.end is not None:
            opts['end'] = self.options.end
        d = self.collector.call('collector_show_actions', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

        return d['data']

    def collector_untag(self):
        opts = {}
        opts['tag_name'] = self.options.tag
        if self.svcname:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_untag', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

    def collector_tag(self):
        opts = {}
        opts['tag_name'] = self.options.tag
        if self.svcname:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_tag', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

    def collector_create_tag(self):
        opts = {}
        opts['tag_name'] = self.options.tag
        if self.svcname:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_create_tag', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])

    def collector_list_tags(self):
        d = self._collector_list_tags()
        for tag in d:
            print(tag)

    def _collector_list_tags(self):
        opts = {'pattern': self.options.like}
        if self.svcname:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_list_tags', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])
        return d['data']

    def collector_show_tags(self):
        try:
            d = self._collector_show_tags()
        except ex.excError as e:
            print(e, file=sys.stderr)
            return
        for tag in d:
            print(tag)

    def _collector_show_tags(self):
        opts = {}
        if self.svcname:
            opts['svcname'] = self.svcname
        d = self.collector.call('collector_show_tags', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])
        return d['data']

    def collector_list_nodes(self):
        d = self._collector_list_nodes()
        for node in d:
            print(node)

    def collector_json_list_nodes(self):
        d = self._collector_list_nodes()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(d, indent=4, separators=(',', ': '))))

    def _collector_list_nodes(self):
        opts = {'fset': self.options.filterset}
        d = self.collector.call('collector_list_nodes', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])
        return d['data']

    def collector_list_services(self):
        d = self._collector_list_services()
        for service in d:
            print(service)

    def collector_json_list_services(self):
        d = self._collector_list_services()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(d, indent=4, separators=(',', ': '))))

    def _collector_list_services(self):
        opts = {'fset': self.options.filterset}
        d = self.collector.call('collector_list_services', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])
        return d['data']

    def collector_list_filtersets(self):
        d = self._collector_list_filtersets()
        for fset in d:
            print(fset)

    def collector_json_list_filtersets(self):
        d = self._collector_list_filtersets()
        import json
        from rcColor import colorize_json
        print(colorize_json(json.dumps(d, indent=4, separators=(',', ': '))))

    def _collector_list_filtersets(self):
        opts = {'fset': self.options.filterset}
        d = self.collector.call('collector_list_filtersets', opts)
        if d is None:
            raise ex.excError("xmlrpc unknown failure")
        if d['ret'] != 0:
            raise ex.excError(d['msg'])
        return d['data']

