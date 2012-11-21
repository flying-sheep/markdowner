# -*- coding: utf-8 -*-

"""
Access to resouce files
"""

from __future__ import (
	print_function, unicode_literals,
	division, absolute_import)

import re
from base64 import b64encode
from os.path import * #we just do path stuff here, so we might as well

from PyQt4.QtCore import QUrl
from PyQt4.QtGui  import QPalette
from PyKDE4.kdeui import KColorScheme, KIcon, KMessageBox

HERE = dirname(realpath(__file__))

def developing():
	user_dir = expanduser('~')
	return commonprefix([HERE, user_dir]) == user_dir

if developing():
	RES_DIR = join(HERE, '..', 'resources')
else:
	RES_DIR = '/usr/share/markdowner' #TODO

def dot_repl(matchobj):
	"""
	Changes custom template to str.format template
	usable with "ColorRole opacity" keys.
	"""
	dic, color, alph = matchobj.groups()
	return '{{{}[{} {}]}}'.format(dic, color, alph or 1)

with open(join(RES_DIR, 'html.css')) as css_file:
	CSS_TEMPLATE = css_file.read()
	#convert custom template to python template string:
	CSS_TEMPLATE = re.sub(r'\{([^\}]*)\}',   r'{{\1}}',   CSS_TEMPLATE)
	CSS_TEMPLATE = re.sub(r'\$(\w+)\.(\w+)(\.\d+)?', dot_repl, CSS_TEMPLATE)

class Colors(object):
	"""Singleton to access colors from the current color theme"""
	def __getitem__(self, role):
		scheme = KColorScheme(QPalette.Active, KColorScheme.Window)
		role, alph = role.split()
		role = KColorScheme.__dict__[role]
		try:
			color = scheme.foreground(role).color()
		except TypeError:
			color = scheme.background(role).color()
		return 'rgba({}, {}, {}, {})'.format(
			color.red(), color.green(), color.blue(), alph or color.alpha())
COLORS = Colors()

def base64css():
	"""
	generates a base64 encoded version of a file
	suited for HTML src attributes.
	"""
	cssbytes = CSS_TEMPLATE.format(colors=COLORS).encode('utf-8')
	uri = 'data:text/css;charset=utf-8;base64,'
	uri += b64encode(cssbytes).decode('utf-8')
	return QUrl(uri)