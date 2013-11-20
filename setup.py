from setuptools import setup
import sys

packages = ['seamicro_api', ]
install_requires = ['enum', 'requests']
tests_require = []

if sys.version_info < (2, 7, 0):
    install_requires.append('simplejson')

from seamicro_api import version


setup(name='seamicro_api',
      version=version.get_git_version(),
      description='Python bindings for SeaMicro API v0.9',
      url='https://github.com/seamicro/scripts/seamicro_api',
      packages=packages,
      author='Vince Gonzalez',
      author_email='vince.gonzalez@amd.com',
      license='MIT',
      install_requires=install_requires)
