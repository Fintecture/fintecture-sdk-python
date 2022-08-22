import os
from codecs import open
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

os.chdir(here)

with open(
    os.path.join(here, "LONG_DESCRIPTION.rst"), "r", encoding="utf-8"
) as fp:
    long_description = fp.read()

version_contents = {}
with open(os.path.join(here, "fintecture", "version.py"), encoding="utf-8") as f:
    exec(f.read(), version_contents)

setup(
    name="fintecture",
    version=version_contents["VERSION"],
    description="Python bindings for the Fintecture API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Fintecture",
    author_email="contact@fintecture.com",
    url="https://github.com/Fintecture/fintecture-sdk-python",
    license="MIT",
    keywords="fintecture api payments",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"fintecture": ["data/ca-certificates.crt"]},
    zip_safe=False,
    install_requires=[
        'requests >= 2.20; python_version >= "3.0"',
        'requests[security] >= 2.20; python_version < "3.0"',
        'cryptography ~= 37.0.4',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    project_urls={
        "Bug Tracker": "https://github.com/Fintecture/fintecture-sdk-python/issues",
        "Changes": "https://github.com/Fintecture/fintecture-sdk-python/blob/master/CHANGELOG.md",
        "Documentation": "https://fintecture.com/docs/api/?lang=python",
        "Source Code": "https://github.com/Fintecture/fintecture-sdk-python",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=["wheel"],
)