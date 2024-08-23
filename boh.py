#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/appImageViewer.py
#
#  includes classes: MyGraphicsView, MainWindow
#
#  Simple program that uses Qt to display an image, it has some few options.
#    File menu: Open File, Clear Image, Print Info, and (Close and) Quit
#    Scale menu: Scale 1, Scale Up, and Scale down
#  In the bottom it display the value for pixel that mouse points on (without clicking)
#  It can also print information for many of the attributes used
#  This program does not use numpy or qimage2ndarray or ueye (IDS camera). 
#
# Karl Skretting, UiS, September-October 2018, February 2019, November 2020, June 2022

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> python appImageViewer.py
# (py38) C:\..\py3> python appImageViewer.py kart1.png

_appFileName = "ChessboardImage"
_author = "FEF, UiS" 
_version = "1.0"

import sys
import os.path
import cv2
try:
	from PyQt5.QtCore import Qt, QT_VERSION_STR   # QSize, QPoint, QRect, QRectF, 
	from PyQt5.QtGui import QImage, QPixmap, QTransform
	from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, 
			QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes 
myPath = ''                # path where you may have some images
#end try, import DBpath  

class MyGraphicsView(QGraphicsView):
	"""A simple extension of QGraphicsView, the viewer where the pixmap is shown 
	Mouse events are processed in this class, 
	and some variables belonging to the parent (MainWindow object) are used
	"""
	def __init__(self, scene, parent = None):
		"""Initialize as for the inherited class 'QGraphicView', then set mouse tracking to True."""
		super().__init__(scene, parent)
		self.setMouseTracking(True)
		return
		
	def mousePressEvent(self, event):
		"""Just print where the mouse is when a mouse button is pressed.
		Note that event.pos() gives the location in the view, while (x,y) gives the
		location in the scene, which here corresponds to the pixel index of the pixmap.
		This method is a 'slot' that is called whenever a mouse button is pressed (in the view).
		"""
		posScene = self.mapToScene(event.pos())
		(x,y) = (int(posScene.x()), int(posScene.y()))
		#
		if (event.button() == Qt.LeftButton):
			print("MyGraphicsView.mousePressEvent(): Press LeftButton at:  ", end='') 
		if (event.button() == Qt.RightButton):
			print("MyGraphicsView.mousePressEvent(): Press RightButton at: ", end='')
		print( f"{str(event.pos())}, in scene at (x,y) = ({x},{y})" )
		return 
		
	def mouseMoveEvent(self, event):
		"""Displays position of mouse pointer and, from the QImage object, the pixel color. 
		This method is a 'slot' that is called whenever the mouse moves over the view.
		"""
		p = self.parent()    # gives easy access to parent attributes here
		posScene = self.mapToScene(event.pos())
		(x,y) = (int(posScene.x()), int(posScene.y()))
		# p.pixmap and p.image should be different representations of the same image, and thus of the same size
		if ((x >= 0) and (y >= 0) and (y < p.pixmap.height()) and (x < p.pixmap.width())):
			if not p.image.isNull():  
				col = p.image.pixelColor(x, y)
				if p.isAllGray: 
					p.posInfo.setText( f"(x,y) = ({x},{y}):  gray = {col.red()}" )   # or col.value()
				elif (p.image.format() == QImage.Format_Indexed8): 
					p.posInfo.setText( f"(x,y) = ({x},{y}):  gray/index  = {col.value()}" )
				else: # QImage.Format_RGB32, or other
					(r,g,b,a) = (col.red(), col.green(), col.blue(), col.alpha())
					if (a == 255):
						p.posInfo.setText( f"(x,y) = ({x},{y}):  (r,g,b) = ({r},{g},{b})" )
					else:
						p.posInfo.setText( f"(x,y) = ({x},{y}):  (r,g,b,a) = ({r},{g},{b},{a})" )
			else: 
				p.posInfo.setText( f"(x,y) = ({x},{y})" )
		else:
			p.posInfo.setText(" ") 
		return

	def mouseReleaseEvent(self, event):
		"""Just print when the left mouse button is released.
		This method is a 'slot' that is called whenever a mouse button is 
		released (after being pressed in the view).
		"""
		if (event.button() == Qt.LeftButton):
			print("MyGraphicsView.mouseReleaseEvent():  Left Button released.")
		#end if
		return
	#end class MyGraphicsView

