"""
Creates an application from the cmd line args and starts a editor window
"""

import sys

from PyKDE4.kdecore import KGlobal, KCmdLineOptions, KCmdLineArgs
from PyKDE4.kdeui   import KApplication

from . import Markdowner, ABOUT, ki18n

def main():
	"""Creates an application from the cmd line args and starts a editor window"""
	
	KCmdLineArgs.init(sys.argv, ABOUT)
	opts = KCmdLineOptions()
	opts.add('+[file]', ki18n('File to open'))
	KCmdLineArgs.addCmdLineOptions(opts)
	
	args = KCmdLineArgs.parsedArgs()
	urls = [args.url(i) for i in range(args.count())] #wurgs
	
	app = KApplication()
	#KGlobal.locale().setLanguage(['de']) TODO
	win = Markdowner(urls)
	win.show()
	sys.exit(app.exec_())

main()