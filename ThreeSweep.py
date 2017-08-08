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
        self.image = cv2.imread(filename)
        pass

    def showImage(self):
        ''' Show image '''
        cv2.imshow('img', self.image)
        cv2.waitKey(0)
        pass

    def getEdges(self):
        ''' Run edge detection on the image '''
        pass

    def matlabCode(self):

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

        print ax_contours
        # ax_contours = np.unique(np.fliplr(ax_contours), axis=0)

        # h = len(ax_contours)
        # print h, w
        # A = np.zeros((h,1), np.uint8)
        # for i in range(0,h):
        #     A[i] = ax_contours[i,1]
        #
        # points = np.array([[A[h-1], h-1]])
        # for i in range(0, h):
        #     i = h-1-i
        #     points = np.vstack((points, [A[i], i]))
        # print points

        # A(M(:, 2)) = M(:, 1);
        # points = [A;1:size(A, 2)]';
        # points = points(end:-1:1,:);

        border_close = cv2.morphologyEx(cv2.cvtColor(obj_border, cv2.COLOR_BGR2GRAY), cv2.MORPH_CLOSE, kernel)
        border_fill = imfill(border_close)

        bord_approx, bord_contours = getContours(border_fill)

        # cv2.drawContours(obj_contour, contours, -1, (0, 255, 0), 3)
        # cv2.imshow('img', obj_contour)
        # cv2.waitKey(0)

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
