# import honeybee as hb
# import honeybee_radiance as hbr
# print(dir(hb))
# print(hb.__doc__)
# print(hb.__name__)
# print(hb.__package__)
# print(hb.room)
# print(hbr)

# from honeybee.room import Room
# from honeybee.radiance.material.glass import Glass
# from honeybee_radiance.sky.certainIlluminance import CertainIlluminanceLevel
# from honeybee_radiance.recipe.pointintime.gridbased import GridBased
import subprocess as sp

from ladybug.wea import Wea
from honeybee_plus.room import Room
from honeybee_plus.radiance.material.glass import Glass
from honeybee_plus.radiance.sky.certainIlluminance import CertainIlluminanceLevel
from honeybee_plus.radiance.recipe.pointintime.gridbased import GridBased

sp.run(['ls'])
# create a test room
room = Room(origin=(0, 0, 3.2), width=4.2, depth=6, height=3.2,
            rotation_angle=45)

# add another window with custom material. This time to the right wall
glass_60 = Glass.by_single_trans_value('tvis_0.6', 0.6)
room.add_fenestration_surface('right', 4, 1.5, 1.2, radiance_material=glass_60)

# run a grid-based analysis for this room
# generate the sky
sky = CertainIlluminanceLevel(illuminance_value=2000)

# generate grid of test points
analysis_grid = room.generate_test_points(grid_size=0.5, height=0.75)

# put the recipe together
rp = GridBased(sky=sky, analysis_grids=(analysis_grid,), simulation_type=0,
               hb_objects=(room,))

# write simulation to folder
batch_file = rp.write(target_folder='.', project_name='room')

# run the simulation
rp.run(batch_file, debug=False)

# results - in this case it will be an analysis grid
result = rp.results()[0]

print(result)
print(type(result))
