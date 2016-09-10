# -*- coding: utf-8 -*-

import os

from helpers import ETC_SYSTEMD_SYSTEM

if not os.path.exists(ETC_SYSTEMD_SYSTEM):
    raise RuntimeError("systemd not installed")
