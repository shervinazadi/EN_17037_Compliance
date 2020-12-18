
# import topogenesis as tp
from honeybee_plus.radiance.recipe._gridbasedbase import GenericGridBased
from honeybee_plus.radiance.recipe.recipeutil import write_rad_files, write_extra_files

from honeybee_plus.radiance.command.oconv import Oconv
from honeybee_plus.radiance.command.rtrace import Rtrace
from honeybee_plus.radiance.command.rcalc import Rcalc
from honeybee_plus.radiance.command.rpict import Rpict
from honeybee_plus.radiance.command.vwrays import Vwrays

from honeybee_plus.futil import write_to_file

import numpy as np
from honeybee_plus.hbsurface import HBSurface
from honeybee_plus.radiance.recipe.solaraccess.gridbased import SolarAccessGridBased
from honeybee_plus.radiance.sky.certainIlluminance import CertainIlluminanceLevel
from honeybee_plus.radiance.recipe.pointintime.gridbased import GridBased
from honeybee_plus.radiance.analysisgrid import AnalysisGrid
from honeybee_plus.radiance.parameters.rtrace import LowQuality, RtraceParameters
import os
import honeybee_plus
# import ladybug as lb
import pandas as pd
import trimesh as tm


class ContextViewGridBased(GenericGridBased):
    def __init__(self, analysis_grids, rad_parameters=None,
                 hb_objects=None, sub_folder="gridbased"):
        """Create grid-based recipe."""
        GenericGridBased.__init__(
            self, analysis_grids, hb_objects, sub_folder)

        # self.sky = sky
        # """A honeybee sky for the analysis."""

        self.radiance_parameters = rad_parameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)"""

        # self.simulation_type = simulation_type
        # """Simulation type: 0: Illuminance(lux), 1: Radiation (wh),
        #    2: Luminance (Candela) (Default: 0)
        # """

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Files for a grid based analysis are:
            test points <project_name.pts>: List of analysis points.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if hb_objects
                is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if hb_objects
                is None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <project_name.mat> <project_name.rad>
                <additional rad_files> > <project_name.oct>
                rtrace <radiance_parameters> <project_name.oct> > <project_name.res>
            results file <*.res>: Results file once the analysis is over.

        Args:
            target_folder: Path to parent folder. Files will be created under
                target_folder/gridbased. use self.sub_folder to change subfolder name.
            project_name: Name of this project as a string.

        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        self._commands = []

        # create main folder target_folder/project_name
        project_folder = \
            super(GenericGridBased, self).write_content(
                target_folder, project_name)

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_files(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )
        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene')

        # 1.write points
        points_file = self.write_analysis_grids(project_folder, project_name)

        # 2. save rays
        icosphere = tm.creation.icosphere(subdivisions=3, radius=1.0)
        v = icosphere.vertices
        rays = np.c_[np.full(v.shape, 1), v]

        view_rays_fname = "view_rays.txt"
        view_rays_path = os.path.join(project_folder, view_rays_fname)
        np.savetxt(view_rays_path, rays)

        # 3.write batch file
        if header:
            self.commands.append(self.header(project_folder))

        # 4.1.prepare oconv
        octf_name = project_name + '.oct'
        octf = os.path.join(project_folder, self.sub_folder, octf_name)

        oct_scene_files = \
            opqfiles + glzfiles + wgsfiles + extrafiles.fp

        oct_scene_files_items = []
        for f in oct_scene_files:
            if isinstance(f, (list, tuple)):
                print('Point-in-time recipes cannot currently handle dynamic window'
                      ' groups. The first state will be used for simulation.')
                oct_scene_files_items.append(f[0])
            else:
                oct_scene_files_items.append(f)

        oc = Oconv(project_name)
        oc.scene_files = tuple(self.relpath(f, project_folder)
                               for f in oct_scene_files_items)

        # 4.2.prepare rtrace
        rp_rtrace = honeybee_plus.radiance.parameters.rtrace.LowQuality()

        rp_rtrace.remove_parameters()
        rp_rtrace.add_radiance_number('ab')
        rp_rtrace.ab = 0
        rp_rtrace.add_radiance_value('o', is_joined=True)
        rp_rtrace.o = 'vmlL'
        rp_rtrace.add_radiance_bool_flag('w')
        rp_rtrace.w = True

        rc_rtrace = Rtrace(output_name=project_name,
                           octree_file=octf,
                           simulation_type=2)

        rtrace_cmd = '%s %s %s < %s > rtrace_res.txt' % (
            rc_rtrace.normspace(os.path.join(rc_rtrace.radbin_path, "rtrace")),
            rp_rtrace,
            octf_name,
            view_rays_fname)

        # 3.3 write batch file
        self._commands.append(oc.to_rad_string())
        self._commands.append(rtrace_cmd)

        batch_file = os.path.join(project_folder, "commands.bat")

        write_to_file(batch_file, "\n".join(self.commands))

        self._result_files = os.path.join(project_folder, 'rtrace_res.txt')

        return batch_file


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


def parse_results(rp, aggregate=False):

    df = pd.read_csv(rp._result_files, skiprows=13, sep='\t', header=None)

    if not aggregate:
        return df
    else:
        return df.sum(axis=1) / df.shape[0]
