# -*- coding: utf-8 -*-

from setuptools import Command
import logging

from .helpers import SystemdSetupHelper

__author__ = 'Eric Pascual'


class InstallSystemdUnit(Command):
    description = "install a systemd unit, using the descriptor stored as package data"
    user_options = [
        ('pkg-name=', None, 'the name of the package containing the unit description as a resource'),
        ('unit-name=', None, 'the name of the unit descriptor file (should be in the pkg_data subdir of the package)'),
    ]

    unit_name = ''
    pkg_name = ''

    before_start = None

    def initialize_options(self):
        self.unit_name = ''
        self.pkg_name = ''

    def finalize_options(self):
        if not self.pkg_name:
            raise Exception('--pkg-name option is mandatory')
        if not self.unit_name:
            raise Exception('--unit-name option is mandatory')

    def run(self):
        try:
            if not SystemdSetupHelper(self.unit_name, self.pkg_name, before_start=self.before_start).install_unit():
                self.announce('already installed', level=logging.WARNING)
        except RuntimeError as e:
            self.announce(str(e), level=logging.ERROR)


class RemoveSystemdUnit(Command):
    description = "remove an installed systemd unit"
    user_options = [
        ('pkg-name=', None, 'the name of the package containing the unit description as a resource'),
        ('unit-name=', None, 'the name of the unit descriptor file'),
    ]

    unit_name = ''
    pkg_name = ''

    after_stop = None

    def initialize_options(self):
        self.unit_name = ''
        self.pkg_name = ''

    def finalize_options(self):
        if not self.pkg_name:
            raise Exception('--pkg-name option is mandatory')
        if not self.unit_name:
            raise Exception('--unit-name option is mandatory')

    def run(self):
        try:
            if not SystemdSetupHelper(self.unit_name, self.pkg_name, after_stop=self.after_stop).remove_unit():
                self.announce('not installed', level=logging.WARNING)
        except RuntimeError as e:
            self.announce(str(e), level=logging.ERROR)