class MainWindow(QMainWindow):    #  and QMainWindow inherits QWidget
	"""MainWindow class for this simple image viewer."""
	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		"""Initialize the main window object with title, location and size,
		an empty image (represented both as pixmap and image), 
		empty scene and empty view, labels for status and position information.
		A file name 'fName' may be given as input (from command line when program is started)
		and if so the file (an image) will be opened and displayed.
		"""
		# print( f"File {_appFileName}:  (debug) first line in __init__()" )
		super().__init__(parent) 
		self.appFileName = _appFileName 
		self.setGeometry(150, 50, 1400, 800)  # initial window position and size
		self.scaleUpFactor = 2
		#
		self.pixmap = QPixmap()      # a null pixmap
		self.image = QImage()        # a null image
		self.isAllGray = False       # true when self.image.allGray() 
		# the allGray() function is slow for images without color table
		#
		self.scene = QGraphicsScene()
		self.curItem = None          # (a pointer to) pixmap on scene
		self.view = MyGraphicsView(self.scene, parent=self)
		self.status = QLabel('Open image to display it.', parent = self)
		self.posInfo = QLabel(' ', parent = self)
		#
		self.initMenu()  # menu is needed before (!) self.openFile(..)
		#
		if isinstance(fName, str) and (fName != ""):
			self.openFile(fName)
		#
		if (not self.pixmap.isNull()): 
			self.setWindowTitle( f"{self.appFileName} : {fName}" )
		else:
			self.setWindowTitle(self.appFileName)
		#
		# print( f"File {_appFileName}:  (debug) last line in __init__()" )
		#
		self.setMenuItems() 
		return
	#end function __init__ 
	
	def initMenu(self):
		"""Set up the menu for main window: 
		File with Open, Clear, Print (information), and (Close and) Quit, 
		Scale with '1', '+', and '-'.
		"""
		# print( f"File {_appFileName}:  (debug) first line in initMenu()" )
		qaOpenFileDlg = QAction('openFile', self) 
		qaOpenFileDlg.setShortcut('Ctrl+O')
		qaOpenFileDlg.triggered.connect(self.openFileDlg)
		self.qaClearImage = QAction('Clear Image', self)
		self.qaClearImage.setShortcut('Ctrl+C')
		self.qaClearImage.setToolTip('Remove the current pixmap item from scene.')
		self.qaClearImage.triggered.connect(self.removePixmapItem)
		qaPrintInfo = QAction('printInfo', self)
		qaPrintInfo.setShortcut('Ctrl+I')
		qaPrintInfo.triggered.connect(self.printInfo)
		qaPrintShortInfo = QAction('printShortInfo', self)
		qaPrintShortInfo.triggered.connect(self.printShortInfo)
		qaCloseWin = QAction('closeWin', self)
		qaCloseWin.setShortcut('Ctrl+Q')
		qaCloseWin.setToolTip('Close and quit program')
		qaCloseWin.triggered.connect(self.closeWin)
		#
		self.qaScaleUp = QAction('scaleUp', self)
		self.qaScaleUp.setShortcut('Ctrl++')
		self.qaScaleUp.triggered.connect(self.scaleUp)
		self.qaScaleDown = QAction('scaleDown', self)
		self.qaScaleDown.setShortcut('Ctrl+-')
		self.qaScaleDown.triggered.connect(self.scaleDown)
		self.qaScaleOne = QAction('scaleOne', self)
		self.qaScaleOne.setShortcut('Ctrl+1')
		self.qaScaleOne.triggered.connect(self.scaleOne)
		#
		self.mainMenu = self.menuBar()  # menuBar is a function in QMainWindow class, returns a QMenuBar object
		self.fileMenu = self.mainMenu.addMenu('&File')
		self.fileMenu.addAction(qaOpenFileDlg)
		self.fileMenu.addAction(self.qaClearImage)
		self.fileMenu.addAction(qaPrintInfo)
		self.fileMenu.addAction(qaPrintShortInfo)
		self.fileMenu.addAction(qaCloseWin)
		self.fileMenu.setToolTipsVisible(True)
		#
		scaleMenu = self.mainMenu.addMenu('&Scale')
		scaleMenu.addAction(self.qaScaleOne)
		scaleMenu.addAction(self.qaScaleUp)
		scaleMenu.addAction(self.qaScaleDown)
		# print( f"File {_appFileName}: (debug) last line in initMenu()" )
		return
	#end function initMenu
	
