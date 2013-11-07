# -*- python -*-
# encoding: utf-8
# ex: set syntax=python:
import project
from os.path import expanduser
from buildbot.config import BuilderConfig
from buildbot.buildslave import BuildSlave
from buildbot.changes.gitpoller import GitPoller
from buildbot.process.factory import BuildFactory
from buildbot.steps.master import MasterShellCommand
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.basic import SingleBranchScheduler


SU = project.Project("SimpleExampleProjext")
SU.repo_url = "git.example.com/buildbot"


# Slave
SU["slaves"] = [BuildSlave(SU.gen_name("slave"), "update_me_now")]


# Change Source
SU["change_source"] = []
SU["change_source"].append(
    GitPoller(
        SU.repo_url,
        # Use a field project to separate change source projects (>8.0)
        project=SU.gen_name(),
        workdir='.gitpoller-example', branch='master',
        pollinterval=10))


# Factory
update_factory = BuildFactory()

update_factory.addStep(
    MasterShellCommand(
        command=("build")))


# Builders
SU["builders"] = []
SU["builders"].append(
    BuilderConfig(
        name=SU.gen_name("builder"),
        slavebuilddir=expanduser("~"),
        slavenames=[SU.gen_name("slave")],
        factory=update_factory))


# Sheluders
SU['schedulers'] = []
SU['schedulers'].append(
    SingleBranchScheduler(
        name=SU.gen_name("scheduler", "auto"),
        change_filter=SU.get_change_filter(),
        treeStableTimer=None,
        builderNames=[SU.gen_name("builder")]))
SU['schedulers'].append(
    ForceScheduler(
        name=SU.gen_name("scheduler", "force"),
        builderNames=[SU.gen_name("builder")]))
