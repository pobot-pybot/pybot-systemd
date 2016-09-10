# -*- coding: utf-8 -*-

import os

if not os.path.exists('/lib/systemd'):
    raise RuntimeError("systemd not installed")