# Some methods that may be used by several of the menu actions
	def setMenuItems(self):
		"""Enable/disable menu items as appropriate."""
		pixmapOK = ((not self.pixmap.isNull()) and isinstance(self.curItem, QGraphicsPixmapItem))
		self.qaClearImage.setEnabled(pixmapOK)
		self.qaScaleOne.setEnabled(pixmapOK)
		self.qaScaleUp.setEnabled(pixmapOK)
		self.qaScaleDown.setEnabled(pixmapOK)
		return
		
	def setIsAllGray(self, value=-1):
		"""Set variable 'self.isAllGray', usually by calling method 'QImage.allGray', 
		but value may be given as input argument 'value' as well; ==0 for False, and >0 for True
		"""
		if (value == 0):
			self.isAllGray = False
		elif (value > 0):
			self.isAllGray = True
		else:
			self.isAllGray = self.image.allGray()
		#
		self.setMenuItems()
		return
		
# Methods for actions on the File-menu
	def openFileDlg(self):
		"""Use the Qt file open dialog to select an image to open."""
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog     # make dialog appear the same on all systems
		flt = "All jpg files (*.jpg);;All bmp files (*.bmp);;All png files (*.png);;All files (*)"
		(fName, used_filter) = QFileDialog.getOpenFileName(parent=self, caption="Open image file", 
				directory=myPath, filter=flt, options=options)
		self.openFile(fName)
		return
		
	def openFile(self, fName):   
		"""Open the (image) file both as image (QImage) and pixmap (QPixmap).
		The pixmap is added as an item to the graphics scene which is shown in the graphics view.
		The view is scaled to unity.
		""" 
		# print( f"File {_appFileName}: (debug) first line in openFile()" )
		if (fName != ""):
			self.removePixmapItem()
			print( f"Try to load {fName} into pixmap (image)" )
			self.pixmap.load(fName) 
			# If the file does not exist or is of an unknown format, the pixmap becomes a null pixmap.
			self.image = self.pixmap.toImage()   # and image or a null image
			self.setIsAllGray()
			# print(self.image.format())  often 4, QImage::Format_RGB32 
			if (not self.pixmap.isNull()): # ok
				self.curItem = QGraphicsPixmapItem(self.pixmap)
				self.scene.addItem(self.curItem)
				(w, h) = (self.pixmap.width(), self.pixmap.height())
				self.scene.setSceneRect(0, 0, w, h)
				self.setWindowTitle( f"{self.appFileName} : {fName}" )
				self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
				self.scaleOne()
			else:
				self.setWindowTitle( f"{self.appFileName} : error for file {fName}" )
			#end if
		#end if
		self.setMenuItems()
		# print( f"File {_appFileName}: (debug) last line in openFile()" )
		return
	#end function openFile 
		
	def removePixmapItem(self):
		"""Removes the current pixmap item from the scene if it exists."""
		if self.curItem: 
			self.scene.removeItem(self.curItem)
			self.curItem = None
			self.setMenuItems()
		self.setWindowTitle(self.appFileName)
		self.status.setText('No pixmap (image) on scene.')
		return
	#end function removePixmapItem
	
	def printInfo(self):
		"""Print some general (debug) information for the program and the image."""
		print( "Print some elements of MainWindow(QMainWindow) object.")
		print( f"myPath             = {str(myPath)}" )
		print( f"self               = {str(self)}" )
		print( f"  .parent()          = {str(self.parent())}" )
		print( f"  .appFileName       = {str(self.appFileName)}" )
		print( f"  .pos()             = {str(self.pos())}" )
		print( f"  .size()            = {str(self.size())}" )
		print( f"  .isAllGray         = {str(self.isAllGray)}" )
		print( f"  .scaleUpFactor     = {str(self.scaleUpFactor)}" )
		print( f"  .curItem           = {str(self.curItem)}" )
		print( f"self.view          = {str(self.view)}" )
		print( f"  .parent()          = {str(self.view.parent())}" )
		print( f"  .scene()           = {str(self.view.scene())}" )
		print( f"  .pos()             = {str(self.view.pos())}" )
		print( f"  .size()            = {str(self.view.size())}" )
		t = self.view.transform()
		print( f"  .transform()       = {str(t)}" )
		print( f"    .m11, .m12, .m13   = [{t.m11():5.2f}, {t.m12():5.2f}, {t.m13():5.2f}, " )
		print( f"    .m21, .m22, .m23   =  {t.m21():5.2f}, {t.m22():5.2f}, {t.m23():5.2f}, " )
		print( f"    .m31, .m32, .m33   =  {t.m31():5.2f}, {t.m32():5.2f}, {t.m33():5.2f} ]" )
		print( f"self.scene         = {str(self.scene)}" )
		print( f"  .parent()          = {str(self.scene.parent())}" )
		print( f"  .sceneRect()       = {str(self.scene.sceneRect())}" )
		print( f"  number of items    = {len(self.scene.items())}" )
		if len(self.scene.items()):
			print( f"  first item         = {str(self.scene.items()[0])}" )
		print( f"self.pixmap        = {str(self.pixmap)}" )
		if not self.pixmap.isNull():
			print( f"  .size()            = {str(self.pixmap.size())}" )
			print( f"  .width()           = {str(self.pixmap.width())}" )
			print( f"  .height()          = {str(self.pixmap.height())}" )
			print( f"  .depth()           = {str(self.pixmap.depth())}" )
			print( f"  .hasAlpha()        = {str(self.pixmap.hasAlpha())}" ) 
			print( f"  .isQBitmap()       = {str(self.pixmap.isQBitmap())}" )
		#end if pixmap
		print( f"self.image         = {str(self.image)}" )
		if not self.image.isNull():
			if (self.image.format() == 3):
				s2 = "3 (QImage.Format_Indexed8)"
			elif (self.image.format() == 4):
				s2 = "4 (QImage.Format_RGB32)"
			elif (self.image.format() == 5):
				s2 = "5 (QImage.Format_ARGB32)"
			else:
				s2 = f"{self.image.format()}" 
			#end
			print( f"  .size()            = {str(self.image.size())}" )
			print( f"  .width()           = {str(self.image.width())}" )
			print( f"  .height()          = {str(self.image.height())}" )
			print( f"  .depth()           = {str(self.image.depth())}" )
			print( f"  .hasAlphaChannel() = {str(self.image.hasAlphaChannel())}" )
			print( f"  .format()          = {s2}" )
			print( f"  .allGray()         = {str(self.image.allGray())}" )
		#end if image
		return

	def printShortInfo(self):
		img = cv2.imread(self.pixmap)
		print( f"{img.dtype = }, {img.size = }, {img.ndim = }, {img.shape = }" )

	def closeWin(self):
		"""Quit program."""
		print("Close the main window and quit program.")
		self.close()   # the correct way to quit, is as (upper right) window frame symbol "X" 
		return
		
