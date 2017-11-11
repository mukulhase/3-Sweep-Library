
#include "scenemodifier.h"

#include <QtGui/QGuiApplication>
#include <QtCore/QDebug>
#include <QMaterial>
#include "planeentity.h"

SceneModifier::SceneModifier(Qt3DCore::QEntity *rootEntity, QWidget *parentWidget)
    : m_rootEntity(rootEntity)
    , m_parentWidget(parentWidget)
{

    // Cuboid shape data
    Qt3DExtras::QCuboidMesh *cuboid = new Qt3DExtras::QCuboidMesh();
    cuboid->setXYMeshResolution(QSize(2, 2));
    cuboid->setYZMeshResolution(QSize(2, 2));
    cuboid->setXZMeshResolution(QSize(2, 2));
    // CuboidMesh Transform
    objTransform = new Qt3DCore::QTransform();
    objTransform->setScale(0.05f);
    objTransform->setTranslation(QVector3D(0.0f, 5.0f, 0.0f));

    objMaterial = new Qt3DExtras::QPhongMaterial();
    objMaterial->setDiffuse(QColor(QRgb(0xbeb32b)));

    //Cuboid
    m_objEntity = new Qt3DCore::QEntity(m_rootEntity);
    m_objEntity->addComponent(cuboid);
    m_objEntity->addComponent(objMaterial);
    m_objEntity->addComponent(objTransform);

    planeEntity = new PlaneEntity(m_rootEntity);
    planeEntity->mesh()->setHeight(20.0f);
    planeEntity->mesh()->setWidth(32.0f);
    planeEntity->mesh()->setMeshResolution(QSize(5, 5));

    normalDiffuseSpecularMapMaterial = new Qt3DExtras::QNormalDiffuseSpecularMapMaterial();
    normalDiffuseSpecularMapMaterial->setTextureScale(1.0f);
    normalDiffuseSpecularMapMaterial->setShininess(80.0f);
    normalDiffuseSpecularMapMaterial->setAmbient(QColor::fromRgbF(1.0f, 1.0f, 1.0f, 1.0f));

    objectMaterial = new Qt3DExtras::QNormalDiffuseSpecularMapMaterial();
    objectMaterial->setTextureScale(1.0f);
    objectMaterial->setShininess(80.0f);
    objectMaterial->setAmbient(QColor::fromRgbF(1.0f, 1.0f, 1.0f, 1.0f));

    this->initData();
    qGuiApp->installEventFilter(this);
    this->loadImage("/home/vikas/Documents/3-Sweep-Library/output/object0.png");
    QFile file("/home/vikas/Documents/3-Sweep-Library/output/object0.ply");
    if (!file.open(QFile::ReadOnly | QFile::Text)) {
        return;
    }

    QTextStream in(&file);
    this->parsePLY(in);

    file.close();
}

SceneModifier::~SceneModifier()
{
}

void SceneModifier::initData()
{
    vertices = new QList<QVector3D>();
    colors = new QList<QVector3D>();
}

void SceneModifier::loadImage(const QString &fileName)
{
//    if(m_objEntity->isEnabled())
//        m_objEntity->setEnabled(false);
    QStringList filepath = fileName.split('.');
    qInfo() << filepath[0];

//    QFileInfo filmesh(filepath[0] + ".ply");
//    Qt3DRender::QMesh *mesh = new Qt3DRender::QMesh();
//    mesh->setSource(QUrl::fromLocalFile("/home/vikas/Documents/WebGL/three.js/examples/models/ply/ascii/dolphins_colored.obj"));
//    mesh->setSource(QUrl::fromLocalFile(filmesh.absoluteFilePath()));
//    m_objEntity->addComponent(mesh);

//    Qt3DRender::QTextureImage *Texture = new Qt3DRender::QTextureImage();
//    Texture->setSource(QUrl::fromLocalFile("/home/vikas/Documents/3-Sweep-Library/output_color.png"));
//    objectMaterial->diffuse()->addTextureImage(Texture);
//    m_objEntity->addComponent(objectMaterial);

    QFileInfo fil(filepath[0] + ".png");
    QImage *background = new QImage(fil.absoluteFilePath());

    Qt3DRender::QTextureImage *diffuseImage = new Qt3DRender::QTextureImage();
    diffuseImage->setSource(QUrl::fromLocalFile(fil.absoluteFilePath()));
    normalDiffuseSpecularMapMaterial->diffuse()->addTextureImage(diffuseImage);

    Qt3DRender::QTextureImage *specularImage = new Qt3DRender::QTextureImage();
    specularImage->setSource(QUrl(QStringLiteral("qrc:/assets/textures/pattern_09/specular.webp")));
    normalDiffuseSpecularMapMaterial->specular()->addTextureImage(specularImage);

    planeEntity->mesh()->setHeight(20.0f);
    planeEntity->mesh()->setWidth(20.0f*background->width()/background->height());
    planeEntity->addComponent(normalDiffuseSpecularMapMaterial);
}

