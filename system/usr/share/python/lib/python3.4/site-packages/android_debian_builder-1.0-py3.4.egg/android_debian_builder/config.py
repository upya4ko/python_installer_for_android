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

from configparser import ConfigParser

from .util import load


class Config:
    def __init__(self, cfgpaths):
        self._parser = ConfigParser(interpolation=None)
        for path in cfgpaths:
            self._parser.read_string(load(path), path)

    def dump(self, f):
        self._parser.write(f, True)

    @property
    def image_size(self):
        return self._parser["image"]["size"]

    @property
    def image_fs(self):
        return self._parser["image"]["fs_type"]

    @property
    def multistrap_config(self):
        return self._parser["bootstrap"]["multistrap-config"]

    @property
    def extra_gpg_keys(self):
        return self._parser["bootstrap"]["extra-gpg-keys"].split()

    @property
    def embedded_config(self):
        return self._parser["bootstrap"]["embedded-config"]

    @property
    def init_script(self):
        return self._parser["bootstrap"]["init-script"]

    @property
    def init_script_template(self):
        return self._parser["bootstrap"]["init-script-template"]

    @property
    def extra_scripts(self):
        return self._parser["extra-scripts"]

    @property
    def launcher_script_template(self):
        return self._parser["launcher"]["template"]

    @property
    def device_image_file(self):
        return self._parser["launcher"]["image-path"]

    @property
    def device_mount_point(self):
        return self._parser["launcher"]["mount-point"]

    @property
    def bind_mounts(self):
        return self._parser.items("bind-mounts")