# Methods for actions on the Scale-menu, which modify the view transform
	def scaleOne(self):
		"""Scale to 1, i.e. set the transform to identity matrix"""
		if not self.pixmap.isNull():
			self.view.setTransform(QTransform())  # identity
		return
	
	def scaleUp(self):
		"""Scale up the view by factor set by 'self.scaleUpFactor'"""
		if not self.pixmap.isNull():
			self.view.scale(self.scaleUpFactor, self.scaleUpFactor)  
		return
		
	def scaleDown(self):
		"""Scale down the view by factor set by 1.0/'self.scaleUpFactor'"""
		if not self.pixmap.isNull():
			self.view.scale(1.0/self.scaleUpFactor, 1.0/self.scaleUpFactor)  
		return
	
# Finally, some methods used as slots for common actions
	def resizeEvent(self, arg1):
		"""Make the size of the view follow any changes in the size of the main window.
		This method is a 'slot' that is called whenever the size of the main window changes.
		"""
		self.view.setGeometry( 0, 20, self.width(), self.height()-50 ) 
		self.status.setGeometry(5, self.height()-29, (self.width()//2)-10, 28) 
		self.posInfo.setGeometry((self.width()//2)+5, self.height()-29, (self.width()//2)-10, 28) 
		return
	
	def mousePressEvent(self, event):
		"""Just print which mouse button has been pressed in the main window.
		Note that the view catches most mouse events, so this does only happen
		when mouse is on the bottom of the main window; the status line.
		Normally we are fine if this function does nothing (is not included here).
		This method is a 'slot' that is called whenever a mouse button is pressed (in the main window).
		"""
		if (event.button() == Qt.LeftButton):
			print("MainWindow: Press LeftButton at:  " + str(event.pos()))
		if (event.button() == Qt.RightButton):
			print("MainWindow: Press RightButton at: " + str(event.pos()))
		return
	#end function mousePressEvent
#end class MainWindow

if __name__ == '__main__':
	print( f"{_appFileName}: (version {_version}), path for images is: {myPath}" )
	print( f"{_appFileName}: Using Qt {QT_VERSION_STR}" )
	img = cv2.imread("Image1crop.png") # filename is a string with the name of the file
	print( f"{img.dtype = }, {img.size = }, {img.ndim = }, {img.shape = }" )
	mainApp = QApplication(sys.argv)
	if (len(sys.argv) >= 2):
		fn = sys.argv[1]
		if not os.path.isfile(fn):
			fn = myPath + os.path.sep + fn   # alternative location
		mainWin = MainWindow(fName=fn)
	else:
		mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
