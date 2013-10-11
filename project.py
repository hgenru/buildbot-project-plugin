import os
import imp
import glob


class Modifier(object):
    """Wrapper to set project-specify
       properties to object
    """
    def __init__(self, mod_prop):
        self.mod_prop = mod_prop

    def __set__(self, obj, value):
        self.value = value

    def __get__(self, obj, objtype):
        # TODO: Rewrite this dirty hack
        return [self.mod_obj(v)
                for v in self.value]

    def mod_object(self, obj):
        obj.__dict__.update(self.mod_prop)
        return obj


class ProjectFactory(dict):
    """Project Factory
    """
    class __metaclass__(type):
        __inheritors__ = []

        def __call__(cls, *args, **kwargs):
            obj = type.__call__(cls, *args, **kwargs)
            cls.__inheritors__.append(obj)
            obj.__dict__["builders"] = Modifier(
                {"builddir": os.path.dirname(os.path.realpath(__file__))})
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
