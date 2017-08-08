import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ThreeSweep():
    ''' Module class for Three Sweep '''

    def __init__(self):
        self.image = None
        self.contourPoints = []
        self.objectPoints = []
        self.axisResolution = 10
        self.primitiveDensity = 40
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

    def pickPrimitive(self):
        ''' To select whether shape will be a circle or square(will be automated in the future) '''
        self.primitiveDensity = 40
        angles = np.linspace(0, 2 * np.pi, self.primitiveDensity)
        return np.array([np.cos(angles), np.sin(angles), np.zeros(self.primitiveDensity)])

    def plot3DArray(self,x):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x[0], x[1], x[2])
        plt.show()

    def createSTL(self):
        ''' takes the object points in order and creates pairs of triangles, writes to a file'''
        pass
