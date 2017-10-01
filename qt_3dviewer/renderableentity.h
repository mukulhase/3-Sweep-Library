#ifndef RENDERABLEENTITY_H
#define RENDERABLEENTITY_H

#include <Qt3DCore/QEntity>
#include <Qt3DCore/QTransform>
#include <Qt3DRender/QMesh>

class RenderableEntity : public Qt3DCore::QEntity
{
public:
    RenderableEntity(Qt3DCore::QNode *parent = 0);

    Qt3DRender::QMesh *mesh() const;
    Qt3DCore::QTransform *transform() const;

private:
    Qt3DRender::QMesh *m_mesh;
    Qt3DCore::QTransform *m_transform;
};

#endif // RENDERABLEENTITY_H
