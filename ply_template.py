TEMPLATE_PLY_FILE = u"""\
{
ply,
format ascii 1.0,
comment VCGLIB generated,
element vertex %(nPoints)d,
property float x,
property float y,
property float z,
property uchar red,
property uchar green,
property uchar blue,
property uchar alpha,
element face %(nFacepoints)d,
property list uchar int vertex_indices,
end_header,
[%(points)s],
[%(facepoints)s]
}
"""
TEMPLATE_VERTEX = "%f %f %f %d %d %d %d"
TEMPLATE_FACES = "%d %d %d %d"
