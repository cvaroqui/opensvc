from __future__ import print_function
from stat import *
import os
import sys
import re
import datetime
import json
import rcExceptions as ex
from rcGlobalEnv import rcEnv
from rcUtilities import is_exe, justcall, banner, is_string
from subprocess import *
from rcPrintTable import print_table
from rcStatus import color, _colorize
from rcScheduler import scheduler_fork

comp_dir = os.path.join(rcEnv.pathvar, 'compliance')

# ex: \x1b[37;44m\x1b[1mContact List\x1b[0m\n
regex = re.compile("\x1b\[([0-9]{1,3}(;[0-9]{1,3})*)?[m|K|G]", re.UNICODE)

class Module(object):
    pattern = '^S*[0-9]+-*%(name)s$'

    def __init__(self, name, autofix=False, moduleset=None):
        self.name = name
        self.moduleset = moduleset
        self.executable = None
        self.autofix = autofix
        self.python_link_d = os.path.dirname(sys.executable)

        dl = os.listdir(comp_dir)
        match = []
        for e in dl:
            if re.match(self.pattern%dict(name=name), e) is not None:
                match.append(e)
        if len(match) == 0:
            raise ex.excInitError('module %s not found in %s'%(name, comp_dir))
        if len(match) > 1:
            raise ex.excError('module %s matches too many entries in %s'%(name,
                              comp_dir))
        base = match[0]
        if base[0] == 'S':
            base == base[1:]
        for i, c in enumerate(base):
            if not c.isdigit():
               break
        self.ordering = int(base[0:i])
        regex2 = re.compile("^S*[0-9]+-*", re.UNICODE)
        self.name = regex2.sub("", match[0])

        locations = []
        locations.append(os.path.join(comp_dir, match[0]))
        locations.append(os.path.join(locations[0], 'main'))
        locations.append(os.path.join(locations[0], 'scripts', 'main'))

        for loc in locations:
            if not os.path.exists(loc):
                continue
            statinfo = os.stat(loc)
            mode = statinfo[ST_MODE]
            if statinfo.st_uid != 0 or statinfo.st_gid not in (0,2,3,4):
                raise ex.excError('%s is not owned by root. security hazard.'%(loc))
            if not S_ISREG(mode):
                continue
            if not is_exe(loc):
                mode |= S_IXUSR
                os.chmod(loc, mode)
            self.executable = loc
        if self.executable is None:
            raise ex.excError('executable not found for module %s'%(name))

    def __str__(self):
        a = []
        a.append("name: %s"%self.name)
        a.append("ordering: %d"%self.ordering)
        a.append("executable: %s"%self.executable)
        return '\n'.join(a)


    def strip_unprintable(self, s):
        return regex.sub('', s).decode('utf8', 'ignore')

    def log_action(self, out, ret, action):
        vals = [rcEnv.nodename,
                self.name,
                str(ret),
                self.strip_unprintable(out),
                action,
                self.rset_md5]
        if self.svcname is not None:
            vals.append(self.svcname)
        else:
            vals.append("")
        self.context.action_log_vals.append(vals)

    def set_python_link_dir_in_path(self):
        if self.python_link_d == sys.path[0]:
            return
        if "PATH" in os.environ:
            os.environ["PATH"] = self.python_link_d + ":" + os.environ["PATH"]
        else:
            os.environ["PATH"] = self.python_link_d

    def setup_env(self):
        os.environ.clear()
        os.environ.update(self.context.env_bkp)
        self.set_python_link_dir_in_path()
        for rule in self.ruleset.values():
            if (rule["filter"] != "explicit attachment via moduleset" and \
                "matching non-public contextual ruleset shown via moduleset" not in rule["filter"]) or ( \
               self.moduleset in self.context.data["modset_rset_relations"]  and \
               rule['name'] in self.context.data["modset_rset_relations"][self.moduleset]
               ):
                for var, val in rule['vars']:
                    os.environ[self.context.format_rule_var(var)] = self.context.format_rule_val(val)


    def action(self, action):
        self.print_bold(banner(self.name))

        if action not in ['check', 'fix', 'fixable', 'env']:
            print('action %s not supported')
            return 1

        if self.options.force:
            # short-circuit all pre and post action
            return self.do_action(action)

        if action == 'fix':
            if self.do_action('check') == 0:
                print('check passed, skip fix')
                return 0
            if self.do_action('fixable') not in (0, 2):
                print('not fixable, skip fix')
                return 1
            self.do_action('fix')
            r = self.do_action('check')
        elif action == 'check':
            r = self.do_action('check')
            if r == 1:
                self.do_action('fixable')
        elif action == 'fixable':
            r = self.do_action('fixable')
        elif action == 'env':
            r = self.do_env()
        return r

    def do_env(self):
        a = []
        self.setup_env()
        for var in sorted(os.environ):
            val = os.environ[var]
            a.append('%s=%s'%(var, val))
        print('\n'.join(a))
        return 0

    def do_action(self, action):
        start = datetime.datetime.now()
        cmd = [self.executable, action]
        log = ''
        self.print_bold("ACTION:   %s"%action)
        print("START:    %s"%str(start))
        print("COMMAND:  %s"%' '.join(cmd))
        print("LOG:")

        import tempfile
        import time
        fo = tempfile.NamedTemporaryFile()
        fe = tempfile.NamedTemporaryFile()
        _fo = None
        _fe = None

        def poll_out():
            fop = _fo.tell()
            line = _fo.readline()
            if not line:
                _fo.seek(fop)
                return None
            sys.stdout.write(line)
            sys.stdout.flush()
            return line

        def poll_err():
            fep = _fe.tell()
            line = _fe.readline()
            if not line:
                _fe.seek(fep)
                return None
            _line = color.RED + 'ERR: ' + color.END + line
            line = 'ERR: '+line
            sys.stdout.write(_line)
            sys.stdout.flush()
            return line

        def poll_pipes(log):
            i = 0
            while True:
                o = poll_out()
                e = poll_err()
                if o is not None:
                    log += o
                if e is not None:
                    log += e
                if o is None and e is None:
                    break
            return log

        try:
            self.setup_env()
            p = Popen(cmd, stdout=fo, stderr=fe, env=os.environ)
            _fo = open(fo.name, 'r')
            _fe = open(fe.name, 'r')
            while True:
                time.sleep(0.1)
                log = poll_pipes(log)
                if p.poll() != None:
                    log = poll_pipes(log)
                    break
        except OSError as e:
            if _fo is not None:
                _fo.close()
            if _fe is not None:
                _fe.close()
            fo.close()
            fe.close()
            if e.errno == 2:
                raise ex.excError("%s execution error (File not found or bad interpreter)"%self.executable)
            elif e.errno == 8:
                raise ex.excError("%s execution error (Exec format error)"%self.executable)
            else:
                raise
        fo.close()
        fe.close()
        _fo.close()
        _fe.close()
        end = datetime.datetime.now()
        self.print_rcode(p.returncode)
        print("DURATION: %s"%str(end-start))
        self.log_action(log, p.returncode, action)
        return p.returncode

    def print_bold(self, s):
        print(_colorize(s, color.BOLD))

    def print_rcode(self, r):
        if r == 1:
            print(_colorize("RCODE:    %d"%r, color.RED))
        elif r == 0:
            print(_colorize("RCODE:    %d"%r, color.GREEN))
        else:
            print("RCODE:    %d"%r)

    def env(self):
        return self.action('env')

    def check(self):
        return self.action('check')

    def fix(self):
        return self.action('fix')

    def fixable(self):
        return self.action('fixable')

