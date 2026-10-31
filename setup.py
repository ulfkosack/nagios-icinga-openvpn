from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()

setup(
  name         = 'nagios-icinga-openvpn',
  version      = '0.0.1',
  author       = 'Roland Wolters (liquidat)',
  author_email = 'liquidat@bayz.de',
  url          = 'https://github.com/liquidat/nagios-icinga-openvpn',
  scripts      = ['bin/check_openvpn'],
  description  = 'Nagios/Icinga check for OpenVPN availability',
  long_description=long_description,
  long_description_content_type='text/markdown',
  license      = 'MIT',
  classifiers  = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Topic :: System :: Monitoring',
  ],
)