void SceneModifier::parsePLY(QTextStream &input)
{
    while(!input.atEnd())
    {
            QString line = input.readLine();
            QStringList data = line.split(" ");

            if(data[0].isEmpty())
                continue;
            unsigned int data_size = data.count();

            if (data_size == 7)
            {
                QVector3D v(data[0].toFloat(), data[1].toFloat(), data[2].toFloat());
                vertices->append(v);
                QVector3D c(data[3].toFloat()/255.0f, data[4].toFloat()/255.0f, data[5].toFloat()/255.0f);
                colors->append(c);
            }

            else if (data_size == 4)
                if (data[0].toInt() == 3)
                {
                    this->createTriangles(vertices->at(data[1].toInt()), colors->at(data[1].toInt())
                                         ,vertices->at(data[2].toInt()), colors->at(data[2].toInt())
                                         ,vertices->at(data[3].toInt()), colors->at(data[3].toInt()));
                }
    }
    qInfo() << "Done";
}

void SceneModifier::createTriangles(QVector3D v0, QVector3D color1,
                                    QVector3D v1, QVector3D color2,
                                    QVector3D v2, QVector3D color3)
{
    // Custom Mesh (TetraHedron)
    Qt3DRender::QGeometryRenderer *customMeshRenderer = new Qt3DRender::QGeometryRenderer;
    Qt3DRender::QGeometry *customGeometry = new Qt3DRender::QGeometry(customMeshRenderer);

    Qt3DRender::QBuffer *vertexDataBuffer = new Qt3DRender::QBuffer(Qt3DRender::QBuffer::VertexBuffer, customGeometry);
    Qt3DRender::QBuffer *indexDataBuffer = new Qt3DRender::QBuffer(Qt3DRender::QBuffer::IndexBuffer, customGeometry);

    // 4 distinct vertices
    QByteArray vertexBufferData;
    vertexBufferData.resize(4 * (3 + 3 + 3) * sizeof(float));

    QVector3D v3 = v2;

    // Faces Normals
    QVector3D n023 = QVector3D::normal(v0, v2, v3);
    QVector3D n012 = QVector3D::normal(v0, v1, v2);
    QVector3D n310 = QVector3D::normal(v3, v1, v0);
    QVector3D n132 = QVector3D::normal(v1, v3, v2);

    // Vector Normals
    QVector3D n0 = QVector3D(n023 + n012 + n310).normalized();
    QVector3D n1 = QVector3D(n132 + n012 + n310).normalized();
    QVector3D n2 = QVector3D(n132 + n012 + n023).normalized();
    QVector3D n3 = QVector3D(n132 + n310 + n023).normalized();


    QVector<QVector3D> vertices = QVector<QVector3D>()
            << v0 << n0 << color1
            << v1 << n1 << color2
            << v2 << n2 << color3
            << v3 << n3 << color3;

    float *rawVertexArray = reinterpret_cast<float *>(vertexBufferData.data());
    int idx = 0;

    Q_FOREACH (const QVector3D &v, vertices) {
        rawVertexArray[idx++] = v.x();
        rawVertexArray[idx++] = v.y();
        rawVertexArray[idx++] = v.z();
    }

    // Indices (12)
    QByteArray indexBufferData;
    indexBufferData.resize(4 * 3 * sizeof(ushort));
    ushort *rawIndexArray = reinterpret_cast<ushort *>(indexBufferData.data());

    // Front
    rawIndexArray[0] = 0;
    rawIndexArray[1] = 1;
    rawIndexArray[2] = 2;
    // Bottom
    rawIndexArray[3] = 3;
    rawIndexArray[4] = 1;
    rawIndexArray[5] = 0;
    // Left
    rawIndexArray[6] = 0;
    rawIndexArray[7] = 2;
    rawIndexArray[8] = 3;
    // Right
    rawIndexArray[9] = 1;
    rawIndexArray[10] = 3;
    rawIndexArray[11] = 2;

    vertexDataBuffer->setData(vertexBufferData);
    indexDataBuffer->setData(indexBufferData);

    // Attributes
    Qt3DRender::QAttribute *positionAttribute = new Qt3DRender::QAttribute();
    positionAttribute->setAttributeType(Qt3DRender::QAttribute::VertexAttribute);
    positionAttribute->setBuffer(vertexDataBuffer);
    positionAttribute->setDataType(Qt3DRender::QAttribute::Float);
    positionAttribute->setDataSize(3);
    positionAttribute->setByteOffset(0);
    positionAttribute->setByteStride(9 * sizeof(float));
    positionAttribute->setCount(4);
    positionAttribute->setName(Qt3DRender::QAttribute::defaultPositionAttributeName());

    Qt3DRender::QAttribute *normalAttribute = new Qt3DRender::QAttribute();
    normalAttribute->setAttributeType(Qt3DRender::QAttribute::VertexAttribute);
    normalAttribute->setBuffer(vertexDataBuffer);
    normalAttribute->setDataType(Qt3DRender::QAttribute::Float);
    normalAttribute->setDataSize(3);
    normalAttribute->setByteOffset(3 * sizeof(float));
    normalAttribute->setByteStride(9 * sizeof(float));
    normalAttribute->setCount(4);
    normalAttribute->setName(Qt3DRender::QAttribute::defaultNormalAttributeName());

    Qt3DRender::QAttribute *colorAttribute = new Qt3DRender::QAttribute();
    colorAttribute->setAttributeType(Qt3DRender::QAttribute::VertexAttribute);
    colorAttribute->setBuffer(vertexDataBuffer);
    colorAttribute->setDataType(Qt3DRender::QAttribute::Float);
    colorAttribute->setDataSize(3);
    colorAttribute->setByteOffset(6 * sizeof(float));
    colorAttribute->setByteStride(9 * sizeof(float));
    colorAttribute->setCount(4);
    colorAttribute->setName(Qt3DRender::QAttribute::defaultColorAttributeName());

    Qt3DRender::QAttribute *indexAttribute = new Qt3DRender::QAttribute();
    indexAttribute->setAttributeType(Qt3DRender::QAttribute::IndexAttribute);
    indexAttribute->setBuffer(indexDataBuffer);
    indexAttribute->setDataType(Qt3DRender::QAttribute::UnsignedShort);
    indexAttribute->setDataSize(1);
    indexAttribute->setByteOffset(0);
    indexAttribute->setByteStride(0);
    indexAttribute->setCount(12);

    customGeometry->addAttribute(positionAttribute);
    customGeometry->addAttribute(normalAttribute);
    customGeometry->addAttribute(colorAttribute);
    customGeometry->addAttribute(indexAttribute);

    customMeshRenderer->setInstanceCount(1);
    customMeshRenderer->setIndexOffset(0); //customMeshRenderer->setBaseVertex(0);
    customMeshRenderer->setFirstInstance(0); //customMeshRenderer->setBaseInstance(0);
    customMeshRenderer->setPrimitiveType(Qt3DRender::QGeometryRenderer::Triangles);
    customMeshRenderer->setGeometry(customGeometry);
    // 4 faces of 3 points
    customMeshRenderer->setVertexCount(12); //customMeshRenderer->setPrimitiveCount(12);

    // Material
    Qt3DRender::QMaterial *material = new Qt3DExtras::QPerVertexColorMaterial();

    // Transform
    Qt3DCore::QTransform *transform = new Qt3DCore::QTransform;
    transform->setScale(0.01f);
    transform->setTranslation(QVector3D(0.0f, 10.0f, 0.0f));

    // Custom mesh TetraHedron
    Qt3DCore::QEntity *m_customEntity = new Qt3DCore::QEntity(m_rootEntity);
    scene_entities.append(m_customEntity);
    scene_entities.last()->addComponent(customMeshRenderer);
    scene_entities.last()->addComponent(material);
    scene_entities.last()->addComponent(transform);

    scene_entities_trans.append(transform);
//    m_customEntity->addComponent(customMeshRenderer);
//    m_customEntity->addComponent(material);
//    m_customEntity->addComponent(transform);
}

