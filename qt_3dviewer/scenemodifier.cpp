
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
    objTransform->setScale(0.02f);
    objTransform->setTranslation(QVector3D(0.0f, 5.0f, 0.0f));

    objMaterial = new Qt3DExtras::QPhongMaterial();
    objMaterial->setDiffuse(QColor(QRgb(0xbeb32b)));

    //Cuboid
    m_objEntity = new Qt3DCore::QEntity(m_rootEntity);
    m_objEntity->addComponent(cuboid);
    m_objEntity->addComponent(objMaterial);
    m_objEntity->addComponent(objTransform);
    scene_entities.append(m_objEntity);

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
}

SceneModifier::~SceneModifier()
{
}

void SceneModifier::initData()
{
    cylinder = new QList<QVector3D>();
}

void SceneModifier::loadImage(const QString &fileName)
{
//    if(m_objEntity->isEnabled())
//        m_objEntity->setEnabled(false);
    QStringList filepath = fileName.split('.');
    qInfo() << filepath[0];

    QFileInfo filmesh(filepath[0] + ".ply");
    Qt3DRender::QMesh *mesh = new Qt3DRender::QMesh();
//    mesh->setSource(QUrl::fromLocalFile("/home/vikas/Documents/WebGL/three.js/examples/models/ply/ascii/dolphins_colored.obj"));
    mesh->setSource(QUrl::fromLocalFile(filmesh.absoluteFilePath()));
    m_objEntity->addComponent(mesh);

    Qt3DRender::QTextureImage *Texture = new Qt3DRender::QTextureImage();
    Texture->setSource(QUrl::fromLocalFile("/home/vikas/Documents/3-Sweep-Library/output_color.png"));
    objectMaterial->diffuse()->addTextureImage(Texture);
    m_objEntity->addComponent(objectMaterial);

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


bool SceneModifier::eventFilter(QObject *obj, QEvent *event)
{
    Q_UNUSED(obj)
    switch (event->type())
    {
        case QEvent::KeyPress:
        {
            QKeyEvent *ke = static_cast<QKeyEvent *>(event);
            if (ke->key() == Qt::Key_Left)
            {
                objTransform->setTranslation(objTransform->translation() + QVector3D(0.5f, 0.0f, 0.0f));
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_Right)
            {
                objTransform->setTranslation(objTransform->translation() + QVector3D(-0.5f, 0.0f, 0.0f));
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_Up)
            {
                objTransform->setTranslation(objTransform->translation() + QVector3D(0.0f, 0.0f, 0.5f));
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_Down)
            {
                objTransform->setTranslation(objTransform->translation() + QVector3D(0.0f, 0.0f, -0.5f));
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_W)
            {
                objTransform->setRotationX(objTransform->rotationX()+0.5f);
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_S)
            {
                objTransform->setRotationX(objTransform->rotationX()-0.5f);
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_A)
            {
                objTransform->setRotationY(objTransform->rotationY()-0.5f);
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_D)
            {
                objTransform->setRotationY(objTransform->rotationY()+0.5f);
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_Z)
            {
                objTransform->setScale(objTransform->scale()+0.005f);
                m_objEntity->addComponent(objTransform);
                return true;
            }
            else if (ke->key() == Qt::Key_X)
            {
                objTransform->setScale(objTransform->scale()-0.005f);
                m_objEntity->addComponent(objTransform);
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
