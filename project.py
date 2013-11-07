import os
import gc
import imp
import glob
from buildbot.util import safeTranslate
from buildbot.changes.filter import ChangeFilter


class Project(object):
    """Project Factory
    """
    def __init__(self, name):
        self.name = name

    def __getitem__(self, attr):
        return getattr(self, str(attr))

    def __setitem__(self, attr, value):
        self.__setattr__(attr, value)

    def get(self, key, unless=None):
        # Not to obstruct descriptor
        return self.__dict__.get(key, unless)

    @classmethod
    def get_instances(cls):
        objects = []
        for obj in gc.get_objects():
            if isinstance(obj, cls):
                objects.append(obj)
        return objects

    def gen_name(self, *strings):
        """Returns the generated name based on the give strings
        """
        strings = (self.name,) + strings  # To make it clear exactly
        return safeTranslate("_".join(strings))

    def get_change_filter(self, *args, **kwargs):
        p_filter = ChangeFilter(
            *args,
            projects=safeTranslate(self.name),
            **kwargs)
        return p_filter


class ProjectLoader(object):
    """Load projects from directory
    """
    def __init__(self,
                 conf,
                 path="projects",
                 file_math="*.py"):
        self.conf = conf
        self.path = path
        self.file_math = file_math
        self.loaded_projects = self.load_projects_from_path()
        self.add_projects_to_config()

    def load_projects_from_path(self):
        projects_f = glob.iglob(
            (os.path.sep).join((self.path, "*", self.file_math)))
        convert = lambda s: "_".join(s.replace(".", "_").split("/")[-2:])
        return [imp.load_source(convert(m), m) for m in projects_f]

    def add_projects_to_config(self):
        def _mod_builders(project):
            for builder in project["builders"]:
                builddir_name = safeTranslate(
                    project["name"]) + builder.name
                builder.builddir = os.path.join(
                    "build_data", builddir_name)
        props = {
            "slaves": None,
            "status": None,
            "builders": _mod_builders,
            "schedulers": None,
            "change_source": None
        }

        projects = Project.get_instances()
        for project in projects:
            for prop in props.iterkeys():
                if project.get(prop, None):
                    if not (prop in self.conf):
                        self.conf[prop] = []
                    if props[prop]:
                        props[prop](project)
                    self.conf[prop] += project[prop]
