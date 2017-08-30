import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sympy import *
from sympy.geometry import *
from stl import mesh

from mpl_toolkits.mplot3d import Axes3D
import ipdb


def getPoint(point):
    if type(point) == list:
        return Point(point[0], point[1])
    return Point(point.x(), point.y())


def roundPoint(point):
    return [int(round(point.x)), int(round(point.y))]

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

class ThreeSweep():
    ''' Module class for Three Sweep '''

    def __init__(self):
        self.image = None
        self.leftContour = []
        self.rightContour = []
        self.objectPoints = np.array([])
        self.sweepPoints = []
        self.primitivePoints = []
        self.axisResolution = 10
        self.primitiveDensity = 20
        self.gradient = None
        self.leftMajor = None
        self.rightMajor = None
        self.minor = None
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.axis('equal')
        pass

    def loadImage(self, image):
        ''' Load image into module for processing '''
        self.filename = image
        if type(image) is unicode:
            self.image = cv2.imread(image,0)
        else:
            self.image = image
        pass

    def showImage(self):
        ''' Show image '''
        cv2.imshow('img', self.image)
        cv2.waitKey(0)
        pass

    def getEdges(self):
        ''' Run edge detection on the image '''
        self.gradient = auto_canny(self.image)
        return self.gradient
        pass

    def matlabCode(self):
        def getaxis(ax_contours):
            points = ax_contours[0][0]
            for i in range(1, len(ax_contours)):
                points = np.vstack((points, ax_contours[i][0]))

            # points = np.fliplr(points)
            # temp = [tuple(row) for row in points]
            # unique_points = np.unique(temp)
            unique_points = points

            h = len(unique_points)

            A = np.zeros((np.max(unique_points[:, 1]) + 1, 1), np.uint8)
            for i in range(0, h):
                A[unique_points[i, 1]] = unique_points[i, 0]

            col = np.arange(len(A))

            return np.column_stack((A, col))

        def getContours(input):
            im2, contours, hierarchy = cv2.findContours(input, 1, 2)
            cnt = contours[0] # return this instead?
            epsilon = 0.1 * cv2.arcLength(cnt, True)
            return cv2.approxPolyDP(cnt, epsilon, True), contours

        def imfill(im_in):
            th, im_th = cv2.threshold(im_in, 100, 255, cv2.THRESH_BINARY)
            im_floodfill = im_th.copy()

            # Mask used to flood filling. Notice the size needs to be 2 pixels than the image.
            h, w = im_th.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)

            cv2.floodFill(im_floodfill, mask, (0, 0), 255)
            im_floodfill_inv = cv2.bitwise_not(im_floodfill)

            # Combine the two images to get the foreground.
            im_out = im_th | im_floodfill_inv
            return im_out

        self.image[np.where((self.image == [255, 255, 255]).all(axis=2))] = [0, 0, 0]

        obj_axis = self.image.copy()
        obj_border = self.image.copy()

        obj_axis[np.where((obj_axis == [0, 0, 255]).all(axis=2))] = [0, 0, 0]
        obj_axis[np.where((obj_axis == [255, 0, 0]).all(axis=2))] = [255, 255, 255]

        obj_border[np.where((obj_border == [255, 0, 0]).all(axis=2))] = [0, 0, 0]
        obj_border[np.where((obj_border == [0, 0, 255]).all(axis=2))] = [255, 255, 255]

        # Structuring Element (Disk)
        kernel = np.array([[0, 0, 1, 0, 0],
                      [0, 1, 1, 1, 0],
                      [1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 0],
                      [0, 0, 1, 0, 0]], np.uint8)

        # Fill the object and get the contour points.
        ax_close = cv2.morphologyEx(cv2.cvtColor(obj_axis, cv2.COLOR_BGR2GRAY), cv2.MORPH_CLOSE, kernel)
        ax_approx, ax_contours = getContours(ax_close)

        ax_points = getaxis(ax_contours) # till line 26 in fakecombine.m

        border_close = cv2.morphologyEx(cv2.cvtColor(obj_border, cv2.COLOR_BGR2GRAY), cv2.MORPH_CLOSE, kernel)
        border_fill = imfill(border_close)

        bord_approx, bord_contours = getContours(border_fill)

        # cv2.drawContours(obj_axis, ax_points, -1, (0, 255, 0), 3)
        # cv2.imshow('img', obj_axis)
        # cv2.waitKey(0)

    def setMajor(self, point1, point2):
        ''' Set points for Major Axis '''
        self.leftMajor = getPoint(point1)
        self.rightMajor = getPoint(point2)
        self.leftContour.append(self.leftMajor)
        self.rightContour.append(self.rightMajor)
        pass
    def setMinor(self, point):
        self.minor = getPoint(point)
        self.sweepPoints.append(self.minor)
        pass

    def update3DPoints(self, newPoints):
        center = sum([np.array(roundPoint(x)) for x in newPoints]) / 2
        diff = newPoints[0] - newPoints[1]
        radius = ((diff.y**2 + diff.x**2)**(0.5))/2
        scaled = np.concatenate((self.primitivePoints, np.ones((1, np.shape(self.primitivePoints)[1]))), axis=0)
        # scaled = np.append(self.primitivePoints,np.ones(np.shape(self.primitivePoints)[1]))
        theta = atan2(diff.y, diff.x)
        transformation = np.array([
            [radius, 0, 0, center[0]],
            [0, radius, 0, 0],
            [0, 0, 1, -center[1]],
            [0, 0, 0, 1]], dtype=np.float)
        rotation = np.array([
            [cos(theta), 0, sin(theta), 0],
            [0, 1, 0, 0],
            [-sin(theta), 0, cos(theta), 0],
            [0, 0, 0, 1]],dtype=np.float)
        tr = np.matmul(transformation,rotation)
        affineTrans = np.matmul(tr, scaled)
        if (self.objectPoints.any()):
            self.objectPoints = np.concatenate((self.objectPoints,np.transpose(affineTrans)), axis=0)
        else:
            self.objectPoints = np.transpose(affineTrans)
        # self.updatePlot(np.transpose(affineTrans))

    def addSweepPoint(self, point):
        ''' Called everytime another point on the axis is given by user '''

        def detectBoundaryPoints(axisPoint, slope, left, right):
            ''' Detect points on the boundary '''

            def searchOut(point, slope, inv=False, k=1):
                if inv:
                    k = -k
                try:
                    if (slope > 1):
                        temp = point + Point(k * slope, k * 1)
                    else:
                        temp = point + Point(k * 1, k * slope)
                except:
                    return
                if inv:
                    k = -k
                index = roundPoint(temp)
                if k > 35:
                    return None
                if (self.gradient[index[1]][index[0]] > 0):
                    return temp
                else:
                    if inv:
                        return searchOut(point, slope, False, k + 1)
                    else:
                        return searchOut(point, slope, True, k)

            # offset by axis offset
            left += slope
            right += slope

            # store as datatype
            left = Point(left)
            right = Point(right)
            axisPoint = Point(axisPoint)

            # get slope for ray search
            slopeLeft = axisPoint - left
            slopeRight = axisPoint - right
            slopeLeft = slopeLeft.y / slopeLeft.x
            slopeRight = slopeRight.y / slopeRight.x

            # search for contour points
            foundleft = searchOut(left, slopeLeft)
            foundright = searchOut(right, slopeRight)
            if (foundleft == None) or (foundright == None):
                return [left, right]
            else:
                return [foundleft, foundright]
            pass

        point = getPoint(point)
        direction = point - self.sweepPoints[-1]
        newPoints = detectBoundaryPoints(point, direction, self.leftContour[-1], self.rightContour[-1])
        self.sweepPoints.append(point)
        self.leftContour.append(newPoints[0])
        self.rightContour.append(newPoints[1])
        self.update3DPoints(newPoints)

    def pickPrimitive(self):
        ''' To select whether shape will be a circle or square(will be automated in the future) '''
        self.primitiveDensity = 40
        angles = np.linspace(0, 2 * np.pi, self.primitiveDensity)
        self.primitivePoints = np.array([np.cos(angles), np.sin(angles), np.zeros(self.primitiveDensity)],np.float64)
        return self.primitivePoints

    def plot3DArray(self,x):
        self.ax.plot_wireframe(x[:,0], x[:,1], x[:,2])
        plt.show()
        pass

    def updatePlot(self,points):
        #background = fig.canvas.copy_from_bbox(ax.bbox)
        self.ax.plot(points[:,0],points[:,1],points[:,2])
        plt.draw()
        plt.pause(0.0001)
        pass

    def generateTriSurf(self):
        def genEdges():
            topleft = [[x, x+self.primitiveDensity, x+self.primitiveDensity+1] for x in range(len(self.objectPoints)-self.primitiveDensity - 1)]
            topright = [[x + 1, x, x + self.primitiveDensity + 1] for x in range(len(self.objectPoints) - self.primitiveDensity -1)]
            return topleft + topright
        points = self.objectPoints
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        plt.axis('equal')
        triangles = np.array(genEdges())
        ax.plot_trisurf(points[:,0],points[:,1],points[:,2], triangles = triangles)
        plt.axis('equal')
        ax.axis('equal')
        plt.show()
        # ipdb.set_trace()
        points = points[:,:-1]
        cube = mesh.Mesh(np.zeros(triangles.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(triangles):
            for j in range(3):
                cube.vectors[i][j] = points[int(floor(f[j])), :]
        cube.save('output.stl')

    def end(self):
        # self.plot3DArray(self.objectPoints)
        self.generateTriSurf()
        pass
    def createSTL(self):
        ''' takes the object points in order and creates pairs of triangles, writes to a file'''
        pass
