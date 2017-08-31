#include "planeentity.h"

#include <Qt3DExtras/QPlaneMesh>
#include <Qt3DCore/QTransform>

PlaneEntity::PlaneEntity(Qt3DCore::QNode *parent)
    : Qt3DCore::QEntity(new Qt3DCore::QEntity(parent))
    , m_mesh(new Qt3DExtras::QPlaneMesh())
    , m_transform(new Qt3DCore::QTransform())
{
    addComponent(m_mesh);
    addComponent(m_transform);
}

PlaneEntity::~PlaneEntity()
{
}

Qt3DExtras::QPlaneMesh *PlaneEntity::mesh() const
{
    return m_mesh;
}

