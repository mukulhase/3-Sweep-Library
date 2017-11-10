#!/usr/bin/env python

import os
import shelve
import sys
import time

import cv2
import numpy as np
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import (Qt3DWindow, QFirstPersonCameraController)
from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DRender import QPointLight
from PyQt5.QtCore import (QPoint, QRect, QSize, Qt, QDir, pyqtSlot)
from PyQt5.QtGui import (QColor, QImage, QPainter)
from PyQt5.QtGui import QImageWriter, QPen, qRgb, qRgba, QVector3D
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (QAction, QColorDialog, QFileDialog, QLineEdit,
                             QInputDialog, QMainWindow, QMenu, QMessageBox, QStatusBar, QProgressBar, QPushButton,
                             QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QApplication, QOpenGLWidget)

from ThreeSweep import ThreeSweep, generateEllipse
from Viewer3D import SceneModifier

last_time = None

d = shelve.open('config.dat')

def getPoint(point):
    if type(point) == list:
        return np.array(point)
    return np.array([point.x(), point.y()])


class ScribbleArea(QOpenGLWidget):
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
        self.overLayed = {}
        self.setAttribute(Qt.WA_StaticContents)
        self.modified = False
        self.clicked = False
        self.state = {}
        self.stateUpdate({
            'init': False,
            'iteration': 0
        })
        self.myPenWidth = 5
        self.myPenColor = Qt.blue
        self.image = QImage().convertToFormat(5)
        self.image.fill(qRgba(255,0,0,0))
        self.imagePath = None
        self.lastPoint = QPoint()
        self.imagePainter = None
        self.edges = None
        self.app = None

    def revertAll(self):
        self.imagePainter.end()
        self.imagePainter = None
        self.edges = None
        self.firstPoint = None
        self.thirdPoint = None
        self.secondPoint = None
        self.loadImageToCanvas()
        self.update()
        self.threesweep = ThreeSweep()
        self.threesweep.loadImage(self.imagePath)


    def revert(self):
        state = (self.state)
        if self.state['currentStep'] == 'Start':
            self.self.threesweep = ThreeSweep()
            pass
        elif self.state['currentStep'] == 'FirstSweep':
            self.statusBar.showMessage('Click to add second point')
            self.edges = None
            self.firstPoint = None
            pass
        elif self.state['currentStep'] == 'SecondSweep':
            self.secondPoint = None
            pass
        elif self.state['currentStep'] == 'ThirdSweep':
            self.thirdPoint = None
            pass
        elif self.state['currentStep'] == "GrabCut":
            pass
        elif self.state['currentStep'] == "DrawRect":
            pass
        elif self.state['currentStep'] == "Complete":
            pass

    def stateUpdate(self, state=None):
        if state == None:
            pass
        else:
            self.state.update(state)
            print(self.state)
        state = (self.state)
        if self.state['init'] == False:
            self.threesweep = ThreeSweep()
            self.stateUpdate({'init': True, 'currentStep': 'Waiting for image'})
        elif self.state['currentStep'] == 'Start':
            self.statusBar.showMessage('Click to add a ThreeSweep point')
            self.saveDrawing()
            pass
        elif self.state['currentStep'] == 'FirstSweep':
            self.statusBar.showMessage('Click to add second point')
            self.edges = self.threesweep.getEdges()
            self.setPenColor(Qt.blue)
            self.plotPoint(self.firstPoint)
            self.plotPoint(self.secondPoint)
            self.plotPoint(self.thirdPoint)
            pass
        elif self.state['currentStep'] == 'SecondSweep':
            self.statusBar.showMessage('Drag to specify axis')
            self.setPenColor(Qt.red)
            self.threesweep.setMajor(getPoint(self.firstPoint), getPoint(self.secondPoint))
            self.plotPoint(self.firstPoint)
            self.plotPoint(self.secondPoint)
            self.plotPoint(self.thirdPoint)
            pass
        elif self.state['currentStep'] == 'ThirdSweep':
            # sweep1 = QVector2D(self.firstPoint - self.secondPoint)
            # sweep2 = QVector2D(self.thirdPoint - self.secondPoint)
            # cosine_angle = QVector2D.dotProduct(sweep1,sweep2) / (sweep1.length() * sweep2.length())
            # angle = acos(cosine_angle)*180/math.pi
            # if angle < 60:
            #     distance = (self.firstPoint - self.secondPoint)
            #     center = (self.firstPoint + self.secondPoint) / 2
            #     minor = (center - self.thirdPoint).y()
            #     distance = (distance.x()) ** 2 + (distance.y()) ** 2
            #     distance = distance ** 0.5
            #     self.imagePainter.drawEllipse(center, distance / 2, minor)
            # else:
            #     distance = (self.secondPoint - self.thirdPoint)
            #     distance = (distance.x()) ** 2 + (distance.y()) ** 2
            #     mag = distance ** 0.5
            #
            #     slope = (self.secondPoint.x() - self.thirdPoint.x()) / (self.secondPoint.y() - self.thirdPoint.y())
            #     fourthPoint = QtCore.QPoint(self.firstPoint.x() + (mag * slope) / (slope ** 2 + 1) ** 0.5,
            #                                 self.firstPoint.y() + mag / (slope ** 2 + 1) ** 0.5)
            #
            #     self.drawLineWithColor(self.firstPoint, self.secondPoint, temp=True)
            #     self.drawLineWithColor(self.secondPoint, self.thirdPoint, temp=True)
            #     self.drawLineWithColor(self.thirdPoint, fourthPoint, temp=True)
            #     self.drawLineWithColor(fourthPoint, self.firstPoint, temp=True)
            self.plotPoint(self.firstPoint)
            self.plotPoint(self.secondPoint)
            self.plotPoint(self.thirdPoint)
            self.threesweep.generatePrimitive()
            self.threesweep.setMinor(getPoint(self.thirdPoint))
            self.setPenColor(Qt.green)
            pass

        elif self.state['currentStep'] == "StartGrabcut":
            self.statusBar.showMessage('Grabcut: Select 2 points to specify the Bounding Box')
        elif self.state['currentStep'] == "GrabCut":
            self.threesweep.grabCut(getPoint(self.rectPoint1), getPoint(self.rectPoint2))
            self.statusBar.showMessage('Click on "start Sweep" to start')
        elif self.state['currentStep'] == "DrawRect":
            self.statusBar.showMessage('Grabcut: Select 2nd point to specify the bottom right')
        elif self.state['currentStep'] == "Complete":
            self.progressBar.setValue(75)
            self.restoreDrawing()
            self.update()
            self.statusBar.showMessage('Exporting... Please Wait')
            self.threesweep.export("object" + str(self.state['iteration']))
            self.statusBar.showMessage('Export Completed!')
            self.progressBar.setValue(100)
            ret = QMessageBox.question(self, "Scribble",
                                      "Would you like to add another object?",
                                      QMessageBox.Yes | QMessageBox.No )

            # window = MainWindow()
            # window.modifier.loadscene(self.state['iteration'] + 1)

            if ret == QMessageBox.Yes:
                self.imagePath = os.path.join(os.path.dirname(__file__),
                                              'output/uploaded.png')
                self.state['iteration'] += 1
                return self.revertAll()
            elif ret == QMessageBox.No:
                return False

    def openImage(self, fileName):
        self.threesweep.loadImage(fileName)
        self.imagePath = fileName
        self.loadImageToCanvas()

    def loadImageToCanvas(self):
        self.loadedImage = QImage()
        if not self.loadedImage.load(self.imagePath):
            return False
        newSize = self.loadedImage.size()
        self.resize(newSize)
        newSize = self.loadedImage.size().expandedTo(self.size())
        self.resizeImage(self.loadedImage, newSize)
        self.image = self.loadedImage.copy()
        self.modified = False
        self.stateUpdate({
            'currentStep': 'Start',
        })
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
        self.image.fill(qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.state['currentStep'] == 'Start':
                pass
            elif self.state['currentStep'] == 'FirstSweep':
                pass
            elif self.state['currentStep'] == 'SecondSweep':
                self.thirdPoint = event.pos()
                self.stateUpdate({
                    'currentStep': 'ThirdSweep'
                })
                pass
            elif self.state['currentStep'] == 'ThirdSweep':
                pass
            self.lastPoint = event.pos()
            self.clicked = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.state['currentStep'] == 'ThirdSweep':
            self.threesweep.addSweepPoint(getPoint(event.pos()))
            self.drawLineTo(event.pos())
            global last_time
            if not last_time:
                last_time = time.time()
            if (time.time() - last_time) > 0.1:
                last_time = time.time()
            self.contourPointsOverlay()
        elif self.state['currentStep'] == 'FirstSweep':
            self.drawLineWithColor(self.firstPoint, event.pos(), temp=True)
        elif self.state['currentStep'] == 'SecondSweep':
            self.drawLineWithColor(self.secondPoint, event.pos(), temp=True)
            first = getPoint(self.firstPoint)
            second = getPoint(self.secondPoint)
            distance = np.linalg.norm(first - second)
            center = (first + second) / 2
            minor = np.linalg.norm(center - getPoint(event.pos()))
            angle = np.arctan2((first[1] - second[1]),(first[0] - second[0]))
            a = generateEllipse(distance/2, minor, angle, 40 ,center)
            # self.imagePainter.drawEllipse(center, distance / 2, minor)
            for i in a.T:
                self.plotPoint(i, False)

        if self.state['currentStep'] == 'DrawRect':
            self.rectPoint2 = event.pos()
            self.drawGrabCutRectangle()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.state['currentStep'] == 'Start':
            self.firstPoint = event.pos()
            self.stateUpdate({'currentStep': 'FirstSweep'})
        elif self.state['currentStep'] == 'FirstSweep':
            self.secondPoint = event.pos()
            self.stateUpdate({'currentStep': 'SecondSweep'})
        elif self.state['currentStep'] == 'SecondSweep':
            # self.thirdPoint = event.pos()
            pass
        elif self.state['currentStep'] == 'ThirdSweep':
            self.stateUpdate({'currentStep': 'Complete'})
        elif self.state['currentStep'] == 'StartGrabcut':
            self.rectPoint1 = event.pos()
            self.stateUpdate({'currentStep': 'DrawRect'})
        elif self.state['currentStep'] == 'DrawRect':
            self.rectPoint2 = event.pos()
            self.stateUpdate({'currentStep': 'GrabCut'})
            self.update()
        elif self.state['currentStep'] == 'Complete':
            pass

        self.clicked = False

    def saveDrawing(self):
        self.oldimage = QImage(self.image)

    def contourPointsOverlay(self):
        def checkAndPlot(i):
            x = int(round(i[0]))
            y = int(round(i[1]))
            if ((x, y) in self.overLayed):
                pass
            else:
                self.plotPoint(QPoint(x, y))
                self.overLayed[x, y] = True

        for i in self.threesweep.leftContour[:self.threesweep.iter]:
            checkAndPlot(i)
        for i in self.threesweep.rightContour[:self.threesweep.iter]:
            checkAndPlot(i)
        for i in self.threesweep.colorIndices:
            checkAndPlot(i)
        if self.threesweep.test:
            for i in self.threesweep.test:
                checkAndPlot(i)

    def restoreDrawing(self):
        self.imagePainter.drawImage(QPoint(0, 0), self.oldimage)
        self.imagePainter.drawImage(0, 0, self.toQImage(self.edges))

    def paintEvent(self, event):
        painter = QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect, flags=Qt.NoOpaqueDetection)
        painter.end()
        pass

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def beforeDraw(self, temp):
        if not self.imagePainter:
            self.imagePainter = QPainter(self.image)

        if self.tempDrawing:
            self.restoreDrawing()
            if not temp:
                self.tempDrawing = False
            else:
                self.saveDrawing()
        else:
            if temp:
                self.tempDrawing = True

    def afterDraw(self, temp):
        if not temp:
            self.saveDrawing()
        else:
            pass

    def plotPoint(self, point, temp=False):
        self.beforeDraw(temp)
        if point is None:
            return
        self.imagePainter.setPen(QPen(self.myPenColor, 10,
                                      Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if type(point) == np.ndarray or type(point) == list:
            x = int(round(point[0]))
            y = int(round(point[1]))
            point = QPoint(x, y)
        self.imagePainter.drawPoint(point)
        self.afterDraw(temp)
        self.update()

    def drawLineWithColor(self, startPoint, endPoint, temp=False):
        self.beforeDraw(temp)
        self.imagePainter.setPen(QPen(self.myPenColor, self.myPenWidth,
                                      Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.imagePainter.drawLine(startPoint, endPoint)
        self.afterDraw(temp)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)
        self.update()

    def drawLineTo(self, endPoint, temp=False):
        self.drawLineWithColor(self.lastPoint, endPoint, temp=temp)

    def startSweep(self):
        self.stateUpdate({'currentStep': 'Start'})

    def drawGrabCutRectangle(self):
        self.drawRectangle(self.rectPoint1, self.rectPoint2, True)

    def drawRectangle(self, point1, point2, temp=False):
        if not point1 and not point2:
            return
        self.beforeDraw(temp)
        self.imagePainter.save()
        color = QColor(255, 0, 0)
        color.setNamedColor('#d4d4d4')
        self.imagePainter.setPen(color)
        self.imagePainter.drawRect(QRect(point1, point2))
        self.afterDraw(temp)
        self.imagePainter.restore()

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage
        painter.end()

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)

        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
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

    def startGrabCut(self):
        self.stateUpdate({'currentStep': 'StartGrabcut'})

    @pyqtSlot(int)
    def setAxisRotate(self, enabled):
        print(enabled)
        pass

    @pyqtSlot(str)
    def setModelDensity(self, text):
        self.threesweep.primitiveDensity = int(text)
        pass

    @pyqtSlot(str)
    def setModelResolution(self, text):
        self.threesweep.axisResolution = int(text)
        pass

    # Covert numpy array to QImage // error in line 4
    def toQImage(self, im, copy=False):
        gray_color_table = [qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QImage()
        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim
            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888)
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32)
                    return qim.copy() if copy else qim


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.saveAsActs = []

        self.scribbleArea = ScribbleArea()
        # layout = QGridLayout(self.centralWidget())
        # layout.addWidget(self.editor, 0, 0, 1, 3)
        # layout.addWidget(button, 1, 1, 1, 1)
        widget = QWidget()
        self.hLayout = QHBoxLayout(widget)
        self.vLayout = QVBoxLayout()
        self.vLayout.setAlignment(Qt.AlignTop)
        container = self.create3DWidget()
        self.hLayout.addWidget(self.scribbleArea, 3)
        self.hLayout.addWidget(container, 3)
        self.hLayout.addLayout(self.vLayout)

        widget.setWindowTitle("3D Viewer")

        # Show the window.
        widget.show()
        widget.resize(1200, 800)
        self.setCentralWidget(widget)
        self.createActions()
        self.createMenus()
        self.createToolBar()
        self.app = None
        self.setWindowTitle("3-Sweep")
        self.resize(1500, 1500)
        self.statusBar = QStatusBar()
        self.progressBar = QProgressBar()
        self.statusBar.addPermanentWidget(self.progressBar)
        self.setStatusBar(self.statusBar)
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setValue(100)
        self.scribbleArea.progressBar = self.progressBar
        self.scribbleArea.statusBar = self.statusBar

    def create3DWidget(self):
        view = Qt3DWindow()
        # view.defaultFramegraph().setClearColor(QColor(0x4d4d4f))
        container = QWidget.createWindowContainer(view)
        screenSize = view.screen().size()
        container.setMinimumSize(QSize(200, 100))
        container.setMaximumSize(screenSize)
        aspect = QInputAspect()
        view.registerAspect(aspect)
        # Root entity.
        self.rootEntity = QEntity()

        # Camera.
        cameraEntity = view.camera()

        cameraEntity.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        cameraEntity.setPosition(QVector3D(0.0, 24.0, -0.5))
        cameraEntity.setUpVector(QVector3D(0.0, 1.0, 0.0))
        cameraEntity.setViewCenter(QVector3D(0.0, 0.0, 0.0))

        # Light
        lightEntity = QEntity(self.rootEntity)
        light = QPointLight(lightEntity)
        light.setColor(QColor.fromRgbF(1.0, 1.0, 1.0, 1.0))
        light.setIntensity(1)
        lightEntity.addComponent(light)
        lightTransform = QTransform(lightEntity)
        lightTransform.setTranslation(QVector3D(10.0, 40.0, 0.0))
        lightEntity.addComponent(lightTransform)

        # For camera controls.
        camController = QFirstPersonCameraController(self.rootEntity)
        camController.setCamera(cameraEntity)

        # Set root object of the scene.
        view.setRootEntity(self.rootEntity)

        self.modifier = SceneModifier(self.rootEntity)

        moveLeft = QPushButton(text="Left")
        moveLeft.clicked.connect(self.modifier.transformLeft)
        moveLeft.setAutoRepeat(True)

        moveRight = QPushButton(text="Right")
        moveRight.clicked.connect(self.modifier.transformRight)
        moveRight.setAutoRepeat(True)

        moveUp = QPushButton(text="Up")
        moveUp.clicked.connect(self.modifier.transformUp)
        moveUp.setAutoRepeat(True)

        moveDown = QPushButton(text="Down")
        moveDown.clicked.connect(self.modifier.transformDown)
        moveDown.setAutoRepeat(True)

        scaleDown = QPushButton(text="Scale Down")
        scaleDown.clicked.connect(self.modifier.scaleDown)
        scaleDown.setAutoRepeat(True)

        scaleUp = QPushButton(text="Scale Up")
        scaleUp.clicked.connect(self.modifier.scaleUp)
        scaleUp.setAutoRepeat(True)

        # loadModel = QPushButton(text="Load Model")
        # loadModel.clicked.connect(self.modifier.loadscene)

        self.vLayout.addWidget(moveLeft)
        self.vLayout.addWidget(moveRight)
        self.vLayout.addWidget(moveUp)
        self.vLayout.addWidget(moveDown)
        self.vLayout.addWidget(scaleUp)
        self.vLayout.addWidget(scaleDown)
        # self.vLayout.addWidget(loadModel)
        return container

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def open(self, fname=None):
        print(fname)
        fileName = ""
        if self.maybeSave():
            if not fname:
                fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                                                          QDir.currentPath())
            else:
                fileName = fname
                pass
            if fileName:
                self.scribbleArea.openImage(fileName)
                image = cv2.imread(fileName)
                d['lastopened'] = fileName

    def openLast(self):
        if 'lastopened' in d:
            self.open(fname=d['lastopened'])

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)

    def penColor(self):
        newColor = QColorDialog.getColor(self.scribbleArea.penColor())
        if newColor.isValid():
            self.scribbleArea.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QInputDialog.getInt(self, "Scribble",
                                           "Select pen width:", self.scribbleArea.penWidth(), 1, 50, 1)
        if ok:
            self.scribbleArea.setPenWidth(newWidth)

    def about(self):
        QMessageBox.about(self, "About Scribble",
                          "<p>The <b>Scribble</b> example shows how to use "
                          "QMainWindow as the base widget for an application, and how "
                          "to reimplement some of QWidget's event handlers to receive "
                          "the events generated for the application's widgets:</p>"
                          "<p> We reimplement the mouse event handlers to facilitate "
                          "drawing, the paint event handler to update the application "
                          "and the resize event handler to optimize the application's "
                          "appearance. In addition we reimplement the close event "
                          "handler to intercept the close events before terminating "
                          "the application.</p>"
                          "<p> The example also demonstrates how to use QPainter to "
                          "draw an image in real time, as well as to repaint "
                          "widgets.</p>")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                               triggered=self.open)

        self.openRecentAct = QAction("&Open Recent...", self, shortcut="Ctrl+Shift+O",
                                     triggered=self.openLast)

        for format in QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QAction("&Print...", self,
                                triggered=self.scribbleArea.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               triggered=self.close)

        self.penColorAct = QAction("&Pen Color...", self,
                                   triggered=self.penColor)

        self.penWidthAct = QAction("Pen &Width...", self,
                                   triggered=self.penWidth)

        self.startSweepAct = QAction("&Start Sweeping..", self,
                                     triggered=self.scribbleArea.startSweep)

        self.drawRectAct = QAction("&Grab Cut", self,
                                   triggered=self.scribbleArea.startGrabCut)

        self.axisRotateAct = QCheckBox(checked=True, text="Axis Rotate")
        self.axisRotateAct.stateChanged.connect(self.scribbleArea.setAxisRotate)

        self.input_axisResolution = QLineEdit()
        self.input_axisResolution.setText("20")
        self.input_axisResolution.setMaximumWidth(40);
        self.input_axisResolution.textChanged.connect(self.scribbleArea.setModelResolution)

        self.input_primitiveDensity = QLineEdit()
        self.input_primitiveDensity.setText("200")
        self.input_primitiveDensity.setMaximumWidth(40);
        self.input_primitiveDensity.textChanged.connect(self.scribbleArea.setModelDensity)


        self.clearScreenAct = QAction("&Clear Screen", self, shortcut="Ctrl+L",
                                      triggered=self.scribbleArea.clearImage)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                                  triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.saveAsMenu = QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openRecentAct)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)

        helpMenu = QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def createToolBar(self):

        tb = self.addToolBar('Image Processing')
        tb.addAction(self.drawRectAct)
        tb.addAction(self.startSweepAct)
        tb.addSeparator()
        tb.addSeparator()
        tb.addWidget(self.axisRotateAct)
        tb.addSeparator()
        tb.addSeparator()
        tb.addWidget(self.input_axisResolution)
        tb.addWidget(self.input_primitiveDensity)

    def maybeSave(self):
        if self.scribbleArea.isModified():
            ret = QMessageBox.warning(self, "Scribble",
                                      "The image has been modified.\n"
                                      "Do you want to save your changes?",
                                      QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat):
        initialPath = QDir.currentPath() + '/untitled.' + fileFormat

        fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                                                  "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.saveImage(fileName, fileFormat)

        return False

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
