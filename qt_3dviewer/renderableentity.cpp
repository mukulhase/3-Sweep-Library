
#include "renderableentity.h"

RenderableEntity::RenderableEntity(Qt3DCore::QNode *parent)
    : Qt3DCore::QEntity(parent)
    , m_mesh(new Qt3DRender::QMesh())
    , m_transform(new Qt3DCore::QTransform())
{
    addComponent(m_mesh);
    addComponent(m_transform);
}

Qt3DRender::QMesh *RenderableEntity::mesh() const
{
    return m_mesh;
}

Qt3DCore::QTransform *RenderableEntity::transform() const
{
    return m_transform;
}
