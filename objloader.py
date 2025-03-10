import glm
import re

def loadOBJ(filename):
    """
    Loads an OBJ file and returns the vertex coordinates,
    texture coordinates (UV), and normal vectors.

    Args:
        filename (str): Path to the OBJ file.

    Returns:
        tuple: Three lists containing vertices (vec3), UVs (vec2), and normals (vec3).
    """
    
    vertices = []
    uvs = []
    normals = []
    
    # Lists for unique vertex data, UVs, and normal vectors
    uniq_vertices = [glm.vec3(0.0, 0.0, 0.0)]
    uniq_uvs = [glm.vec2(0.0, 0.0)]
    uniq_normals = [glm.vec3(0.0, 0.0, 0.0)]
    
    # Indices for each list
    indices_v = []
    indices_uv = []
    indices_vn = []
    
    print(f"Loading OBJ file '{filename}' ...")
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Recognizing data types from the line
                if line.startswith('v '):
                    # Vertex
                    parts = line.split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    uniq_vertices.append(glm.vec3(x, y, z))
                
                elif line.startswith('vt '):
                    # Texture UV
                    parts = line.split()
                    u, v = float(parts[1]), float(parts[2])
                    uniq_uvs.append(glm.vec2(u, v))
                
                elif line.startswith('vn '):
                    # Normal vector
                    parts = line.split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    uniq_normals.append(glm.vec3(x, y, z))
                
                elif line.startswith('f '):
                    # Creating a face (triangle)
                    parts = line.split()[1:]
                    face_vertices = []
                    face_uvs = []
                    face_normals = []

                    for part in parts:
                        # Splitting indices by "/"
                        vertex_indices = part.split('/')
                        v_idx = int(vertex_indices[0]) if vertex_indices[0] else 0
                        uv_idx = int(vertex_indices[1]) if len(vertex_indices) > 1 and vertex_indices[1] else 0
                        vn_idx = int(vertex_indices[2]) if len(vertex_indices) > 2 and vertex_indices[2] else 0

                        face_vertices.append(v_idx)
                        face_uvs.append(uv_idx)
                        face_normals.append(vn_idx)

                    # Adding indices for each triangle
                    indices_v.extend(face_vertices)
                    indices_uv.extend(face_uvs)
                    indices_vn.extend(face_normals)

    except IOError:
        print(f"Error: File '{filename}' could not be opened.")
        return None, None, None

    # Creating the final lists for vertices, UVs, and normals using the indices
    for i in range(len(indices_v)):
        vertices.append(uniq_vertices[indices_v[i]])
        uvs.append(uniq_uvs[indices_uv[i]])
        normals.append(uniq_normals[indices_vn[i]])

    print("Loading complete.")
    return vertices, uvs, normals
