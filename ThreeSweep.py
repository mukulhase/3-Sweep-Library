import pdb
import os
import cv2
import numpy as np
import copy
from ply_template import TEMPLATE_PLY_FILE, TEMPLATE_VERTEX, TEMPLATE_FACES
import transformations as trans


def getPoint(point):
    if type(point) == list:
        return np.array(point)
    return point

def roundPoint(point):
    return [int(round(point[0])), int(round(point[1]))]

def generateEllipse(a, b, rot, count, center):
    theta = np.linspace(0, 2 * np.pi, count)
    r = 1 / np.sqrt((np.cos(theta)) ** 2 + (np.sin(theta)) ** 2)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    data = np.array([x, y])
    S = np.array([[a, 0], [0, b]])
    R = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]])
    T = np.dot(R, S)
    data = np.dot(T, data)
    data[1] += center[1]
    data[0] += center[0]
    return (data)


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
        self.state = 'Init'
        self.previousStates = []
        self.image = None
        self.iter = 0
        self.loadedimage = None
        self.straightAxis = False
        self.leftContour = None
        self.test = None
        self.rightContour = None
        self.objectPoints = np.array([])
        self.colorIndices = []
        self.sweepPoints = None
        self.primitivePoints = None
        self.axisResolution = 20
        self.primitiveDensity = 200
        self.gradient = None
        self.leftMajor = None
        self.rightMajor = None
        self.minor = None
        self.tolerance = 70
        self.rectPoint1 = None
        self.rectPoint2 = None
        self.weights = None
        self.inpaintiterations = 6
        pass

    def updateState(self, state=None):
        def loadedImage():
            self.leftContour = np.empty(((np.shape(self.image))[0]*10, 2))
            self.rightContour = np.empty(((np.shape(self.image))[0]*10, 2))
            self.sweepPoints = np.empty(((np.shape(self.image))[0]*10, 2))
            ## weights for distance of points
            self.weights = np.linspace(0, 1, self.tolerance)
            self.weights = np.append(self.weights, (1 - self.weights))

        def minor():
            if 'major' in self.previousStates:
                self.updateState('primitiveSelected')

        def major():
            if 'minor' in self.previousStates:
                self.updateState('primitiveSelected')

        def primitiveSelected():
            center = self.leftMajor + self.rightMajor
            minor = np.linalg.norm(center - self.minor)
            major = np.linalg.norm(self.leftMajor - self.rightMajor)
            self.ratio = major/(minor*2)
            self.iter += 1
            self.update3DPoints([self.leftContour[0], self.rightContour[0]])

        def startedSweep():
            pass

        if state:
            self.previousStates.append(self.state)
            self.state = state
        state = self.state
        if self.state in locals():
            locals()[self.state]()

    def loadImage(self, image):
        ''' Load image into module for processing '''
        if isinstance(image, str):
            self.filename = image
            self.image = cv2.imread(image,0)
        else:
            self.image = image
        self.updateState('loadedImage')
        pass

    def showImage(self):
        ''' Show image '''
        cv2.imshow('img', self.image)
        cv2.waitKey(0)
        pass

    def getEdges(self):
        ''' Run edge detection on the image '''
        if 'grabCutStarted' not in self.previousStates:
            self.gradient = auto_canny(self.image)
        self.gradient = cv2.blur(self.gradient, (2,2))
        return self.gradient
        pass

    def grabCut(self, topLeft, bottomRight):
        self.updateState('grabCutStarted')
        img_org = self.image
        img = img_org
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        width = abs(bottomRight[0] - topLeft[0])
        height = abs(bottomRight[1] - topLeft[1])
        rect = (topLeft[0], topLeft[1], width, height)
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img = img * mask2[:, :, np.newaxis]

        # img[np.where((img > [0, 0, 0]).all(axis=2))] = [255, 255, 255]
        imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,1,255,0)

        kernel = np.array([[0, 0, 1, 0, 0],
                           [0, 1, 1, 1, 0],
                           [1, 1, 1, 1, 1],
                           [0, 1, 1, 1, 0],
                           [0, 0, 1, 0, 0]], np.uint8)

        # Fill the mask.
        obj_seg = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        inpaint_mask = cv2.inpaint(img_org,obj_seg,self.inpaintiterations,cv2.INPAINT_TELEA)
        cv2.imwrite('output.png',cv2.flip( inpaint_mask.astype('uint8'), 1 ))

        self.gradient = auto_canny(obj_seg)
        self.updateState('grabCutEnded')

        pass

    def setMajor(self, point1, point2):
        ''' Set points for Major Axis '''
        self.leftMajor = point1
        self.rightMajor = point2
        self.leftContour[self.iter] = self.leftMajor.T
        self.rightContour[self.iter] = self.rightMajor.T
        self.updateState('major')
        pass
    def setMinor(self, point):
        self.minor = point
        self.sweepPoints[self.iter] = self.minor
        self.updateState('minor')
        pass

    def update3DPoints(self, newPoints):
        center = sum([np.array(roundPoint(x)) for x in newPoints]) / 2 - self.minor
        diff = newPoints[0] - newPoints[1]
        radius = ((diff[1]**2 + diff[0]**2)**(0.5))/2
        scaled = np.concatenate((self.primitivePoints, np.ones((1, np.shape(self.primitivePoints)[1]))), axis=0)
        theta = np.arctan2(diff[1], diff[0])
        zaxis = [0,1,0]
        rotation = trans.rotation_matrix(theta, zaxis)
        scale = trans.scale_matrix(radius)
        translation = trans.translation_matrix([center[0], 0, -center[1]])
        complete = trans.concatenate_matrices(translation, rotation, scale)
        affineTrans = np.matmul(complete, scaled)

        if (self.objectPoints.any()):
            self.objectPoints = np.concatenate((self.objectPoints,np.transpose(affineTrans)), axis=0)
        else:
            self.objectPoints = np.transpose(affineTrans)

    def getPointsBetween(self, p1, p2, quantity):
        rayx = np.linspace(float(p1[0]), float(p2[0]),quantity, dtype=int)
        rayy = np.linspace(float(p1[1]), float(p2[1]),quantity, dtype=int)
        return (rayx, rayy)

    def getEllipticalPointsBetween(self, first, second, count):
        distance = np.linalg.norm(first - second)
        center = (first + second) / 2
        minor = distance * self.ratio
        angle = np.arctan2((first[1] - second[1]), (first[0] - second[0]))
        a = generateEllipse(distance / 2, minor, angle, count, center)
        return a


    def addSweepPoint(self, point):
        ''' Called everytime another point on the axis is given by user '''

        def searchOut(point, slope):
            if abs(slope) > 1:
                p1= [point[0] - self.tolerance*(1.0/slope), point[1] - self.tolerance]
                p2= [point[0] + self.tolerance*(1.0/slope), point[1] + self.tolerance]
            else:
                p1= [point[0] - self.tolerance, point[1] - self.tolerance * slope]
                p2= [point[0] + self.tolerance, point[1] + self.tolerance * slope]
            (rayx, rayy) = self.getPointsBetween(p1, p2, self.tolerance*2)
            values = self.gradient[np.clip(rayy, 0, self.gradient.shape[0] - 1), np.clip(rayx, 0, self.gradient.shape[1] - 1)]
            values = values * self.weights
            index = np.argmax(values)
            if (values[index] != 0):
                return np.array([rayx[np.argmax(values)], rayy[np.argmax(values)]])
            return False

        def detectBoundaryPoints(axisPoint, shifted, l, r, anglediff):
            ''' Detect points on the boundary '''

            # offset by axis offset
            left = l + shifted
            right = r + shifted
            if self.straightAxis == False:
                c, s = np.cos(anglediff), np.sin(anglediff)
                rotMatrix = np.matrix([[c, -s], [s, c]])
                points = np.array([left,right])
                shiftedToOrigin = points - axisPoint
                rotated = np.matmul(shiftedToOrigin, rotMatrix)
                shiftedBack = rotated + axisPoint
                left = np.array([shiftedBack[0,0],shiftedBack[0,1]])
                right = np.array([shiftedBack[1,0],shiftedBack[1,1]])
            # get slope for ray search
            slopeLeft = axisPoint - left
            slopeRight = axisPoint - right
            if (slopeLeft == slopeRight).all():
                return
            slopeLeft = slopeLeft[1] / slopeLeft[0]
            slopeRight = slopeRight[1] / slopeRight[0]

            # search for contour points
            foundleft = searchOut([left[0], left[1]], slopeLeft)
            foundright = searchOut([right[0], right[1]], slopeRight)
            if (foundleft is False) or (foundright is False):
                return None
                # return [left, right]
            else:
                return [foundleft, foundright]
            pass

        def generateIntermediatePoints(oldPoint, newPoint):
            slope = oldPoint - newPoint
            slope = (slope[1]+0.0)/slope[0]
            slope = -(1.0/slope)
            (rayx, rayy) = self.getPointsBetween(newPoint, oldPoint, self.axisResolution)
            intermediatePoints = np.array([rayx, rayy], dtype=int).T.tolist()
            return list(map(lambda x:searchOut(x, slope),intermediatePoints))

        point = getPoint(point)
        shift = point - self.sweepPoints[self.iter - 1]
        if np.linalg.norm(shift) < self.axisResolution:
            return
        angle = np.arctan2(shift[1],shift[0])
        if self.state == 'primitiveSelected':
            self.previousangle = angle
            self.updateState('startedSweep')
        anglediff = self.previousangle - angle
        newPoints = detectBoundaryPoints(point, shift, self.leftContour[self.iter - 1],
                                         self.rightContour[self.iter - 1], anglediff)
        if newPoints == None:
            return
        self.previousangle = angle

        leftintermediate = generateIntermediatePoints(newPoints[0],self.leftContour[self.iter - 1])
        rightintermediate = generateIntermediatePoints(newPoints[1],self.rightContour[self.iter - 1])
        interNewPoints = filter(lambda x: (x[0] is not False) and (x[1] is not False), zip(leftintermediate, rightintermediate))
        for i in interNewPoints:
            self.sweepPoints[self.iter] = point.T
            self.leftContour[self.iter] = i[0]
            self.rightContour[self.iter] = i[1]
            self.iter += 1
            self.update3DPoints(i)
        self.sweepPoints[self.iter] = point.T
        self.leftContour[self.iter] = newPoints[0]
        self.rightContour[self.iter] = newPoints[1]
        self.iter += 1
        # self.colorIndices.append(getallPoints(newPoints[0], newPoints[1]))
        self.update3DPoints(newPoints)

    def generatePrimitive(self):
        ''' To select whether shape will be a circle or square(will be automated in the future) '''
        angles = np.linspace(0, 2 * np.pi, self.primitiveDensity)
        self.primitivePoints = np.array([np.cos(angles), np.sin(angles), np.zeros(self.primitiveDensity)],np.float64)
        return self.primitivePoints

    def updatePlot(self,points):
        def genEdges():
            topleft = [[x, x+self.primitiveDensity, x+self.primitiveDensity+1] for x in range(len(self.objectPoints)-self.primitiveDensity - 1)]
            topright = [[x + 1, x, x + self.primitiveDensity + 1] for x in range(len(self.objectPoints) - self.primitiveDensity -1)]
            return topleft + topright

        points = self.objectPoints
        triangles = np.array(genEdges())
        pass

    def generateTriSurf(self):
        def genEdges():
            topleft = [[x, x+self.primitiveDensity, x+self.primitiveDensity+1] for x in range(len(self.objectPoints)-self.primitiveDensity - 1)]
            topright = [[x + 1, x, x + self.primitiveDensity + 1] for x in range(len(self.objectPoints) - self.primitiveDensity -1)]
            return topleft + topright

        def generate_vertices(v, color):
            return TEMPLATE_VERTEX % (v[0], v[1], v[2], color[2], color[1], color[0], 255) # put colors where

        def generate_faces(f):
            return TEMPLATE_FACES % (3, f[0], f[1], f[2])

        points = self.objectPoints
        triangles = np.array(genEdges())
        points = points[:, :-1].astype(np.int)
        colorindices = np.array(self.colorIndices).T
        colors = self.loadedimage[colorindices[1], colorindices[0]]
        text = TEMPLATE_PLY_FILE % {
            "nPoints"  : points.shape[0],
            "nFacepoints" : triangles.shape[0],
            "points": "\n".join([generate_vertices(points[i], colors[i]) for i in range(points.shape[0])]),
            "facepoints" : "\n".join(generate_faces(f) for f in triangles)
        }

        text = text.replace(',', '').replace('{', '').replace('}', '').replace('{', '').replace('[', '').replace(']', '')
        text = "".join([s for s in text.strip().splitlines(True) if s.strip()])

        f = open("output.ply", "w")
        f.write(text)
        f.close()

    def end(self):
        # self.plot3DArray(self.objectPoints)
        def getallPoints(p1, p2):
            (interpolated1, interpolated2) = self.getPointsBetween(p1, p2, self.primitiveDensity / 2)
            semicolor = np.array([interpolated1, interpolated2], dtype=int).T.tolist()
            semicolor_reverse = copy.copy(semicolor)
            semicolor_reverse.reverse()
            return semicolor + semicolor_reverse
            #
            # points = self.getEllipticalPointsBetween(p1, p2, self.primitiveDensity)
            # points = np.array(points, dtype=int).T.tolist()
            # points = points[0:int(len(points)/2)]
            # points_reverse = copy.copy(points)
            # points_reverse.reverse()
            # return points + points_reverse

        for i in range(self.iter):
            self.colorIndices += getallPoints(self.leftContour[i], self.rightContour[i])
            # self.update3DPoints([self.leftContour[i],self.rightContour[i]])

        self.generateTriSurf()
        os.system('meshlabserver -i ./output.ply -o ./output.obj -s meshlab_ft.mlx -om vc vf vq vt fc ff fq fn wc wn wt')
        pass
