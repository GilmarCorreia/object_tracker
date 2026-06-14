import os
from glob import glob

from setuptools import find_packages, setup

package_name = "object_tracker"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools", "cv_bridge"],
    zip_safe=True,
    maintainer="gilmar",
    maintainer_email="gilmarcorreiajeronimo@gmail.com",
    description="Object Tracker codes",
    license="BSD-2-Clause",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "object_tracker = object_tracker.object_tracker:main",
        ],
    },
)
