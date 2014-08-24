# -*- coding: utf-8 -*-
#
# This file is part of RestAuthClient (https://python.restauth.net).
#
# RestAuthClient is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# RestAuthClient is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with RestAuthClient.py.
# If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals

import os
import re
import sys
import shutil
import unittest

from distutils.command.clean import clean as _clean
from subprocess import PIPE
from subprocess import Popen

try:
    from setuptools import Command
    from setuptools import setup
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import Command
    from setuptools import setup

from RestAuthClient import version as LATEST_RELEASE
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

name = 'RestAuthClient'
url = 'https://python.restauth.net'

requires = ['RestAuthCommon>=0.6.5', ]
coverage_path = os.path.join('doc', 'coverage')

class build_doc(Command):
    description = "Build documentation."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        version = get_version()
        os.environ['LATEST_RELEASE'] = LATEST_RELEASE
        os.environ['SPHINXOPTS'] = ' '.join([
            '-D release=%s' % version,
            '-D version=%s' % version,
        ])

        cmd = ['make', '-C', 'doc', 'html']
        p = Popen(cmd)
        p.communicate()


class clean(_clean):
    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists(coverage_path):
            shutil.rmtree(coverage_path)
        if os.path.exists('MANIFEST'):
            os.remove('MANIFEST')

        cmd = ['make', '-C', 'doc', 'clean']
        p = Popen(cmd)
        p.communicate()

        _clean.run(self)


def get_version():
    version = LATEST_RELEASE
    if os.path.exists('.git'):  # get from git
        cmd = ['git', 'describe', 'master']
        p = Popen(cmd, stdout=PIPE)
        version = p.communicate()[0].decode('utf-8')
    elif os.path.exists('debian/changelog'):  # building .deb
        f = open('debian/changelog')
        version = re.search('\((.*)\)', f.readline()).group(1)
        f.close()

        if ':' in version:  # strip epoch:
            version = version.split(':', 1)[1]
        version = version.rsplit('-', 1)[0]  # strip debian revision
    return version.strip()


class version(Command):
    description = "Print version and exit."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(get_version())


def run_test_suite(host, user, passwd, part=None):
    if part is None:
        from tests import connection, users, groups
        suite = connection, users, groups
    else:
        mod = __import__('tests', globals(), locals(), [part], -1)
        suite = [getattr(mod, part)]

    for mod in suite:
        mod.rest_host = host
        mod.rest_user = user
        mod.rest_passwd = passwd

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(mod)
        unittest.TextTestRunner(verbosity=1).run(suite)


class prepare_debian_changelog(Command):
    description = "prepare debian/changelog file"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.exists('debian/changelog'):
            sys.exit(0)

        version = get_version()
        cmd = ['sed', '-i', '1s/(.*)/(%s-1)/' % version, 'debian/changelog']
        p = Popen(cmd)
        p.communicate()


server_options = [
    # cast to str because Python2 distutils requires a str.
    (str('user='), str('u'), 'Username to use vor RestAuth server'),
    (str('password='), str('p'), 'Password to use vor RestAuth server'),
    (str('host='), str('h'), 'URL of the RestAuth server (ex: http://auth.example.com)')
]


class test(Command):
    description = "Run test suite."
    user_options = server_options + [
        # cast to str because Python2 distutils requires a str.
        (str('part='), None,
         'Only test one module (either "connection", "users" or "groups")'),
    ]

    def initialize_options(self):
        self.user = 'example.com'
        self.passwd = 'nopass'
        self.host = 'http://[::1]:8000'
        self.part = None

    def finalize_options(self):
        if self.part not in [None, 'connection', 'users', 'groups']:
            print('part must be one of "connection", "users" or "groups"')
            sys.exit(1)

    def run(self):
        common_path = os.path.join('..', 'RestAuthCommon', 'python')
        if os.path.exists(common_path):
            sys.path.insert(0, common_path)

        run_test_suite(self.host, self.user, self.passwd, part=self.part)


class coverage(Command):
    description = "Run test suite and generate code coverage analysis."
    user_options = server_options

    def initialize_options(self):
        self.user = 'example.com'
        self.passwd = 'nopass'
        self.host = 'http://[::1]:8000'

    def finalize_options(self):
        pass

    def run(self):
        try:
            import coverage
        except ImportError:
            print("You need coverage.py installed.")
            return
        common_path = os.path.join('..', 'RestAuthCommon', 'python')
        if os.path.exists(common_path):
            sys.path.insert(0, common_path)

        if not os.path.exists(coverage_path):
            os.makedirs(coverage_path)

        cov = coverage.coverage(include='RestAuthClient/*')

        if PY3:
            cov.exclude('pragma: .*py2')
        else:
            cov.exclude('pragma: .*py3')

        cov.start()
        run_test_suite(self.host, self.user, self.passwd)
        cov.stop()
        cov.html_report(directory=coverage_path)
        cov.report()

setup(
    name=name,
    version=str(get_version()),
    description='RestAuth client library',
    long_description="""RestAuthClient is the client reference implementation
of the `RestAuth protocol <https://restauth.net/Specification>`_. RestAuth is a
system providing shared authentication, authorization and preferences. The full
documentation of this library is available at
`python.restauth.net <https://python.restauth.net>`_.

This library requires `RestAuthCommon <https://common.restauth.net>`_
(`PyPI <http://pypi.python.org/pypi/RestAuthCommon/>`_).
""",
    author='Mathias Ertl',
    author_email='mati@restauth.net',
    url=url,
    download_url='https://python.restauth.net/download/',
    packages=['RestAuthClient', ],
    cmdclass={
        'build_doc': build_doc,
        'clean': clean,
        'coverage': coverage,
        'prepare_debian_changelog': prepare_debian_changelog,
        'test': test,
        'version': version,
    },
    license="GNU General Public License (GPL) v3",
    install_requires=requires,
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ]
)
