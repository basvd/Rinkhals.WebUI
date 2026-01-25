#!/usr/bin/env micropython
"""Install MicroPython packages via mip."""

import mip

PACKAGES = [
    "__future__",
    "abc",
    "argparse",
    "base64",
    "binascii",
    "bisect",
    "cmd",
    "collections",
    "collections-defaultdict",
    "contextlib",
    "copy",
    "curses.ascii",
    "datetime",
    "errno",
    "fnmatch",
    "functools",
    "gzip",
    "hashlib",
    "hashlib-core",
    "hashlib-sha224",
    "hashlib-sha256",
    "hashlib-sha384",
    "hashlib-sha512",
    "heapq",
    "hmac",
    "html",
    "inspect",
    "io",
    "itertools",
    "keyword",
    "locale",
    "logging",
    "operator",
    "os",
    "os-path",
    "pathlib",
    "pickle",
    "pkg_resources",
    "pkgutil",
    "pprint",
    "quopri",
    "random",
    "shutil",
    "ssl",
    "stat",
    "string",
    "struct",
    "tarfile",
    "tarfile-write",
    "tempfile",
    "textwrap",
    "threading",
    "time",
    "traceback",
    "types",
    "unittest",
    "unittest-discover",
    "uu",
    "venv",
    "warnings",
    "zlib",
]


def install_all():
    failures = []
    for package in PACKAGES:
        print("Installing {}".format(package))
        try:
            mip.install(package)
        except Exception as exc:
            failures.append((package, exc))
            print("Failed installing {}: {}".format(package, exc))
    if failures:
        print("Completed with failures:")
        for package, exc in failures:
            print("  {}: {}".format(package, exc))
        raise SystemExit(1)
    print("All packages installed successfully.")


if __name__ == "__main__":
    install_all()
