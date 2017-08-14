#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# test.py
#
# Test program for the simple GL Viewer.
#
# Copyright (c) 2011, Arne Schmitz <arne.schmitz@gmx.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#===============================================================================

import sys
from PyQt4 import QtGui
from PyGLWidget import PyGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

# Import the Model3D class
import model3d

#===============================================================================

class testGLWidget(PyGLWidget):
    def paintGL(self):
        PyGLWidget.paintGL(self)
        # glBegin(GL_TRIANGLES)
        # glColor3f(1,0,0)
        # glVertex3f(0,0,0)
        # glColor3f(0,1,0)
        # glVertex3f(0,1,0)
        # glColor3f(0,0,1)
        # glVertex3f(1,1,0)
        # glEnd()
        # Read the model
        tank_model = model3d.Model3D()
        tank_model.read_obj('mytank.obj')
        tank_model.draw_quick()

#===============================================================================
# Main
#===============================================================================

app = QtGui.QApplication(sys.argv)
mainWindow = testGLWidget()
mainWindow.show()
mainWindow.raise_() # Need this at least on OS X, otherwise the window ends up in background
sys.exit(app.exec_())

#===============================================================================
#
# Local Variables:
# mode: Python
# indent-tabs-mode: nil
# End:
#
#===============================================================================
