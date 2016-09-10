# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

import pkg_resources

__author__ = 'Eric Pascual'

ETC_SYSTEMD_SYSTEM = '/etc/systemd/system/'


class SystemdSetupHelper(object):
    def __init__(self, svc_name, setup_pkg_name):
        if not svc_name or not setup_pkg_name:
            raise ValueError('missing mandatory parameter')

        self._svc_name = svc_name
        self._svc_file_name = svc_name + '.service'
        self._setup_pkg_name = setup_pkg_name

    @staticmethod
    def _check_if_root():
        if not os.getuid() == 0:
            raise RuntimeError('must be root')

    def install_service(self):
        self._check_if_root()

        if os.path.exists(os.path.join(ETC_SYSTEMD_SYSTEM, self._svc_file_name)):
            return False

        # copy the service descriptor file in the configuration directory
        fn = pkg_resources.resource_filename(self._setup_pkg_name, 'pkg_data/%s') % self._svc_file_name
        shutil.copy(fn, ETC_SYSTEMD_SYSTEM)
        # make systemd be aware of changes
        subprocess.check_output(['systemctl', '-q', 'daemon-reload'])
        # enable the service at system start
        subprocess.check_output(['systemctl', '-q', 'enable', self._svc_name])
        # start it now
        subprocess.check_output(['systemctl', '-q', 'start', self._svc_name])

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

        # remove it
        subprocess.check_output(['systemctl', 'disable', self._svc_name])
        os.remove(os.path.join(ETC_SYSTEMD_SYSTEM, self._svc_file_name))

        # make systemd be aware of changes
        subprocess.check_output('systemctl daemon-reload'.split())

        return True


def install_service(svc_name, pkg):
    try:
        if not SystemdSetupHelper(svc_name, pkg).install_service():
            print("already installed")
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)


def remove_service(svc_name, pkg):
    try:
        if not SystemdSetupHelper(svc_name, pkg).remove_service():
            print("not installed")
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)