class Compliance(object):
    def __init__(self, skip_action=None, options=None, collector=None, svcname=None):
        self.skip_action = skip_action
        self.options = options
        self.collector = collector
        self.svcname = svcname
        self.options = options
        self.module_o = {}
        self.module = []
        self.updatecomp = False
        self.moduleset = None
        self.data = None
        self.action_log_vals = []
        self.action_log_vars = [
          'run_nodename',
          'run_module',
          'run_status',
          'run_log',
          'run_action',
          'rset_md5',
          'run_svcname']
        self.env_bkp = os.environ.copy()

    def set_rset_md5(self):
        self.rset_md5 = ""
        rs = self.ruleset.get("osvc_collector")
        if rs is None:
            return
        for var, val in rs["vars"]:
            if var == "ruleset_md5":
                self.rset_md5 = val
                break

    def setup_env(self):
        for rule in self.ruleset.values():
            for var, val in rule['vars']:
                os.environ[self.format_rule_var(var)] = self.format_rule_val(val)

    def reset_env(self):
        os.environ.clear()
        os.environ.update(self.env_bkp)

    def compliance_auto(self):
        if self.skip_action is not None and \
           self.skip_action("compliance_auto"):
            return
        self.task_compliance_auto()

    @scheduler_fork
    def task_compliance_auto(self):
        if self.updatecomp:
            self.node.updatecomp()
        self.do_auto()

    def compliance_env(self):
        self.do_run('env')

    def compliance_check(self):
        self.do_checks()

    def __iadd__(self, o):
        self.module_o[o.name] = o
        o.svcname = self.svcname
        o.ruleset = self.ruleset
        o.options = self.options
        o.collector = self.collector
        o.context = self
        o.rset_md5 = self.rset_md5
        return self

    def print_bold(self, s):
        print(_colorize(s, color.BOLD))

    def expand_modulesets(self, modulesets):
        l = []

        def recurse(ms):
            l.append(ms)
            if ms not in self.data["modset_relations"]:
                return
            for _ms in self.data["modset_relations"][ms]:
                recurse(_ms)

        for ms in modulesets:
            recurse(ms)

        return l

    def init(self):
        if self.options.moduleset != "" and self.options.module != "":
            raise ex.excError('--moduleset and --module are exclusive')

        if self.data is None:
            try:
                self.data = self.get_comp_data()
            except Exception as e:
                raise ex.excError(str(e))
            if self.data is None:
                raise ex.excError("could not fetch compliance data from the collector")
            if "ret" in self.data and self.data["ret"] == 1:
                if "msg" in self.data:
                    raise ex.excError(self.data["msg"])
                raise ex.excError("could not fetch compliance data from the collector")
            modulesets = []
            if self.options.moduleset != "":
                # purge unspecified modulesets
                modulesets = self.options.moduleset.split(',')
                modulesets = self.expand_modulesets(modulesets)
                for ms in self.data["modulesets"].keys():
                    if ms not in modulesets:
                        del(self.data["modulesets"][ms])
            elif self.options.module != "":
                # purge unspecified modules
                modules = self.options.module.split(',')
                for ms, data in self.data["modulesets"].items():
                    n = len(data)
                    for i in sorted(range(n), reverse=True):
                        module, autofix = data[i]
                        if module not in modules:
                            del(self.data["modulesets"][ms][i])
                for module in modules:
                    in_modsets = []
                    for ms, data in self.data["modulesets"].items():
                        for _module, autofix in data:
                            if module == _module:
                               in_modsets.append(ms)
                    if len(in_modsets) == 0:
                        print("module %s not found in any attached moduleset" % module)
                    elif len(in_modsets) > 1:
                        raise ex.excError("module %s found in multiple attached moduleset (%s). Use --moduleset instead of --module to clear the ambiguity" % (module, ', '.join(in_modsets)))

            if len(modulesets) > 0 and \
               hasattr(self.options, "attach") and self.options.attach:
                self._compliance_attach_moduleset(modulesets)

        self.module = self.merge_moduleset_modules()
        self.ruleset = self.data['rulesets']
        self.set_rset_md5()

        if not os.path.exists(comp_dir):
            os.makedirs(comp_dir, 0o755)

        for module, autofix, moduleset in self.module:
            try:
                self += Module(module, autofix, moduleset)
            except ex.excInitError as e:
                print(e, file=sys.stderr)

        self.ordered_module = self.module_o.keys()
        self.ordered_module.sort(lambda x, y: cmp(self.module_o[x].ordering,
                                                  self.module_o[y].ordering))

    def __str__(self):
        print(banner('run context'))
        a = []
        a.append('modules:')
        for m in self.ordered_module:
            a.append(' %0.2d %s'%(self.module_o[m].ordering, m))
        a.append(self.str_ruleset())
        return '\n'.join(a)

    def format_rule_var(self, var):
        var = var.upper().replace('-', '_').replace(' ', '_').replace('.','_')
        var = '_'.join(('OSVC_COMP', var))
        return var

    def format_rule_val(self, val):
        if is_string(val):
            try:
                tmp = json.loads(val)
                val = json.dumps(tmp)
            except Exception as e:
                pass
        else:
            val = str(val)
        return val

    def get_moduleset(self):
        if self.svcname is not None:
            moduleset = self.collector.call('comp_get_svc_data_moduleset', self.svcname)
        else:
            moduleset = self.collector.call('comp_get_data_moduleset')
        if moduleset is None:
            raise ex.excError('could not fetch moduleset')
        return moduleset

    def get_ruleset(self):
        if hasattr(self.options, 'ruleset') and \
           len(self.options.ruleset) > 0:
            return self.get_ruleset_md5(self.options.ruleset)
        return self.get_current_ruleset()

    def get_current_ruleset(self):
        if self.svcname is not None:
            ruleset = self.collector.call('comp_get_svc_ruleset', self.svcname)
        else:
            ruleset = self.collector.call('comp_get_ruleset')
        if ruleset is None:
            raise ex.excError('could not fetch ruleset')
        return ruleset

    def get_ruleset_md5(self, rset_md5):
        ruleset = self.collector.call('comp_get_ruleset_md5', rset_md5)
        if ruleset is None:
            raise ex.excError('could not fetch ruleset')
        return ruleset

    def str_ruleset(self):
        a = []
        a.append('rules:')
        for rule in self.ruleset.values():
            if len(rule['filter']) == 0:
                a.append(' %s'%rule['name'])
            else:
                a.append(' %s (%s)'%(rule['name'],rule['filter']))
            for var, val in rule['vars']:
                val = self.format_rule_val(val)
                if ' ' in val:
                    val = repr(val)
                a.append('  %s=%s'%(self.format_rule_var(var), val))
        return '\n'.join(a)

    def get_comp_data(self, modulesets=[]):
        if self.svcname is not None:
            return self.collector.call('comp_get_svc_data', self.svcname, modulesets)
        else:
            return self.collector.call('comp_get_data', modulesets)

    def merge_moduleset_modules(self):
        l = []
        for ms, data in self.data['modulesets'].items():
            for module, autofix in data:
                if (module, autofix) not in l:
                    l.append((module, autofix, ms))
                elif autofix and (module, False, ms) in l:
                    l.remove((module, False, ms))
                    l.append((module, True, ms))
        return l

    def digest_errors(self, err):
        passed = [m for m in err if err[m] == 0]
        errors = [m for m in err if err[m] == 1]
        na = [m for m in err if err[m] == 2]

        n_passed = len(passed)
        n_errors = len(errors)
        n_na = len(na)

        def _s(n):
            if n > 1:
                return 's'
            else:
                return ''

        def modules(l):
            if len(l) == 0:
                return ''
            return '\n%s'%'\n'.join(map(lambda x: ' '+x, l))

        self.print_bold(banner("digest"))
        print("%d n/a%s"%(n_na, modules(na)))
        print("%d passed%s"%(n_passed, modules(passed)))
        print("%d error%s%s"%(n_errors, _s(n_errors), modules(errors)))

        if len(errors) > 0:
            return 1
        return 0

    def compliance_show_moduleset(self):
        def recurse(ms, depth=0):
            prefix=" "*depth
            print(prefix+ms+':')
            if ms not in data["modulesets"]:
                print(prefix+" (no modules)")
                return
            for module, autofix in data["modulesets"][ms]:
                if autofix:
                    s = " (autofix)"
                else:
                    s = ""
                print(prefix+' %s%s' % (module, s))
            if ms in data["modset_relations"]:
                for _ms in data["modset_relations"][ms]:
                    recurse(_ms, depth+1)

        try:
            data = self.get_moduleset()
        except Exception as e:
            print(e, file=sys.stderr)
            return 1
        if "ret" in data and data["ret"] == 1:
            if "msg" in data:
                print(data["msg"], file=sys.stderr)
            return 1
        if "root_modulesets" not in data:
            print("(none)")
            return 0
        for ms in data["root_modulesets"]:
            recurse(ms)

    def compliance_show_ruleset(self):
        self.ruleset = self.get_ruleset()
        print(self.str_ruleset())

    def do_run(self, action):
        err = {}
        self.init()
        start = datetime.datetime.now()
        for module in self.ordered_module:
            _action = action
            if action == "auto":
                if self.module_o[module].autofix:
                    _action = "fix"
                else:
                    _action = "check"
            err[module] = getattr(self.module_o[module], _action)()
        if action == "env":
            return 0
        r = self.digest_errors(err)
        end = datetime.datetime.now()
        print("total duration: %s"%str(end-start))
        self.collector.call('comp_log_actions', self.action_log_vars, self.action_log_vals)
        return r

    def do_auto(self):
        return self.do_run('auto')

    def do_checks(self):
        return self.do_run('check')

    def compliance_fix(self):
        return self.do_run('fix')

    def compliance_fixable(self):
        return self.do_run('fixable')

    def compliance_detach(self):
        did_something = False
        if hasattr(self.options, 'moduleset') and \
           len(self.options.moduleset) > 0:
            did_something = True
            self._compliance_detach_moduleset(self.options.moduleset.split(','))
        if hasattr(self.options, 'ruleset') and \
           len(self.options.ruleset) > 0:
            did_something = True
            self._compliance_detach_ruleset(self.options.ruleset.split(','))
        if not did_something:
            raise ex.excError('no moduleset nor ruleset specified. use --moduleset and/or --ruleset')

    def compliance_attach(self):
        did_something = False
        if hasattr(self.options, 'moduleset') and \
           len(self.options.moduleset) > 0:
            did_something = True
            self._compliance_attach_moduleset(self.options.moduleset.split(','))
        if hasattr(self.options, 'ruleset') and \
           len(self.options.ruleset) > 0:
            did_something = True
            self._compliance_attach_ruleset(self.options.ruleset.split(','))
        if not did_something:
            raise ex.excError('no moduleset nor ruleset specified. use --moduleset and/or --ruleset')

    def compliance_attach_moduleset(self):
        if not hasattr(self.options, 'moduleset') or \
           len(self.options.moduleset) == 0:
            raise ex.excError('no moduleset specified. use --moduleset')
        self._compliance_attach_moduleset(self.options.moduleset.split(','))

    def _compliance_attach_moduleset(self, modulesets):
        err = False
        for moduleset in modulesets:
            if self.svcname is not None:
                d = self.collector.call('comp_attach_svc_moduleset', self.svcname, moduleset)
            else:
                d = self.collector.call('comp_attach_moduleset', moduleset)
            if d is None:
                print("Failed to attach '%s' moduleset. The collector may not be reachable." % moduleset, file=sys.stderr)
                err = True
                continue
            if not d['status']:
                err = True
            print(d['msg'])
        if err:
            raise ex.excError()

    def compliance_detach_moduleset(self):
        if not hasattr(self.options, 'moduleset') or \
           len(self.options.moduleset) == 0:
            raise ex.excError('no moduleset specified. use --moduleset')
        self._compliance_detach_moduleset(self.options.moduleset.split(','))

    def _compliance_detach_moduleset(self, modulesets):
        err = False
        for moduleset in modulesets:
            if self.svcname is not None:
                d = self.collector.call('comp_detach_svc_moduleset', self.svcname, moduleset)
            else:
                d = self.collector.call('comp_detach_moduleset', moduleset)
            if d is None:
                print("Failed to detach '%s' moduleset. The collector may not be reachable." % moduleset, file=sys.stderr)
                err = True
                continue
            if not d['status']:
                err = True
            print(d['msg'])
        if err:
            raise ex.excError()

    def compliance_attach_ruleset(self):
        if not hasattr(self.options, 'ruleset') or \
           len(self.options.ruleset) == 0:
            raise ex.excError('no ruleset specified. use --ruleset')
        self._compliance_attach_ruleset(self.options.ruleset.split(','))

    def _compliance_attach_ruleset(self, rulesets):
        err = False
        for ruleset in rulesets:
            if self.svcname is not None:
                d = self.collector.call('comp_attach_svc_ruleset', self.svcname, ruleset)
            else:
                d = self.collector.call('comp_attach_ruleset', ruleset)
            if d is None:
                print("Failed to attach '%s' ruleset. The collector may not be reachable." % ruleset, file=sys.stderr)
                err = True
                continue
            if not d['status']:
                err = True
            print(d['msg'])
        if err:
            raise ex.excError()

    def compliance_detach_ruleset(self):
        if not hasattr(self.options, 'ruleset') or \
           len(self.options.ruleset) == 0:
            raise ex.excError('no ruleset specified. use --ruleset')
        self._compliance_detach_ruleset(self.options.ruleset.split(','))

    def _compliance_detach_ruleset(self, rulesets):
        err = False
        for ruleset in rulesets:
            if self.svcname is not None:
                d = self.collector.call('comp_detach_svc_ruleset', self.svcname, ruleset)
            else:
                d = self.collector.call('comp_detach_ruleset', ruleset)
            if d is None:
                print("Failed to detach '%s' ruleset. The collector may not be reachable." % ruleset, file=sys.stderr)
                err = True
                continue
            if not d['status']:
                err = True
            print(d['msg'])
        if err:
            raise ex.excError()

    def compliance_show_status(self):
        args = ['comp_show_status']
        if self.svcname is None:
           args.append('')
        else:
           args.append(self.svcname)
        if hasattr(self.options, 'module') and \
           len(self.options.module) > 0:
            args.append(self.options.module)
        l = self.collector.call(*args)
        if l is None:
            return
        print_table(l, width=50, table=self.options.table)

    def compliance_list_ruleset(self):
        if not hasattr(self.options, 'ruleset') or \
           len(self.options.ruleset) == 0:
            l = self.collector.call('comp_list_ruleset')
        else:
            l = self.collector.call('comp_list_ruleset', self.options.ruleset)
        if l is None:
            return
        print('\n'.join(l))

    def compliance_list_moduleset(self):
        if not hasattr(self.options, 'moduleset') or \
           len(self.options.moduleset) == 0:
            l = self.collector.call('comp_list_moduleset')
        else:
            l = self.collector.call('comp_list_moduleset', self.options.moduleset)
        if l is None:
            return
        print('\n'.join(l))

    def compliance_list_module(self):
        import glob
        regex2 = re.compile("^S*[0-9]+-*", re.UNICODE)
        for path in glob.glob(os.path.join(comp_dir, '*')):
            name = regex2.sub("", os.path.basename(path))
            try:
                m = Module(name)
                print(m.name)
            except:
                continue


