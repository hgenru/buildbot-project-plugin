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

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


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

    def load_projects_from_path(self):
        projects_f = glob.iglob(
            (os.path.sep).join((self.path, "*", self.file_math)))
        convert = lambda s: "_".join(s.replace(".", "_").split("/")[-2:])
        return [imp.load_source(convert(m), m) for m in projects_f]

    def add_project_to_config(self):
        def add(project):
            to_add = ["slaves",
                      "status",
                      "builders",
                      "schedulers",
                      "change_source"]
            (self.config[x].append(project[x])
             for x in to_add if project.get(x, None))

        projects = ProjectFactory.__inheritors__
        (add(p) for p in projects)
