import os
import gc
import imp
import glob


class Project(object):
    """Project Factory
    """
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

        projects = Project.get_instances()
        for p in projects:
            add(p)


def get_builddir_path(
        file_path,
        builddir,
        data_dir_name="data"):
    """Gives an absolute path relative
       to the project configuration file
    """
    path = os.path.relpath(os.path.join(
        os.path.dirname(file_path), data_dir_name, builddir))
    return path
