import io
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def load_readme():
    with io.open(os.path.join(HERE, "README.rst"), "rt", encoding="utf8") as f:
        return f.read()


def load_about():
    about = {}
    with io.open(
        os.path.join(HERE, "license_manager", "__about__.py"),
        "rt",
        encoding="utf-8",
    ) as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about


ABOUT = load_about()


setup(
    name="tutor-contrib-license-manager",
    version=ABOUT["__version__"],
    url="https://github.com/True-Course-Simulations/tutor-contrib-license-manager",
    project_urls={
        "Code": "https://github.com/True-Course-Simulations/tutor-contrib-license-manager",
        "Issue tracker": "https://github.com/True-Course-Simulations/tutor-contrib-license-manager/issues",
        "Upstream (original plugin)": "https://github.com/lpm0073/tutor-contrib-license-manager",
    },
    license="AGPLv3",
    author="Lawrence McDaniel",
    author_email="lpm0073@gmail.com",
    maintainer="Cannon Smith",
    maintainer_email="cannon@tcsims.com",
    description="A Tutor plugin for Open edX License Manager (Sumac / Tutor v16+ compatible)",
    long_description=load_readme(),
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=["tutor>=16.0.0"],
    entry_points={
        "tutor.plugin.v1": [
            "license_manager = license_manager.plugin"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)