Qt3DRender::QObjectPicker *SceneModifier::createObjectPickerForEntity(Qt3DCore::QEntity *entity)
{
    Qt3DRender::QObjectPicker *picker = new Qt3DRender::QObjectPicker(entity);
    picker->setHoverEnabled(false);
    entity->addComponent(picker);
    connect(picker, &Qt3DRender::QObjectPicker::pressed, this, &SceneModifier::handlePickerPress);
    scene_entities.append(entity);
    return picker;
}

void SceneModifier::removeSceneElements()
{
    Q_FOREACH (Qt3DCore::QEntity *entity, scene_entities)
    {
        entity->setEnabled(false);
    }
    scene_entities.clear();
    this->initData();
}

bool SceneModifier::applyTranslations(const QVector3D trans)
{
    for(int i=0;i< scene_entities.length();i++)
    {
        scene_entities_trans.at(i)->setTranslation(scene_entities_trans.at(i)->translation() + trans);
//        scene_entities.at(i)->addComponent(scene_entities_trans.at(i));
    }
    return true;
}

bool SceneModifier::eventFilter(QObject *obj, QEvent *event)
{
    Q_UNUSED(obj)
    switch (event->type())
    {
        case QEvent::KeyPress:
        {
            QKeyEvent *ke = static_cast<QKeyEvent *>(event);
            if (ke->key() == Qt::Key_Left)
                this->applyTranslations(QVector3D(0.5f, 0.0f, 0.0f));

            else if (ke->key() == Qt::Key_Right)
                this->applyTranslations(QVector3D(-0.5f, 0.0f, 0.0f));

            else if (ke->key() == Qt::Key_Up)
                this->applyTranslations(QVector3D(0.0f, 0.0f, 0.5f));

            else if (ke->key() == Qt::Key_Down)
                this->applyTranslations(QVector3D(0.0f, 0.0f, -0.5f));

            else if (ke->key() == Qt::Key_W)
            {
                for(int i=0;i< scene_entities.length();i++)
                    scene_entities_trans.at(i)->setRotationX(scene_entities_trans.at(i)->rotationX()+0.5f);
                return true;
            }
            else if (ke->key() == Qt::Key_S)
            {
                for(int i=0;i< scene_entities.length();i++)
                    scene_entities_trans.at(i)->setRotationX(scene_entities_trans.at(i)->rotationX()-0.5f);
                return true;
            }

            else if (ke->key() == Qt::Key_A)
            {
                for(int i=0;i< scene_entities.length();i++)
                    scene_entities_trans.at(i)->setRotationY(scene_entities_trans.at(i)->rotationY()-0.5f);
                return true;
            }
            else if (ke->key() == Qt::Key_D)
            {
                for(int i=0;i< scene_entities.length();i++)
                    scene_entities_trans.at(i)->setRotationY(scene_entities_trans.at(i)->rotationY()+0.5f);
                return true;
            }

            else if (ke->key() == Qt::Key_Z)
            {
                for(int i=0;i< scene_entities.length();i++)
                    scene_entities_trans.at(i)->setScale(scene_entities_trans.at(i)->scale()+0.005f);
                return true;
            }
            else if (ke->key() == Qt::Key_X)
            {
                for(int i=0;i< scene_entities.length();i++)
                    scene_entities_trans.at(i)->setScale(scene_entities_trans.at(i)->scale()-0.005f);
                return true;
            }
            break;
        }
//    case QEvent::MouseButtonPress:
//        break;

        default:
            break;
    }

    return false;
}


bool SceneModifier::handleMousePress(QMouseEvent *event)
{
    m_mouseButton = event->button();
    return false;
}

void SceneModifier::handlePickerPress(Qt3DRender::QPickEvent *event)
{
    if (event->button() == Qt3DRender::QPickEvent::RightButton)
    {
        Qt3DCore::QEntity *pressedEntity = qobject_cast<Qt3DCore::QEntity *>(sender()->parent());
        if (pressedEntity && pressedEntity->isEnabled())
        {

        }
    }
}

void SceneModifier::mouseControls(Qt3DInput::QKeyEvent *event)
{
    qInfo() << event->key();
}
