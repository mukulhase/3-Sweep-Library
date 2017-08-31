
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

//    void keyPressEvent(QKeyEvent *event);

    QList<QVector3D>* cylinder;

    QList<Qt3DCore::QEntity *> scene_entities;
    Qt3DRender::QObjectPicker *createObjectPickerForEntity(Qt3DCore::QEntity *entity);

public slots:
    void loadImage(const QString &fileName);
    void mouseControls(Qt3DInput::QKeyEvent *event);
    void removeSceneElements();

protected:
    bool eventFilter(QObject *obj, QEvent *event);

private slots:
    void handlePickerPress(Qt3DRender::QPickEvent *event);
    void initData();

private:
    bool handleMousePress(QMouseEvent *event);

    Qt3DCore::QEntity *m_rootEntity;

    Qt3DCore::QEntity *m_objEntity;
    Qt3DCore::QTransform *objTransform;

    Qt3DExtras::QPhongMaterial *objMaterial;
    QWidget *m_parentWidget;

    PlaneEntity *planeEntity ;
    Qt3DExtras::QNormalDiffuseSpecularMapMaterial *normalDiffuseSpecularMapMaterial;

    Qt::MouseButton m_mouseButton;


};

#endif // SCENEMODIFIER_H
