# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

import pkg_resources

__author__ = 'Eric Pascual'

ETC_SYSTEMD_SYSTEM = '/etc/systemd/system/'


class SystemdSetupHelper(object):
    def __init__(self, unit_name, setup_pkg_name, before_start=None, after_stop=None):
        if not unit_name or not setup_pkg_name:
            raise ValueError('missing mandatory parameter')

        self._unit_name = unit_name

        # default to service if the unit name is not fully qualified
        if unit_name.split('.')[-1] not in (
                'service', 'socket', 'target', 'mount', 'device', 'automount',
                'swap', 'path', 'timer', 'slice', 'scope'
        ):
            self._unit_file_name = unit_name + '.service'
        else:
            self._unit_file_name = unit_name

        self._setup_pkg_name = setup_pkg_name

        if before_start and not callable(before_start):
            raise ValueError('before_start must be a callable')
        self._before_start = before_start

        if after_stop and not callable(after_stop):
            raise ValueError('after_stop must be a callable')
        self._after_stop = after_stop

    @staticmethod
    def _check_if_root():
        if not os.getuid() == 0:
            raise RuntimeError('must be root')

    def install_unit(self):
        self._check_if_root()

        # copy the service descriptor file in the configuration directory
        fn = pkg_resources.resource_filename(self._setup_pkg_name, 'pkg_data/%s') % self._unit_file_name
        shutil.copy(fn, ETC_SYSTEMD_SYSTEM)
        # make systemd be aware of changes
        subprocess.check_output(['systemctl', 'daemon-reload'])
        # enable the service at system start
        subprocess.check_output(['systemctl', 'enable', self._unit_name])
        # (re)start it now
        if self._before_start:
            self._before_start()
        subprocess.check_output(['systemctl', 'restart', self._unit_name])

        return True

    def remove_unit(self):
        self._check_if_root()

        if not os.path.exists(os.path.join(ETC_SYSTEMD_SYSTEM, self._unit_file_name)):
            return False

        # stop the service if currently running
        try:
            subprocess.check_output(['systemctl', '-q', 'is-active', self._unit_name])
        except subprocess.CalledProcessError:
            pass
        else:
            subprocess.check_output(['systemctl', 'stop', self._unit_name])
            if self._after_stop:
                self._after_stop()

        # remove it from system start
        subprocess.check_output(['systemctl', 'disable', self._unit_name])
        os.remove(os.path.join(ETC_SYSTEMD_SYSTEM, self._unit_file_name))

        # make systemd be aware of changes
        subprocess.check_output(['systemctl', 'daemon-reload'])

        return True


def install_unit(unit_name, pkg, before_start=None):
    try:
        if not SystemdSetupHelper(unit_name, pkg, before_start=before_start).install_unit():
            print("already installed")
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)

install_service = install_unit      #: for backward compatibility


def remove_unit(unit_name, pkg, after_stop=None):
    try:
        if not SystemdSetupHelper(unit_name, pkg, after_stop=after_stop).remove_unit():
            print("not installed")
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)

remove_service = remove_unit        #: for backward compatibility
