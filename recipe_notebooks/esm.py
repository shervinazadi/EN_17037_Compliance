
# import topogenesis as tp
import numpy as np
from honeybee_plus.hbsurface import HBSurface
from honeybee_plus.radiance.recipe.solaraccess.gridbased import SolarAccessGridBased
from honeybee_plus.radiance.sky.certainIlluminance import CertainIlluminanceLevel
from honeybee_plus.radiance.recipe.pointintime.gridbased import GridBased
from honeybee_plus.radiance.analysisgrid import AnalysisGrid
from honeybee_plus.radiance.parameters.rtrace import LowQuality, RtraceParameters
import os
import ladybug as lb
import pandas as pd

material_glass = {'modifier': 'void',
                  'type': 'glass',
                  'name': 'generic_glass',
                  'r_transmittance': 0.6,
                  'g_transmittance': 0.6,
                  'b_transmittance': 0.6,
                  'refraction_index': 1.52
                  }
material_plastic = {'modifier': 'void',
                    'type': 'plastic',
                    'name': 'generic_plastic',
                    'r_reflectance': 0.2,
                    'g_reflectance': 0.2,
                    'b_reflectance': 0.2,
                    'specularity': 0.0,
                    'roughness': 0.0}


def pv_mesh_to_hbsurface(mesh, s_type, s_name, mat):
    hb_surfaces = []
    face_list = list(mesh.faces)
    e = 0
    while e < len(face_list):
        v_count = face_list[e]
        vertices = []
        for v in range(v_count):
            e += 1
            vertices.append(list(mesh.points[face_list[e]]))
        srf_dict = {
            "name": s_name,
            "vertices": vertices,  # [[(x, y, z), (x1, y1, z1), (x2, y2, z2)]],
            "surface_material": mat,
            "surface_type": s_type  # 0: wall, 5: window
            # TODO: look for the lables of ceiling and floor
            # TODO: check if radiance need unique names for surfaces!
        }
        srf_dict["surface_material"]["name"] = s_name
        hbsrf = HBSurface.from_json(srf_dict)
        hb_surfaces.append(hbsrf)
        e += 1
    return hb_surfaces


def mesh_to_hbsurface(faces, vertices, s_type, s_name, mat):
    hb_surfaces = []
    for face in faces:
        f_vertices = [tuple(vertices[v_id]) for v_id in face]
        srf_dict = {
            "name": s_name,
            # [[(x, y, z), (x1, y1, z1), (x2, y2, z2)]],
            "vertices": f_vertices,
            "surface_material": mat,
            "surface_type": s_type  # 0: wall, 5: window
            # TODO: look for the lables of ceiling and floor
            # TODO: check if radiance need unique names for surfaces!
        }
        srf_dict["surface_material"]["name"] = s_name
        hb_srf = HBSurface.from_json(srf_dict)
        hb_surfaces.append(hb_srf)

    return hb_surfaces
