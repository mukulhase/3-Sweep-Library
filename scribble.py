 #!/usr/bin/env python
# These are only needed for Python v2 but are harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
import copy
import cv2
import numpy as np

from PyQt4 import QtCore, QtGui

class ScribbleArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)
        self.tempDrawing = False
        self.setMouseTracking(True)
        self.firstPoint = None
        self.secondPoint = None
        self.thirdPoint = None
        self.rectPoint1 = None
        self.rectPoint2 = None
        self.contourPoints = []
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.clicked = False
        self.state = 'Start'
        self.myPenWidth = 5
        self.myPenColor = QtCore.Qt.blue
        self.image = QtGui.QImage()
        self.imagePath = None
        self.lastPoint = QtCore.QPoint()
        self.imagePainter = None

    def stateUpdate(self, state=None):
        if state == None:
            pass
        else:
            self.state = state
        state = (self.state)
        self.plotPoint(self.firstPoint)
        self.plotPoint(self.secondPoint)
        self.plotPoint(self.thirdPoint)

    def openImage(self, fileName):
        loadedImage = QtGui.QImage()
        if not loadedImage.load(fileName):
            return False
        self.imagePath = fileName
        newSize = loadedImage.size()
        self.resize(newSize)
        ##newSize = loadedImage.size().expandedTo(self.size())
        ##self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = False
        self.update()
        return True

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(QtGui.qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.state == 'Start':
                pass
            elif self.state == 'FirstSweep':
                pass
            elif self.state == 'SecondSweep':
                self.stateUpdate('ThirdSweep')
                self.thirdPoint = event.pos()
                pass
            elif self.state == 'ThirdSweep':
                pass
            elif self.state == 'DrawRect':
                self.rectPoint1 = event.pos()
            self.lastPoint = event.pos()
            self.clicked = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.state == 'ThirdSweep' and self.clicked:
            self.drawLineTo(event.pos())

        if self.state == 'FirstSweep':
            self.drawLineWithColor(self.firstPoint, event.pos(), temp=True)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.state == 'ThirdSweep':
            self.drawLineTo(event.pos())
        if self.state == 'Start':
            self.firstPoint = event.pos()
            self.stateUpdate('FirstSweep')
        elif self.state == 'FirstSweep':
            self.secondPoint = event.pos()
            self.stateUpdate('SecondSweep')
        elif self.state == 'SecondSweep':
            pass
        elif self.state == 'ThirdSweep':
            self.stateUpdate('Complete')
        elif self.state == 'DrawRect':
            self.rectPoint2 = event.pos()
            self.drawRectangles()
            self.stateUpdate('Complete')
        elif self.state == 'Complete':
            self.restoreDrawing()
            self.update()

        self.clicked = False

    def saveDrawing(self):
        pass
        ##self.oldimage = QtGui.QImage(self.image)

    def restoreDrawing(self):
        pass
        ##self.imagePainter.end()
        ##self.imagePainter= QtGui.QPainter(self.oldimage)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(event.rect(), self.image)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width(), self.image.width())
            newHeight = max(self.height(), self.image.height())
            self.resizeImage(self.image, QtCore.QSize(newWidth, newHeight))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def beforeDraw(self,temp):
        if not self.imagePainter:
            self.imagePainter = QtGui.QPainter(self.image)

        if self.tempDrawing:
            self.restoreDrawing()
            if not temp:
                self.tempDrawing = False
            else:
                self.saveDrawing()
        else:
            if temp:
                self.tempDrawing = True

    def plotPoint(self, point, temp = False):
        self.beforeDraw(temp)
        if not point:
            return

        self.imagePainter.setPen(QtGui.QPen(self.myPenColor, 10,
                                  QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.imagePainter.drawPoint(point)
        if not temp:
            print 'saved'
            self.saveDrawing()
        else:
            pass
        self.update()

    def drawLineWithColor(self, startPoint, endPoint, temp=False):
        if temp:
            return
        self.beforeDraw(temp)
        self.imagePainter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                                  QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.imagePainter.drawLine(startPoint, endPoint)
        if not temp:
            self.saveDrawing()
        else:
            pass
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QtCore.QPoint(endPoint)
        self.update()

    def drawLineTo(self, endPoint, temp=False):
        self.drawLineWithColor(self.lastPoint,endPoint,temp=temp)

    def drawRectangles(self):
        self.beforeDraw(False)
        color = QtGui.QColor(255, 0, 0)
        color.setNamedColor('#d4d4d4')
        self.imagePainter.setPen(color)

        # self.imagePainter.setBrush(QtGui.QColor(200, 0, 0))
        width = abs(self.rectPoint2.x()-self.rectPoint1.x())
        height = abs(self.rectPoint2.y()-self.rectPoint1.y())
        self.imagePainter.drawRect(self.rectPoint1.x(), self.rectPoint1.y(), width, height)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(QtGui.qRgb(255, 255, 255))
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.image = newImage

    def print_(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

        printDialog = QtGui.QPrintDialog(printer, self)
        if printDialog.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth

    def rectDraw(self):
        self.stateUpdate('DrawRect')

    # Covert numpy array to QImage // error in line 4
    def toQImage(im, copy=False):
        gray_color_table = [QtGui.qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QtGui.QImage()
        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim
            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_RGB888);
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_ARGB32);
                    return qim.copy() if copy else qim

    def grabCut(self):
        img = cv2.imread(self.imagePath)
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        width = abs(self.rectPoint2.x() - self.rectPoint1.x())
        height = abs(self.rectPoint2.y() - self.rectPoint1.y())
        rect = (self.rectPoint1.x(), self.rectPoint1.y(), width, height)
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img = img * mask2[:, :, np.newaxis]
        cv2.imwrite('grabcuted.png', img)
        # im = np.require(img, np.uint8, 'C')
        # qImage = self.toQImage(im)
        self.openImage('grabcuted.png')

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.saveAsActs = []
        self.appState = 'Start'
        self.scribbleArea = ScribbleArea()
        self.setCentralWidget(self.scribbleArea)
        self.createActions()
        self.createMenus()
        self.createToolBar()
        self.setWindowTitle("3-Sweep")
        self.resize(1500, 1500)

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def open(self):
        if self.maybeSave():
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                    QtCore.QDir.currentPath())
            if fileName:
                self.scribbleArea.openImage(fileName)

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)

    def penColor(self):
        newColor = QtGui.QColorDialog.getColor(self.scribbleArea.penColor())
        if newColor.isValid():
            self.scribbleArea.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QtGui.QInputDialog.getInteger(self, "Scribble",
                "Select pen width:", self.scribbleArea.penWidth(), 1, 50, 1)
        if ok:
            self.scribbleArea.setPenWidth(newWidth)

    def about(self):
        QtGui.QMessageBox.about(self, "About 3-Sweep",
                "To be added")

    def stateUpdate(self, state=None):
        if state == None:
            pass
        else:
            self.appState = state
        state = (self.appState)
        self.scribbleArea.state = state
        if state=='start':
            pass
        elif state=='sweep':
            pass

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        for format in QtGui.QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QtGui.QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QtGui.QAction("&Print...", self,
                triggered=self.scribbleArea.print_)

        self.exitAct = QtGui.QAction("&Exit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.penColorAct = QtGui.QAction("&Pen Color...", self,
                triggered=self.penColor)

        self.penWidthAct = QtGui.QAction("Pen &Width...", self,
                triggered=self.penWidth)

        self.drawRectAct = QtGui.QAction("&Draw Rectangle", self,
                                         triggered=self.scribbleArea.rectDraw)

        self.grabCutAct = QtGui.QAction("&Grab Cut", self,
                                         triggered=self.scribbleArea.grabCut)

        self.clearScreenAct = QtGui.QAction("&Clear Screen", self,
                shortcut="Ctrl+L", triggered=self.scribbleArea.clearImage)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.saveAsMenu = QtGui.QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QtGui.QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QtGui.QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)

        helpMenu = QtGui.QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def createToolBar(self):

        drawingMenu = QtGui.QToolBar("&Draw",self)
        drawingMenu.addAction(self.drawRectAct)
        drawingMenu.addAction(self.grabCutAct)

        self.addToolBar(drawingMenu)

    def maybeSave(self):
        if self.scribbleArea.isModified():
            ret = QtGui.QMessageBox.warning(self, "Scribble",
                        "The image has been modified.\n"
                        "Do you want to save your changes?",
                        QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                        QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat):
        initialPath = QtCore.QDir.currentPath() + '/untitled.' + fileFormat

        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As",
                initialPath,
                "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.saveImage(fileName, fileFormat)

        return False


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
