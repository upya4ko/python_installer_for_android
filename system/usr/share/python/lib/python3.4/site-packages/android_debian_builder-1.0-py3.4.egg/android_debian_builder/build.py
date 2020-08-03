# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
# Copyright (c) 2014 Felix Krull <f_krull@gmx.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import tempfile

from jinja2 import Template

from .util import call, chroot_path


def run_multistrap(path, config):
    """Run multistrap with `config`."""
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        tmp.write(config)
        tmp.flush()
        call(["multistrap", "-d", path, "-f", tmp.name])


def import_extra_keys(path, extra_keys):
    """Import more GPG keys for apt."""
    gpg_dir = os.path.join(path, "etc", "apt", "trusted.gpg.d")
    os.makedirs(gpg_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_name:
        for key in extra_keys:
            call(["gpg", "--homedir", tmp_name,
                  "--keyserver", "hkp://keyserver.ubuntu.com",
                  "--recv-keys", key])
            call(["gpg", "--homedir", tmp_name,
                  "--keyserver", "hkp://keyserver.ubuntu.com",
                  "--output", os.path.join(gpg_dir, "%s.gpg" % key),
                  "--export", key])


def gen_script(path, template, config, mode=0o755):
    """Generate a script from a template."""
    with open(path, "w") as f:
        f.write(Template(template).render(config=config))
    os.chmod(path, mode)


def store_config(mountpoint, config):
    """Dump the build configuration into the image."""
    with open(chroot_path(mountpoint, config.embedded_config), "w") as f:
        config.dump(f)
