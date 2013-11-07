# -*- python -*-
# encoding: utf-8
# ex: set syntax=python:
# Import, import, import!
import project
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.buildslave import BuildSlave
from buildbot.schedulers.forcesched import ForceScheduler


class ExampleProject(project.Project):
    def __init__(self, *args, **kwargs):
        super(ExampleProject, self).__init__("EXP", *args, **kwargs)
        self["slaves"] = []
        self["builders"] = []

    def gen_builder(self, platform, arch, branch):
        slave_name = self.gen_name("slave", platform, arch)
        self["slaves"].append(
            BuildSlave(slave_name, "buildbot", max_builds=1))
        factory = BuildFactory()
        factory.addStep(
            Git(repourl="ssh://git.example.com",
                mode='incremental', name="clone EXPbuild",
                haltOnFailure=True))
        factory.addStep(
            ShellCommand(
                command="call C:\windowsOnly\_build_env_.bat",
                name="setup windows envs",
                doStepIf=(platform == "win")))
        factory.addStep(
            ShellCommand(
                command="build",
                name="build"))
        builder = BuilderConfig(
            name=self.gen_name("builder", platform, arch, branch),
            slavenames=[slave_name],
            factory=factory)
        self["builders"].append(builder)

    def gen_builders(self, platforms, branches):
        for platform in list(platforms.keys()):
            for arch in platforms[platform]:
                for branch in branches:
                    self.gen_builder(platform, arch, branch)


# Init project
EXP = ExampleProject()


# Generate builders
PLATFORMS = {"linux": ["x32", "x64"], "macosx": ["x64"], "win": ["x32"]}
BRANCHES = ["master", "6.0"]
EXP.gen_builders(PLATFORMS, BRANCHES)


# Sheluders
EXP['schedulers'] = []
EXP['schedulers'].append(ForceScheduler(
    name=EXP.gen_name("scheduler", "force"),
    builderNames=[b.name for b in EXP["builders"]]))
