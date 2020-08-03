#!/usr/bin/python3
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

import argparse
from itertools import chain
import sys

from .build import gen_script, import_extra_keys, run_multistrap, store_config
from .config import Config
from .util import (
    chroot_path, parse_size,
    generate_zero_file, create_fs,
    load, mount_image)


DEFAULT_IMG_PATH = "debian.img"
DEFAULT_SCRIPT_PATH = "deb"
DEFAULT_CONFIG = "builtin:data/default-config"


def build_image(image_path, config):
    """Build system image."""
    print("++ creating %s file system in %s (%s)..." %
          (config.image_fs, image_path, config.image_size))
    generate_zero_file(image_path, parse_size(config.image_size))
    create_fs(image_path, config.image_fs)
    print("++ mounting image...")
    with mount_image(image_path) as mountpoint:
        print("++ running multistrap...")
        run_multistrap(mountpoint, config.multistrap_config)
        print("++ adding extra GPG keys...")
        import_extra_keys(mountpoint, config.extra_gpg_keys)
        print("++ creating basic init script...")
        gen_script(chroot_path(mountpoint, config.init_script),
                   load(config.init_script_template),
                   config)
        print("++ creating extra files...")
        for scriptname, template in config.extra_scripts.items():
            gen_script(chroot_path(mountpoint, scriptname),
                       load(template),
                       config)
        print("++ embedding effective configuration...")
        store_config(mountpoint, config)


def build_script(script_path, config):
    """Build launcher script."""
    print("++ creating launcher script...")
    gen_script(script_path, load(config.launcher_script_template), config)


def parse_args(argv):
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="Generate Debian image.")
    parser.add_argument("--config", metavar="CFG", type=str, nargs="*",
                        default=[],
                        help="Specify a custom config file. May be used "
                             "multiple times.")
    parser.add_argument("--image", metavar="IMAGE", type=str,
                        default=DEFAULT_IMG_PATH,
                        help="Use a different image path.")
    parser.add_argument("--script", metavar="SCRIPT", type=str,
                        default=DEFAULT_SCRIPT_PATH,
                        help="Use a different launcher script path.")
    parser.add_argument("--only-script", action="store_true", default=False,
                        help="Only generate the launcher script.")
    parser.add_argument("--print-config", action="store_true", default=False,
                        help="Print the configuration in effect and exit.")
    parser.add_argument("--no-default-config", action="store_true",
                        default=False,
                        help="Don't include the default configuration.")
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    if args.no_default_config:
        cfgpaths = args.config
    else:
        cfgpaths = chain([DEFAULT_CONFIG], args.config)
    cfg = Config(cfgpaths)
    if args.print_config:
        cfg.dump(sys.stdout)
    else:
        if not args.only_script:
            build_image(args.image, cfg)
        build_script(args.script, cfg)


if __name__ == "__main__":
    main()
