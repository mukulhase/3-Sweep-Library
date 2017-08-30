
#include "scenemodifier.h"

#include <QtCore/QDebug>
#include <QMaterial>
#include <QNormalDiffuseSpecularMapMaterial>
#include "planeentity.h"

SceneModifier::SceneModifier(Qt3DCore::QEntity *rootEntity, QWidget *parentWidget)
    : m_rootEntity(rootEntity)
    , m_cylinderEntity(nullptr)
    , m_parentWidget(parentWidget)
{

    // Cuboid shape data
    Qt3DExtras::QCuboidMesh *cuboid = new Qt3DExtras::QCuboidMesh();
    cuboid->setXYMeshResolution(QSize(2, 2));
    cuboid->setYZMeshResolution(QSize(2, 2));
    cuboid->setXZMeshResolution(QSize(2, 2));
    // CuboidMesh Transform
    Qt3DCore::QTransform *cuboidTransform = new Qt3DCore::QTransform();
    cuboidTransform->setScale(1.0f);
    cuboidTransform->setTranslation(QVector3D(0.0f, 0.0f, 0.0f));

    caoMaterial = new Qt3DExtras::QPhongMaterial();
    caoMaterial->setDiffuse(QColor(QRgb(0xbeb32b)));

    //Cuboid
    m_cuboidEntity = new Qt3DCore::QEntity(m_rootEntity);
    m_cuboidEntity->addComponent(cuboid);
    m_cuboidEntity->addComponent(caoMaterial);
    m_cuboidEntity->addComponent(cuboidTransform);
    scene_entities.append(m_cuboidEntity);

    PlaneEntity *planeEntity = new PlaneEntity(m_rootEntity);
    planeEntity->mesh()->setHeight(20.0f);
    planeEntity->mesh()->setWidth(32.0f);
    planeEntity->mesh()->setMeshResolution(QSize(5, 5));

    Qt3DExtras::QNormalDiffuseSpecularMapMaterial *normalDiffuseSpecularMapMaterial = new Qt3DExtras::QNormalDiffuseSpecularMapMaterial();
    normalDiffuseSpecularMapMaterial->setTextureScale(1.0f);
    normalDiffuseSpecularMapMaterial->setShininess(80.0f);
    normalDiffuseSpecularMapMaterial->setAmbient(QColor::fromRgbF(1.0f, 1.0f, 1.0f, 1.0f));

    Qt3DRender::QTextureImage *diffuseImage = new Qt3DRender::QTextureImage();
    diffuseImage->setSource(QUrl(QStringLiteral("qrc:/assets/textures/pattern_09/diffuse.webp")));
    normalDiffuseSpecularMapMaterial->diffuse()->addTextureImage(diffuseImage);

    Qt3DRender::QTextureImage *specularImage = new Qt3DRender::QTextureImage();
    specularImage->setSource(QUrl(QStringLiteral("qrc:/assets/textures/pattern_09/specular.webp")));
    normalDiffuseSpecularMapMaterial->specular()->addTextureImage(specularImage);

//    Qt3DRender::QTextureImage *normalImage = new Qt3DRender::QTextureImage();
//    normalImage->setSource(QUrl((QStringLiteral("qrc:/assets/textures/pattern_09/normal.webp"))));
//    normalDiffuseSpecularMapMaterial->normal()->addTextureImage(normalImage);

    planeEntity->addComponent(normalDiffuseSpecularMapMaterial);
    this->initData();
}

SceneModifier::~SceneModifier()
{
}

void SceneModifier::initData()
{
    cylinder = new QList<QVector3D>();
}

void SceneModifier::createCylinder(const QVector3D &axis_1, const QVector3D &axis_2,
                                   const unsigned int index, const float radius, const QString &lod_param)
{
    QVector3D main_axis = axis_2 - axis_1;
    QVector3D mid_point = (axis_1 + axis_2) / 2;
    QVector3D main_axis_norm = main_axis.normalized();

    Qt3DExtras::QCylinderMesh *cylinder = new Qt3DExtras::QCylinderMesh();
    cylinder->setRadius(radius);
    cylinder->setLength(qSqrt(qPow(main_axis[0],2) + qPow(main_axis[1],2) + qPow(main_axis[2],2)));
    cylinder->setRings(100);
    cylinder->setSlices(20);

    // CylinderMesh Transform
    Qt3DCore::QTransform *cylinderTransform = new Qt3DCore::QTransform();
    QVector3D cylinderAxisRef(0, 1, 0);
    cylinderTransform->setRotation(QQuaternion::rotationTo(cylinderAxisRef, main_axis_norm));
    cylinderTransform->setTranslation(mid_point);

    m_cylinderEntity = new Qt3DCore::QEntity(m_rootEntity);
    m_cylinderEntity->addComponent(cylinder);
    m_cylinderEntity->addComponent(caoMaterial);
    m_cylinderEntity->addComponent(cylinderTransform);

    createObjectPickerForEntity(m_cylinderEntity);
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
