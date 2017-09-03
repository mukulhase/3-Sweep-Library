
#ifndef SCENEMODIFIER_H
#define SCENEMODIFIER_H

#include <QtCore/QObject>

#include <Qt3DCore/QEntity>
#include <Qt3DCore/QTransform>
#include <QtCore/QtMath>
#include <QtCore/QFileInfo>
#include <QtCore/QFile>

#include <Qt3DExtras/QTorusMesh>
#include <Qt3DExtras/QConeMesh>
#include <Qt3DExtras/QCylinderMesh>
#include <Qt3DExtras/QCuboidMesh>
#include <Qt3DExtras/QPlaneMesh>
#include <Qt3DExtras/QSphereMesh>
#include <Qt3DExtras/QPhongMaterial>
#include <Qt3DExtras/QPerVertexColorMaterial>
#include <Qt3DExtras/QForwardRenderer>
#include <Qt3DRender/QTextureImage>
#include <Qt3DExtras/QDiffuseMapMaterial>
#include <QNormalDiffuseSpecularMapMaterial>

#include <Qt3DInput/QKeyboardHandler>

#include <Qt3DRender/QMesh>
#include <Qt3DRender/QObjectPicker>
#include <Qt3DRender/QPickEvent>
#include <Qt3DRender/QGeometryRenderer>
#include <Qt3DRender/QGeometry>
#include <Qt3DRender/QBuffer>
#include <Qt3DRender/QAttribute>


#include <QDialogButtonBox>
#include <QFormLayout>
#include <QFileDialog>
#include <QInputDialog>
#include <QLabel>
#include <QPushButton>

#include "planeentity.h"

class SceneModifier : public QObject
{
    Q_OBJECT

public:
    explicit SceneModifier(Qt3DCore::QEntity *rootEntity, QWidget *parentWidget);
    ~SceneModifier();


    Qt3DRender::QObjectPicker *createObjectPickerForEntity(Qt3DCore::QEntity *entity);

public slots:
    void loadImage(const QString &fileName);
    void parsePLY(QTextStream &input);
    void mouseControls(Qt3DInput::QKeyEvent *event);
    void removeSceneElements();

protected:
    bool eventFilter(QObject *obj, QEvent *event);

private slots:
    void handlePickerPress(Qt3DRender::QPickEvent *event);
    void initData();
    void createTriangles(QVector3D v0, QVector3D color1, QVector3D v1, QVector3D color2, QVector3D v2, QVector3D color3);
    bool applyTranslations(const QVector3D trans);

private:
    bool handleMousePress(QMouseEvent *event);

    Qt3DCore::QEntity *m_rootEntity;

//    Qt3DCore::QEntity *m_customEntity;
    Qt3DCore::QEntity *m_objEntity;
    Qt3DCore::QTransform *objTransform;
    Qt3DExtras::QPhongMaterial *objMaterial;

    QWidget *m_parentWidget;

    PlaneEntity *planeEntity ;
    Qt3DExtras::QNormalDiffuseSpecularMapMaterial *normalDiffuseSpecularMapMaterial;
    Qt3DExtras::QNormalDiffuseSpecularMapMaterial *objectMaterial;

    Qt::MouseButton m_mouseButton;

    QList<QVector3D>* vertices;
    QList<QVector3D>* colors;

    QList<Qt3DCore::QEntity *> scene_entities;
    QList<Qt3DCore::QTransform *> scene_entities_trans;

};

#endif // SCENEMODIFIER_H
