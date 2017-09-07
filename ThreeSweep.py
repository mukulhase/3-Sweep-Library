import pdb

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.interactive = True


TEMPLATE_PLY_FILE = u"""\
{
ply,
format ascii 1.0,
comment VCGLIB generated,
element vertex %(nPoints)d,
property float x,
property float y,
property float z,
property uchar red,
property uchar green,
property uchar blue,
property uchar alpha,
element face %(nFacepoints)d,
property list uchar int vertex_indices,
end_header,
[%(points)s],
[%(facepoints)s]
}
"""
TEMPLATE_VERTEX = "%f %f %f %d %d %d %d"
TEMPLATE_FACES = "%d %d %d %d"

def getPoint(point):
    if type(point) == list:
        return np.array(point)
    return np.array([point.x(), point.y()])


def roundPoint(point):
    return [int(round(point[0])), int(round(point[1]))]

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
        self.leftContour = None
        self.rightContour = None
        self.objectPoints = np.array([])
        self.colorIndices = []
        self.sweepPoints = None
        self.primitivePoints = None
        self.axisResolution = 10
        self.primitiveDensity = 10000
        self.gradient = None
        self.leftMajor = None
        self.rightMajor = None
        self.minor = None
        self.tolerance = 70
        pass

    def updateState(self, state=None):
        def loadedImage():
            self.leftContour = np.empty(((np.shape(self.image))[0], 2))
            self.rightContour = np.empty(((np.shape(self.image))[0], 2))
            self.sweepPoints = np.empty(((np.shape(self.image))[0], 2))

        def minor():
            if 'major' in self.previousStates:
                self.updateState('primitiveSelected')

        def major():
            if 'minor' in self.previousStates:
                self.updateState('primitiveSelected')

        def primitiveSelected():
            self.iter += 1
            self.update3DPoints([self.leftContour[0], self.rightContour[0]])

        if state:
            self.previousStates.append(self.state)
            self.state = state
        state = self.state
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
        self.gradient = auto_canny(self.image)
        return self.gradient
        pass

    def setMajor(self, point1, point2):
        ''' Set points for Major Axis '''
        self.leftMajor = getPoint(point1)
        self.rightMajor = getPoint(point2)
        self.leftContour[self.iter] = self.leftMajor.T
        self.rightContour[self.iter] = self.rightMajor.T
        self.updateState('major')
        pass
    def setMinor(self, point):
        self.minor = getPoint(point)
        self.sweepPoints[self.iter] = self.minor
        self.updateState('minor')
        pass

    def update3DPoints(self, newPoints):
        center = sum([np.array(roundPoint(x)) for x in newPoints]) / 2
        diff = newPoints[0] - newPoints[1]
        radius = ((diff[1]**2 + diff[0]**2)**(0.5))/2
        scaled = np.concatenate((self.primitivePoints, np.ones((1, np.shape(self.primitivePoints)[1]))), axis=0)
        # scaled = np.append(self.primitivePoints,np.ones(np.shape(self.primitivePoints)[1]))
        theta = np.arctan2(diff[1], diff[0])
        transformation = np.array([
            [radius, 0, 0, center[0]],
            [0, radius, 0, 0],
            [0, 0, 1, -center[1]],
            [0, 0, 0, 1]], dtype=np.float)
        rotation = np.array([
            [np.cos(theta), 0, np.sin(theta), 0],
            [0, 1, 0, 0],
            [-np.sin(theta), 0, np.cos(theta), 0],
            [0, 0, 0, 1]],dtype=np.float)
        tr = np.matmul(transformation,rotation)
        affineTrans = np.matmul(tr, scaled)
        if (self.objectPoints.any()):
            self.objectPoints = np.concatenate((self.objectPoints,np.transpose(affineTrans)), axis=0)
        else:
            self.objectPoints = np.transpose(affineTrans)
        # self.updatePlot(np.transpose(affineTrans))

    def getallPoints(self, p1, p2):
        ''' Get 20 points between p1 and p2'''
        line = []

        x0 = int(p1[0])
        y0 = int(p1[1])
        x1 = int(p2[0])
        y1 = int(p2[1])
        # return [[(x0+x1)/2, (y0+y1)/2]] * self.primitiveDensity

        dx = x1 - x0
        dy = y1 - y0
        D = 2 * dy - dx
        y = y0
        for x in range(x0, x1 + 1):
            line.append([x, y])
            if D > 0:
                y = y + 1
                D = D - 2 * dx
            D = D + 2 * dy
        if len(line) > 1:
            line = np.array(line)
            interpolated1 = np.interp(np.linspace(0, len(line), self.primitiveDensity / 2),
                                      np.linspace(0, len(line) - 1, len(line)), line[:, 0])
            interpolated2 = np.interp(np.linspace(0, len(line), self.primitiveDensity / 2),
                                      np.linspace(0, len(line) - 1, len(line)), line[:, 1])
            interpolated = np.array([interpolated1, interpolated2], dtype=int)
            return np.transpose(interpolated).tolist() * 2
        else:
            return [[x0, y0]] * self.primitiveDensity

    def addSweepPoint(self, point):
        ''' Called everytime another point on the axis is given by user '''

        def detectBoundaryPoints(axisPoint, slope, left, right):
            ''' Detect points on the boundary '''

            def gaussian(x, mu, sig):
                return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

            ## weights for distance of points
            weights = np.linspace(0,1,self.tolerance)
            weights = np.append(weights,(1 - weights))

            def searchOut(point, slope, inv=False, k=1):
                if (slope > 1):
                    rayx = np.linspace(float(point[0] - self.tolerance * slope), float(point[1] + self.tolerance * slope), self.tolerance * 2, dtype=int)
                    rayy = np.linspace(float(point[0] - self.tolerance), float(point[1] + self.tolerance), self.tolerance * 2, dtype=int)
                else:
                    rayy = np.linspace(float(point[1] - self.tolerance * slope), float(point[1] + self.tolerance * slope), self.tolerance * 2, dtype=int)
                    rayx = np.linspace(float(point[0] - self.tolerance), float(point[0] + self.tolerance), self.tolerance * 2, dtype=int)

                try:
                    values = self.gradient[
                        np.clip(rayy, 0, self.gradient.shape[0] - 1), np.clip(rayx, 0, self.gradient.shape[1] - 1)]
                except:
                    pdb.set_trace()
                values = values*weights
                index = np.argmax(values)
                if(values[index] != 0):
                    return np.array([rayx[np.argmax(values)], rayy[np.argmax(values)]])

            # offset by axis offset
            left += slope
            right += slope
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
            if (foundleft is None) or (foundright is None):
                return [left, right]
            else:
                return [foundleft, foundright]
            pass


        point = getPoint(point)
        direction = point - self.sweepPoints[self.iter - 1]
        newPoints = detectBoundaryPoints(point, direction, self.leftContour[self.iter - 1],
                                         self.rightContour[self.iter - 1])
        if newPoints == None:
            return
        self.sweepPoints[self.iter] = point.T
        self.leftContour[self.iter] = newPoints[0]
        self.rightContour[self.iter] = newPoints[1]
        self.iter += 1
        # self.colorIndices.append(getallPoints(newPoints[0], newPoints[1]))
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
        def genEdges():
            topleft = [[x, x+self.primitiveDensity, x+self.primitiveDensity+1] for x in range(len(self.objectPoints)-self.primitiveDensity - 1)]
            topright = [[x + 1, x, x + self.primitiveDensity + 1] for x in range(len(self.objectPoints) - self.primitiveDensity -1)]
            return topleft + topright

        points = self.objectPoints
        ax = self.fig.gca(projection='3d')
        triangles = np.array(genEdges())
        # if 'surf' in self:
        #     self.surf.remove()
        self.surf = ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2], triangles=triangles)
        plt.draw()
        plt.pause(0.0001)
        #self.ax.plot(points[:,0],points[:,1],points[:,2])
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
        for i in range(self.iter):
            self.colorIndices += self.getallPoints(self.leftContour[i], self.rightContour[i])
            # self.update3DPoints([self.leftContour[i],self.rightContour[i]])
        self.generateTriSurf()
        pass
