# -*- coding: utf-8 -*-

"""
A program to edit Markdown and reStructuredText documents with previews
"""

from __future__ import (
	print_function, unicode_literals,
	division, absolute_import)

from contextlib import contextmanager

from PyQt4.QtCore import Qt, QUrl, QThread, pyqtSlot as Slot
from PyQt4.QtGui import (
	QWidget, QDesktopServices, QDockWidget,
	QPalette, QSizeGrip, QScrollBar)
from PyQt4.QtWebKit import QWebSettings, QWebView, QWebPage, QWebInspector
QWebSettings.globalSettings().setAttribute(
	QWebSettings.DeveloperExtrasEnabled, True)

from PyKDE4.kdecore     import KAboutData, KUrl, ki18n, i18n
from PyKDE4.kdeui       import KIcon, KMessageBox
from PyKDE4.kparts      import KParts
from PyKDE4.ktexteditor import KTextEditor

from .formats import FORMATS
from .resources import base64css

ABOUT = KAboutData(
	'markdowner',
	'',
	ki18n(b'Markdowner'),
	'1.0',
	ki18n(b'Markdown editor'),
	KAboutData.License_GPL,
	ki18n('© 2011 flying sheep'.encode('utf-8')),
	ki18n(b'none'),
	'http://red-sheep.de',
	'flying-sheep@web.de')

class Renderer(QThread):
	"""Thread which can reconvert the markup document"""
	def __init__(self, widget):
		QThread.__init__(self)
		self.widget = widget
		self.scrollpos = None
		self.html = ''
	def run(self):
		"""Causes the markdowner to rerender"""
		self.scrollpos = self.widget.preview.page().mainFrame().scrollPosition()
		source = self.widget.editor.document().text()
		html = self.widget.format.converter(source)
		self.html = '<html><body>{}</body></html>'.format(html)

class Markdowner(KParts.MainWindow):
	"""Main Editor window"""
	def __init__(self, urls, parent=None):
		KParts.MainWindow.__init__(self, parent)
		
		self.setWindowIcon(KIcon('text-editor'))
		
		self.kate = KTextEditor.EditorChooser.editor()
		self.editor = self.kate.createDocument(self).createView(self)
		doc = self.editor.document()
		self.editor.setContextMenu(self.editor.defaultContextMenu())
		
		sizegrip = create_grip(self.editor)
		sizegrip.show() #TODO: only show on windowstate change
		
		self.renderer = Renderer(self)
		
		@doc.textChanged.connect
		def _start_markdown(doc=None, old_range=None, new_range=None):
			"""Runs the renderer if it’s not currently rendering"""
			if not self.renderer.isRunning():
				self.renderer.start()
		
		@self.renderer.finished.connect
		def _stop_markdown():
			"""
			Replaces the preview HTML with the newly rendered one
			and restores the scroll position
			"""
			url = self.editor.document().url().resolved(QUrl('.'))
			self.preview.setHtml(self.renderer.html, url) #baseurl für extenes zeug
			self.preview.page().mainFrame().setScrollPosition(self.renderer.scrollpos)
		
		self.editor.document().documentNameChanged.connect(self.refresh_document)
		
		self.guiFactory().addClient(self.editor)
		self.setCentralWidget(self.editor)
		
		self.preview = QWebView()
		self.preview.settings().setUserStyleSheetUrl(base64css())
		self.preview.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.preview.linkClicked.connect(self.intercept_link)
		
		with self.setup_dock(self.preview, 'Preview', Qt.RightDockWidgetArea) as dock:
			page = self.preview.page()
			palette = page.palette()
			palette.setBrush(QPalette.Base, Qt.transparent)
			page.setPalette(palette)
			
			self.preview.setAttribute(Qt.WA_TranslucentBackground)
			self.preview.setAttribute(Qt.WA_OpaquePaintEvent, False)
			
			dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
		
		inspector = QWebInspector()
		with self.setup_dock(inspector, 'Inspector', Qt.BottomDockWidgetArea) as dock:
			inspector.setPage(self.preview.page())
			dock.hide()
			inspect_action = self.preview.page().action(QWebPage.InspectElement)
			inspect_action.triggered.connect(dock.show)
		
		if len(urls) != 0:
			self.editor.document().openUrl(urls[0])
		
		#TODO: spellcheck
		self.setAutoSaveSettings()
		self.kate.readConfig(self.autoSaveConfigGroup().config())
	
	@property
	def format(self):
		"""Gets the format from the corrent document’s file extension"""
		path = self.editor.document().url().path()
		ext = path[path.rfind('.') + 1:]
		return FORMATS[ext]
	
	def queryClose(self):
		"""
		Gets invoked by Qt if the window is about to be closed
		Returns True if it is allowed to close
		"""
		self.kate.writeConfig(self.autoSaveConfigGroup().config())
		
		if self.editor.document().isModified():
			ret = KMessageBox.warningYesNoCancel(self,
				i18n(b'Save changes to document?'))
			if ret == KMessageBox.Yes:
				return self.editor.document().documentSave()
			else:
				return ret == KMessageBox.No
		else:
			return True
	
	@Slot(QUrl)
	def intercept_link(self, url):
		"""Allows to open documents or scrolling to anchors when clicking links"""
		#reenable scrolling to anchor in document
		if url.hasFragment() and url.scheme() == 'about' and url.path() == 'blank':
			self.preview.page().currentFrame().scrollToAnchor(url.fragment())
		elif url.isRelative() and self.queryExit():
			#TODO: less hacky, extensions
			url = KUrl(self.editor.document().url().path() + url.path())
			self.editor.document().openUrl(url)
		else:
			QDesktopServices.openUrl(url)
	
	@Slot(KTextEditor.Document)
	def refresh_document(self, doc):
		"""Sets the necessary bits if a new document is loaded"""
		self.setWindowTitle('{} – {}'.format(
			doc.documentName(),
			ABOUT.programName()
		))
		doc.setMode(self.format.name)
	
	@contextmanager
	def setup_dock(self, widget, name, area):
		"""Helps to setup docks more semantically"""
		dock = QDockWidget(name, self)
		dock.setObjectName(name)
		
		yield dock
		
		self.addDockWidget(area, dock)
		dock.setWidget(widget)

def create_grip(editor):
	"""
	Hack that extracts the dummy widget
	in the corner of the editor scrollbars
	and overlays it with a QSizeGrip
	"""
	for child in editor.children():
		if issubclass(type(child), QScrollBar):
			w_dummy = min(child.width(), child.height())
			break
	
	for child in editor.children():
		if (issubclass(type(child), QWidget)
			and child.width() == w_dummy
			and child.height() == w_dummy):
			dummy = child
			break
	#dummy = editor.m_viewInternal.m_dummy
	
	sizegrip = QSizeGrip(dummy)
	sizegrip.resize(w_dummy, w_dummy)
	return sizegrip