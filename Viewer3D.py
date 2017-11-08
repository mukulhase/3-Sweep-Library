import sys

from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import (Qt3DWindow, QFirstPersonCameraController, QNormalDiffuseMapMaterial,
                              QNormalDiffuseSpecularMapMaterial,
                              QPlaneMesh)
from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DRender import QMesh, QTextureImage, QPointLight, QObjectPicker
from PyQt5.QtCore import pyqtSlot, QObject, QSize, Qt, QUrl
from PyQt5.QtGui import QColor, QVector3D, QImage
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QWidget, QPushButton)

OUTPUT_DIR = 'output/'

class PlaneEntity(QEntity):

    def __init__(self, parent=None):
        super(PlaneEntity, self).__init__(parent)

        self.m_mesh = QPlaneMesh()
        self.m_transform = QTransform()

        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def mesh(self):
        return self.m_mesh


class RenderableEntity(QEntity):

    def __init__(self, parent=None):
        super(RenderableEntity, self).__init__(parent)

        self.m_mesh = QMesh()
        self.m_transform = QTransform()

        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def mesh(self):
        return self.m_mesh

    def transform(self):
        return self.m_transform

class MainObject(QEntity):

    def __init__(self, parent=None):
        super(MainObject, self).__init__(parent)

        self.m_object = RenderableEntity(self)

        self.m_objectMaterial = QNormalDiffuseMapMaterial()

        self.m_objectImage = QTextureImage()
        self.m_objectNormalImage = QTextureImage()

        self.m_object.addComponent(self.m_objectMaterial)

        self.m_object.mesh().setSource(QUrl.fromLocalFile(OUTPUT_DIR + 'object0.obj'))

        self.m_objectMaterial.diffuse().addTextureImage(self.m_objectImage)
        self.m_objectMaterial.normal().addTextureImage(self.m_objectNormalImage)

        self.m_objectImage.setSource( QUrl.fromLocalFile(OUTPUT_DIR + 'object0.png') )
        self.m_objectNormalImage.setSource( QUrl.fromLocalFile('qt_3dviewer/exampleresources/normal.png') )
    
        self.m_objectMaterial.setShininess(80.0)
        self.m_objectMaterial.setSpecular(QColor.fromRgbF(1.0, 1.0, 1.75, 1.0))

    def setPosition(self, pos):
        self.m_object.transform().setTranslation(pos)

    def position(self):
        return self.m_object.transform().translation()

    def setScale(self, scale):
        self.m_object.transform().setScale(scale)

    def scale(self):
        return self.m_object.transform().scale()


class SceneModifier(QObject):

    def __init__(self, rootEntity):
        super(SceneModifier, self).__init__()

        self.m_rootEntity = rootEntity

        self.normalDiffuseSpecularMapMaterial = QNormalDiffuseSpecularMapMaterial()
        self.normalDiffuseSpecularMapMaterial.setTextureScale(1.0)
        self.normalDiffuseSpecularMapMaterial.setShininess(80.0)
        self.normalDiffuseSpecularMapMaterial.setAmbient(QColor.fromRgbF(1.0, 1.0, 1.0, 1.0))

        diffuseImage = QTextureImage()
        diffuseImage.setSource( QUrl.fromLocalFile('loading.png') )
        self.normalDiffuseSpecularMapMaterial.diffuse().addTextureImage(diffuseImage)
        background = QImage()
        background.load('loading.png')

        self.planeEntity = PlaneEntity(self.m_rootEntity)
        self.planeEntity.mesh().setHeight(20.0)
        self.planeEntity.mesh().setWidth(20.0 * background.width() / background.height())
        self.planeEntity.mesh().setMeshResolution(QSize(5, 5))
        self.planeEntity.addComponent(self.normalDiffuseSpecularMapMaterial)

    @pyqtSlot()
    def loadscene(self):
        diffuseImage = QTextureImage()
        diffuseImage.setSource( QUrl.fromLocalFile(OUTPUT_DIR + 'output.png') )
        self.normalDiffuseSpecularMapMaterial.diffuse().addTextureImage(diffuseImage)
        background = QImage()
        background.load(OUTPUT_DIR + 'output.png')

        # Background Plane
        self.planeEntity.mesh().setWidth(20.0 * background.width() / background.height())
        self.planeEntity.addComponent(self.normalDiffuseSpecularMapMaterial)

        self.obj = MainObject(self.m_rootEntity)
        self.obj.setPosition(QVector3D( - (self.planeEntity.mesh().width() / 2) * 0.0, 0.0, - (self.planeEntity.mesh().height() / 2) * 0.0))
        self.obj.setScale(0.05)
        # picker = QObjectPicker(self.m_rootEntity)
        # picker.setHoverEnabled(True)
        # self.obj.addComponent(picker)
        # picker.pressed.connect(self.handlePickerPress)

    @pyqtSlot()
    def handlePickerPress(self):
        print("selected obj")

    @pyqtSlot()
    def transformLeft(self):
        self.obj.setPosition(self.obj.position() + QVector3D(0.5, 0.0, 0.0))

    @pyqtSlot()
    def transformRight(self):
        self.obj.setPosition(self.obj.position() - QVector3D(0.5, 0.0, 0.0))

    @pyqtSlot()
    def transformUp(self):
        self.obj.setPosition(self.obj.position() + QVector3D(0.0, 0.0, 0.5))

    @pyqtSlot()
    def transformDown(self):
        self.obj.setPosition(self.obj.position() - QVector3D(0.0, 0.0, 0.5))
    
    @pyqtSlot()
    def scaleUp(self):
        self.obj.setScale(self.obj.scale() + 0.005)

    @pyqtSlot()
    def scaleDown(self):
        self.obj.setScale(self.obj.scale() - 0.005)

