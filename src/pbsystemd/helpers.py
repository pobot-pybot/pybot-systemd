# -*- coding: utf-8 -*-

import os
import subprocess
import shutil

import pkg_resources

__author__ = 'Eric Pascual'

LIB_SYSTEMD_SYSTEM = '/lib/systemd/system/'


class SystemdSetupHelper(object):
    def __init__(self, svc_name):
        if not svc_name:
            raise ValueError('missing mandatory parameter')

        self._svc_name = svc_name
        self._svc_file_name = svc_name + '.service'

    @staticmethod
    def _check_if_root():
        if not os.getuid() == 0:
            raise RuntimeError('must be root')

    def install_service(self):
        self._check_if_root()

        if subprocess.call(['systemctl', '-q', 'is-enabled', self._svc_name]) == 0:
            return False

        # copy the service descriptor file in the blessed directory (/lib/systemd/system)
        fn = pkg_resources.resource_filename('nros.core.setup', 'pkg_data/%s') % self._svc_file_name
        shutil.copy(fn, LIB_SYSTEMD_SYSTEM)
        # make systemd be aware of changes
        subprocess.check_output(['systemctl', '-q', 'daemon-reload'])
        # enable the service at system start
        subprocess.check_output(['systemctl', '-q', 'enable', self._svc_name])
        # start it now
        subprocess.check_output(['systemctl', '-q', 'start', self._svc_name])

        return True

    def remove_service(self):
        self._check_if_root()

        try:
            subprocess.check_output(['systemctl', '-q', 'is-enabled', self._svc_name])
        except subprocess.CalledProcessError:
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
        os.remove(os.path.join(LIB_SYSTEMD_SYSTEM, self._svc_file_name))

        # make systemd be aware of changes
        subprocess.check_output('systemctl daemon-reload'.split())

        return True
