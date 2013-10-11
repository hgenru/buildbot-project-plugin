import os
import imp
import glob


class ProjectFactory(object):
    """Project Factory
    """
    class __metaclass__(type):
        __inheritors__ = []

        def __call__(cls, *args, **kwargs):
            obj = type.__call__(cls, *args, **kwargs)
            cls.__inheritors__.append(obj)
            return obj

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        self.__setattr__(attr, value)

    def get(self, key, unless):
        # Not to obstruct descriptor
        if key in self.__dict__:
            return getattr(self, key)
        else:
            return unless


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
        def add(project):
            to_add = ["slaves",
                      "status",
                      "builders",
                      "schedulers",
                      "change_source"]
            for x in to_add:
                if project.get(x, None):
                    if not (x in self.conf):
                        self.conf[x] = []
                    self.conf[x] += project[x]

        projects = ProjectFactory.__inheritors__
        for p in projects:
            add(p)
