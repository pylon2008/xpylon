#from distutils.core import setup
from setuptools import find_packages, setup, findall

DATA_FILES = [('.\\Lib\\site-packages\\xpylon\\doc',findall('./doc')), \
              ('.\\Lib\\site-packages\\xpylon\\tutorial', findall('./tutorial')), \
              ('.\\Lib\\site-packages\\xpylon\\test', findall('./test')),]

setup(name='xpylon',
      version = '1.0',
      description = 'xpylon Distribution Utilities',
      author = 'xpylon',
      author_email = 'gward@python.net',
      url = 'http://www.python.org/sigs/distutils-sig/',
      include_package_data = True,
      packages = ['xpylon', 'xpylon.xethernet', 'xpylon.xutil'],
      package_dir  = {'xpylon':'src/xpylon', 'xpylon.xethernet': 'src/xpylon/xethernet', 'xpylon.xutil': 'src/xpylon/xutil'},
      data_files = DATA_FILES,
     )
