# -*- coding: utf-8 -*-

"""
Utilities to render markup formats to HTML
"""

from __future__ import (
	print_function, unicode_literals,
	division, absolute_import)

import sys

from markdown import markdown
from docutils import core
try:
	raise ImportError('not implemented') #TODO fix
	from docutils_html5_writer import Writer as RSTHTMLWriter
except ImportError:
	print('no html5 writer available', file=sys.stderr)
	from docutils.writers.html4css1 import Writer as RSTHTMLWriter

def mdconverter(source):
	"""Converts Markdown source to HTML"""
	# http://www.freewisdom.org/projects/python-markdown/
	return markdown(source, ['extra', 'codehilite'])

def rstconverter(source):
	"""Converts reStructuredText source to HTML"""
	parts = core.publish_parts(source=source, writer=RSTHTMLWriter())
	return parts['whole']

class Format(object):
	"""
	Holds a format supported by markdowner.
	Formats have names, a bunch of file extensions, and associated converters
	"""
	def __init__(self, name, converter, extensions):
		self.name = name
		self.converter = converter
		self.extensions = extensions
	def __iter__(self):
		return self.extensions

FMTLIST = (
	Format('Dummy', '<pre>{}</pre>'.format, ('',)),
	Format('Markdown', mdconverter,
		('md', 'mdwn', 'mdown', 'markdown', 'txt', 'text', 'mdtext')),
	Format('reStructuredText', rstconverter,
		('rst', 'rest'))
)
FORMATS = {ext: fmt for fmt in FMTLIST for ext in fmt.extensions}