import ast
from io import open
import os
import sys

from setuptools import Extension, setup


def version():
    filename = "src/pillow_avif/__init__.py"
    with open(filename) as f:
        tree = ast.parse(f.read(), filename)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            (target,) = node.targets
            if isinstance(target, ast.Name) and target.id == "__version__":
                return node.value.value if hasattr(node.value, "value") else node.value.s


def readme():
    try:
        with open("README.md") as f:
            return f.read()
    except IOError:
        pass


IS_DEBUG = hasattr(sys, "gettotalrefcount")
PLATFORM_MINGW = os.name == "nt" and "GCC" in sys.version

libraries = ["avif"]
include_dirs = []
library_dirs = []


def pkg_config(name):
    try:
        import subprocess

        command = ["pkg-config", "--cflags", "--libs", name]
        output = subprocess.check_output(command).decode("utf-8").strip()
        flags = output.split()
        return flags
    except (OSError, subprocess.CalledProcessError):
        return []


# Try to use pkg-config to find libavif
avif_flags = pkg_config("libavif")

for flag in avif_flags:
    if flag.startswith("-I"):
        include_dirs.append(flag[2:])
    elif flag.startswith("-L"):
        library_dirs.append(flag[2:])

if sys.platform == "win32":
    libraries.extend(
        [
            "advapi32",
            "bcrypt",
            "ntdll",
            "userenv",
            "ws2_32",
            "kernel32",
        ]
    )

test_requires = [
    "pytest",
    "packaging",
    "pytest-cov",
    "test-image-results",
    "pillow",
]

setup(
    name="pillow-avif-plugin",
    description="A pillow plugin that adds avif support via libavif",
    long_description=readme(),
    long_description_content_type="text/markdown",
    version=version(),
    ext_modules=[
        Extension(
            "pillow_avif._avif",
            ["src/pillow_avif/_avif.c"],
            depends=["avif/avif.h"],
            libraries=libraries,
            include_dirs=include_dirs,
            library_dirs=library_dirs,
        ),
    ],
    package_data={"": ["README.rst"]},
    package_dir={"": "src"},
    packages=["pillow_avif"],
    license="MIT License",
    author="Frankie Dintino",
    author_email="fdintino@theatlantic.com",
    url="https://github.com/fdintino/pillow-avif-plugin/",
    download_url="https://github.com/fdintino/pillow-avif-plugin/releases",
    install_requires=[],
    extras_require={"tests": test_requires},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    zip_safe=not (IS_DEBUG or PLATFORM_MINGW),
)
