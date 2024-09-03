from .. import \
    KEYWORDS as BASE_KEYWORDS, \
    BaseTask
from drivers.resource.container.docker import \
    KEYWORDS as DOCKER_KEYWORDS, \
    ContainerDocker
import core.exceptions as ex

from core.objects.svcdict import KEYS
from utilities.subsystems.docker import has_docker

DRIVER_GROUP = "task"
DRIVER_BASENAME = "docker"
DRIVER_BASENAME_ALIASES = ["oci"]
KEYWORDS = BASE_KEYWORDS + [kw for kw in DOCKER_KEYWORDS if kw["keyword"] != "start_timeout"]
DEPRECATED_KEYWORDS = {
    "task.docker.run_image": "image",
    "task.docker.run_command": "command",
    "task.docker.net": "netns",
    "task.oci.run_image": "image",
    "task.oci.run_command": "command",
    "task.oci.net": "netns",
}
REVERSE_DEPRECATED_KEYWORDS = {
    "task.docker.image": "run_image",
    "task.docker.command": "run_command",
    "task.docker.netns": "net",
    "task.oci.image": "run_image",
    "task.oci.command": "run_command",
    "task.oci.netns": "net",
}

KEYS.register_driver(
    DRIVER_GROUP,
    DRIVER_BASENAME,
    name=__name__,
    keywords=KEYWORDS,
    deprecated_keywords=DEPRECATED_KEYWORDS,
    reverse_deprecated_keywords=REVERSE_DEPRECATED_KEYWORDS,
    driver_basename_aliases=DRIVER_BASENAME_ALIASES,
)

def driver_capabilities(node=None):
    data = []
    if has_docker(["docker", "docker.io"]):
        data += [
            "task.docker",
            "task.docker.registry_creds",
        ]
    return data


class TaskDocker(ContainerDocker, BaseTask):
    def __init__(self, *args, **kwargs):
        kwargs["detach"] = False
        kwargs["type"] = "task.docker"
        ContainerDocker.__init__(self, *args, **kwargs)
        BaseTask.__init__(self, *args, **kwargs)
        self.start_timeout = self.timeout

    def on_add(self):
        if self.max_parallel > 1:
            print(self.container_name)
            from utilities.lazy import set_lazy, unset_lazy
            from os import getpid
            set_lazy(self, "container_name", "%s.%d" % (self.container_name, getpid()))
            set_lazy(self, "container_label_id", "%s.%d" % (self.container_label_id, getpid()))
            unset_lazy(self, "container_id")

    _info = ContainerDocker._info

    def start(self):
        BaseTask.start(self)

    def stop(self):
        BaseTask.stop(self)

    def _run_call(self):
        try:
            ContainerDocker.start(self)
            self.write_last_run_retcode(0)
        except ex.Error:
            self.write_last_run_retcode(1)
            raise
        finally:
            if self.rm:
                self.container_rm()

    def _status(self, *args, **kwargs):
        return BaseTask._status(self, *args, **kwargs)

    def post_provision_start(self):
        pass

    def pre_provision_stop(self):
        pass