class Viewer3D():
    def __init__(self, app):
        view = Qt3DWindow()
        # view.defaultFramegraph().setClearColor(QColor(0x4d4d4f))
        container = QWidget.createWindowContainer(view)
        screenSize = view.screen().size()
        container.setMinimumSize(QSize(200, 100))
        container.setMaximumSize(screenSize)

        widget = QWidget()
        self.hLayout = QHBoxLayout(widget)
        self.vLayout = QVBoxLayout()
        self.vLayout.setAlignment(Qt.AlignTop)
        self.hLayout.addWidget(container, 1)
        self.hLayout.addLayout(self.vLayout)

        widget.setWindowTitle("3D Viewer")

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
        # camController = QFirstPersonCameraController(self.rootEntity)
        # camController.setCamera(cameraEntity)

        # Set root object of the scene.
        view.setRootEntity(self.rootEntity)

        modifier = SceneModifier(self.rootEntity)

        moveLeft = QPushButton(text="Left")
        moveLeft.clicked.connect(modifier.transformLeft)
        moveLeft.setAutoRepeat(True)

        moveRight = QPushButton(text="Right")
        moveRight.clicked.connect(modifier.transformRight)
        moveRight.setAutoRepeat(True)

        moveUp = QPushButton(text="Up")
        moveUp.clicked.connect(modifier.transformUp)
        moveUp.setAutoRepeat(True)

        moveDown = QPushButton(text="Down")
        moveDown.clicked.connect(modifier.transformDown)
        moveDown.setAutoRepeat(True)

        scaleDown = QPushButton(text="Scale Down")
        scaleDown.clicked.connect(modifier.scaleDown)
        scaleDown.setAutoRepeat(True)

        scaleUp = QPushButton(text="Scale Up")
        scaleUp.clicked.connect(modifier.scaleUp)
        scaleUp.setAutoRepeat(True)

        loadModel = QPushButton(text="Load Model")
        loadModel.clicked.connect(modifier.loadscene)

        self.vLayout.addWidget(moveLeft)
        self.vLayout.addWidget(moveRight)
        self.vLayout.addWidget(moveUp)
        self.vLayout.addWidget(moveDown)
        self.vLayout.addWidget(scaleUp)
        self.vLayout.addWidget(scaleDown)
        self.vLayout.addWidget(loadModel)

        # Show the window.
        widget.show()
        widget.resize(1200, 800)
        sys.exit(app.exec_())


    # def createTriangles(self, v0, v1, v2, c0, c1, c2):
    #     customMeshRenderer = QGeometryRenderer()
    #     customGeometry = QGeometry(customMeshRenderer)
    #
    #     vertexDataBuffer = QBuffer('VertexBuffer', customGeometry)
    #     indexDataBuffer = QBuffer('IndexBuffer', customGeometry)
    #     v3 = v2
    #     ## Faces Normals
    #     n023 = QVector3D.normal(v0, v2, v3)
    #     n012 = QVector3D.normal(v0, v1, v2)
    #     n310 = QVector3D.normal(v3, v1, v0)
    #     n132 = QVector3D.normal(v1, v3, v2)
    #
    #     ## Vector Normals
    #     n0 = QVector3D(n023 + n012 + n310).normalized()
    #     n1 = QVector3D(n132 + n012 + n310).normalized()
    #     n2 = QVector3D(n132 + n012 + n023).normalized()
    #     n3 = QVector3D(n132 + n310 + n023).normalized()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)

    viewer = Viewer3D(app)
