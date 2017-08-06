import cv2
import numpy as np


class ThreeSweep():
    ''' Module class for Three Sweep '''

    def __init__(self):
        self.image = None
        self.contourPoints = []
        self.objectPoints = []
        self.axisResolution = 10
        pass

    def loadImage(self, filename):
        ''' Load image into module for processing '''
        self.image = cv2.imread(filename, 0)
        pass

    def getEdges(self):
        ''' Run edge detection on the image '''
        pass

    def setMajor(self):
        ''' Set points for Major Axis '''
        pass

    def addSweepPoint(self):
        ''' Called everytime another point on the axis is given by user '''

        def detectBoundaryPoints(axisPoint, slope):
            ''' Detect points on the boundary '''
            pass

    def createSTL(self):
        ''' takes the object points in order and creates pairs of triangles, writes to a file'''
        pass
