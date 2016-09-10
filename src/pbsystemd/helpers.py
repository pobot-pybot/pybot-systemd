# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

import pkg_resources

__author__ = 'Eric Pascual'

ETC_SYSTEMD_SYSTEM = '/etc/systemd/system/'


class SystemdSetupHelper(object):
    def __init__(self, svc_name, setup_pkg_name, before_start=None, after_stop=None):
        if not svc_name or not setup_pkg_name:
            raise ValueError('missing mandatory parameter')

        self._svc_name = svc_name
        self._svc_file_name = svc_name + '.service'
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

    def install_service(self):
        self._check_if_root()

        # copy the service descriptor file in the configuration directory
        fn = pkg_resources.resource_filename(self._setup_pkg_name, 'pkg_data/%s') % self._svc_file_name
        shutil.copy(fn, ETC_SYSTEMD_SYSTEM)
        # make systemd be aware of changes
        subprocess.check_output(['systemctl', 'daemon-reload'])
        # enable the service at system start
        subprocess.check_output(['systemctl', 'enable', self._svc_name])
        # (re)start it now
        if self._before_start:
            self._before_start()
        subprocess.check_output(['systemctl', 'restart', self._svc_name])

        return True

    def remove_service(self):
        self._check_if_root()

        if not os.path.exists(os.path.join(ETC_SYSTEMD_SYSTEM, self._svc_file_name)):
            return False

        # stop the service if currently running
        try:
            subprocess.check_output(['systemctl', '-q', 'is-active', self._svc_name])
        except subprocess.CalledProcessError:
            pass
        else:
            subprocess.check_output(['systemctl', 'stop', self._svc_name])
            if self._after_stop:
                self._after_stop()

        # remove it from system start
        subprocess.check_output(['systemctl', 'disable', self._svc_name])
        os.remove(os.path.join(ETC_SYSTEMD_SYSTEM, self._svc_file_name))

        # make systemd be aware of changes
        subprocess.check_output(['systemctl', 'daemon-reload'])

        return True


def install_service(svc_name, pkg, before_start=None):
    try:
        if not SystemdSetupHelper(svc_name, pkg, before_start=before_start).install_service():
            print("already installed")
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)


def remove_service(svc_name, pkg, after_stop=None):
    try:
        if not SystemdSetupHelper(svc_name, pkg, after_stop=after_stop).remove_service():
            print("not installed")
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)
