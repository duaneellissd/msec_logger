
from setuptools import setup

setup( name='msec_logger',
       version='1.0',
       description='A simplified debug logging system useful during application development.',
       long_description=' Unlike other logging schemes that are syslog based, and thus often flood syslog with useless dribble, this is a standalone solution that uses a local logfile but can, if needed it can also write to the syslog.',
       url='http://github.com/duaneellissd/msec_logger',
       author='Duane Ellis',
       author_email='duane@duaneellis.com',
       keywords=['logging', 'millisecond', 'embedded-system'],
       license='PSF - Same as Python',
       platforms='any',
       test_suite='tests',
       packages=['msec_logger'] )

