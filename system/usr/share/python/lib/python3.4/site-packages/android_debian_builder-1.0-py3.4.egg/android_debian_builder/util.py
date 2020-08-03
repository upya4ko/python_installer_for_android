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

from contextlib import contextmanager
import os
import pkgutil
import shutil
import subprocess
import sys
import tempfile
import time


def call(args, *pos_args, **kwargs):
    """Run the command with `subprocess.check_call`.

    If the first element of `args` is not an absolute path, it is looked up
    using `shutil.which` and the resulting binary is run, if any.

    >>> call(["true"])
    0
    >>> call(["this-does-not-exist"])
    Traceback (most recent call last):
    ...
    OSError: `this-does-not-exist` not found
    """
    cmd = args[0]
    binary = shutil.which(cmd)
    if not binary:
        raise OSError("`%s` not found" % cmd)
    copied_args = args[:]
    copied_args[0] = binary
    return subprocess.check_call(copied_args, *pos_args, **kwargs)


def parse_size(size):
    """Parse a size specification, i.e. an int with a K, M, G suffix.

    >>> parse_size("1000")
    1000
    >>> parse_size("100K")
    102400
    >>> parse_size("1M")
    1048576
    >>> parse_size("5 g")
    5368709120
    >>> parse_size("")
    Traceback (most recent call last):
    ...
    ValueError
    >>> parse_size("test M")
    Traceback (most recent call last):
    ...
    ValueError: test M
    """
    SUFFIXES = {
        "K": 1024,
        "M": 1024 * 1024,
        "G": 1024 * 1024 * 1024,
    }

    if not size:
        raise ValueError(size)
    s = size.strip()
    suffix = s[-1]
    try:
        mult = SUFFIXES[suffix.upper()]
        s = s[:-1]
    except KeyError:
        mult = 1
    try:
        return int(s.strip()) * mult
    except ValueError:
        raise ValueError(size)


def generate_zero_file(path, size):
    """Generate a file of a certain size filled with '\0'.

    Equivalent to `dd if=/dev/zero of=path count=size`.
    """
    CHUNK_SIZE = 10 * 1024
    data = b"\0" * CHUNK_SIZE
    with open(path, "wb") as f:
        for i in range(size // CHUNK_SIZE):
            f.write(data)
        f.write(b"\0" * (size % CHUNK_SIZE))


def create_fs(path, fs, extra_opts=["-F"]):
    """Run mkfs."""
    args = ["mkfs", "-t", fs]
    args.extend(extra_opts)
    args.append(path)
    call(args)


def umount(path, ntries=10, interval=1):
    """Run `umount` on the given path, retrying as necessary."""
    for i in range(ntries):
        try:
            call(["umount", path])
            return
        except Exception:
            print("-- umount failed, retrying in %s second(s)..." % interval)
            time.sleep(interval)
    raise OSError("failed umount %s times" % ntries, path)


@contextmanager
def mount_image(path):
    """Context manager to loop-mount a file to a temporary mount point.

    The absolute path of the mount point will be available for the `with`
    statement's `as` part.
    """
    mounted = False
    tmp_dir = tempfile.mkdtemp()
    try:
        call(["mount", "-o", "loop", path, tmp_dir])
        mounted = True
        yield tmp_dir
    finally:
        if mounted:
            umount(tmp_dir)
        os.rmdir(tmp_dir)


def chroot_path(mount, path):
    """Join the base path of a chroot and an absolute path in the chroot.

    >>> chroot_path("/var/chroot", "/etc/debian.sh")
    '/var/chroot/etc/debian.sh'
    """
    return os.path.join(mount, os.path.relpath(path, "/"))


def load(path, encoding="utf-8"):
    """Load a string from a file or an internal package resource.

    If `path` starts with "builtin:", that prefix is stripped and the package
    resource with that name is loaded; if path is `-`, stdin is used;
    otherwise, it is interpreted as a file name. The contents of the file are
    returned as a string, decoded with the given encoding (if applicable).
    """
    if path.startswith("builtin:"):
        res_path = path[8:]
        try:
            res_bin = pkgutil.get_data("android_debian_builder", res_path)
        except Exception:
            res_bin = None
        if res_bin is None:
            raise FileNotFoundError(path)
        return res_bin.decode(encoding)
    elif path == "-":
        return sys.stdin.read()
    else:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
