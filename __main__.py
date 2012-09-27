#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Creates an application from the cmd line args and starts a editor window
"""

from __future__ import (
	print_function, unicode_literals,
	division, absolute_import)

import sys

if __package__ is None:
	import os
	PARDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	sys.path.insert(0, PARDIR)
	import markdowner
	__package__ = 'markdowner'

from PyKDE4.kdecore import ki18n, KCmdLineOptions, KCmdLineArgs
from PyKDE4.kdeui   import KApplication

from . import Markdowner, ABOUT

def main():
	"""Creates an application from the cmd line args and starts a editor window"""
	
	KCmdLineArgs.init(sys.argv, ABOUT)
	opts = KCmdLineOptions()
	opts.add('+[file]', ki18n(b'File to open'))
	KCmdLineArgs.addCmdLineOptions(opts)

	args = KCmdLineArgs.parsedArgs()
	urls = [args.url(i) for i in range(args.count())] #wurgs

	app = KApplication()
	win = Markdowner(urls)
	win.show()
	sys.exit(app.exec_())

main()