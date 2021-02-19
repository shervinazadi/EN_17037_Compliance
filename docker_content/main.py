import numpy as np
import pandas as pd
import json
import copy
import random
import itertools
import pyrebase
# import topogenesis as tg
# import honeybee_plus as hb

# with open("fb_auth.json") as json_file:
#     config = json.load(json_file)

# # create firebase app
# firebase = pyrebase.initialize_app(config)

# # access the database
# fb_db = firebase.database()


def gate(request):
    # For more information about CORS and CORS preflight requests, see
    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request
    # for more information.
    # this solution was not working, check this: https://bit.ly/3f8WhL2

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    # retrieve the parameters
    req_dict = dict(request.args)

    funcNames = json.loads(req_dict['function'])['funcNames']

    # iterate over the functions and run them one by one
    for funcNameItem in funcNames:
        # retrieve the requested function
        func = globals()[funcNameItem]

        # run the requested function and updating the funcdata
        funcData = func()

    d = {
        'result': "Done"
    }
    return (d, 200, headers)


def TestFunction():
    # retrive all the cell data
    db_cells = fb_db.child("cells").get()

    # retrieve the data as dictionary
    db_cells_data = db_cells.val()

    # # add a new cell
    # db_cells_data[fb_db.generate_key()] = {"position": [10, 0, 10], "state": 1}

    # add the new cells
    new_cell_data = {}

    # iterating over all the cells
    for k, v in db_cells_data.items():
        # changing the state to 1
        v["state"] = 1
        # convert the dictionary keys to include the path in database
        new_cell_data["cells/" + k] = v

    # update the database
    fb_db.update(new_cell_data)

    return True


def Segregation():
    threshold = 0.75
    # retrive all the cell data
    db_cells = fb_db.child("cells").get()
    db_agents = fb_db.child("agents").get()

    # retrieve the data as dictionary
    db_cells_data = db_cells.val()
    db_agents_data = db_agents.val()
    cells_df = pd.DataFrame.from_dict(db_cells_data, orient='index')
    agents_df = pd.DataFrame.from_dict(db_agents_data, orient='index')

    cell_pos = np.stack(cells_df["position"].to_numpy(), axis=0)
    cell_state = cells_df["state"].to_numpy()
    agent_pos = np.stack(agents_df["position"].to_numpy(), axis=0)
    agent_class = agents_df["class"].to_numpy()

    # check compatibility
    ######################
    grid_shape = cell_pos.max(axis=0) + 1
    grid = cell_state.reshape(tuple(grid_shape))

    # check if the cells have the agent information
    if grid.sum() == 0:
        agent_indices = tuple(agent_pos.T)
        grid[agent_indices] = agent_class

    # randomly relocate the incompatible agents
    neighborhood = np.array(list(itertools.product(
        [0, 1, -1], [0], [0, 1, -1], repeat=1))[1:])

    grid_padded = np.pad(grid, ((1, 1), (0, 0), (1, 1)),
                         'constant', constant_values=0)

    available_pos = np.argwhere(grid == 0)

    uncomp = []
    for a_pos in agent_pos:
        a_padded_pos = a_pos + [1, 0, 1]
        neighs_padded_pos = a_pos + neighborhood + [1, 0, 1]
        a_val = grid_padded[tuple(a_padded_pos)]
        neigh_vals = grid_padded[tuple(neighs_padded_pos.T)]
        unq_vals, unq_counts = np.unique(neigh_vals, return_counts=True)
        neigh_class_percentage = unq_counts / unq_counts.sum()
        a_ind = np.argwhere(unq_vals == a_val)
        # print(a_ind, unq_vals, a_val)
        if neigh_class_percentage[a_ind] > threshold:
            uncomp.append(0)

        elif sum(uncomp) < len(available_pos):
            # change position
            uncomp.append(1)

        else:
            uncomp.append(0)

    selected_pos = np.random.choice(
        np.arange(len(available_pos)), size=sum(uncomp), replace=False)

    uncomp_mask = np.array(uncomp) == 1

    # update agent positions
    agent_pos[uncomp_mask] = available_pos[selected_pos]

    grid *= 0
    agent_indices = tuple(agent_pos.T)
    grid[agent_indices] = agent_class
    # update the cell and agent dictionaries

    agents_df["position"] = agent_pos.tolist()
    agents_df["new_key"] = "agents/" + agents_df.index.values
    agents_df = agents_df.set_index("new_key")

    cell_state = grid.flatten()
    cells_df["state"] = cell_state
    cells_df["new_key"] = "cells/" + cells_df.index.values
    cells_df = cells_df.set_index("new_key")

    # update the database
    fb_db.update(cells_df.T.to_dict())
    fb_db.update(agents_df.T.to_dict())

    return True


def stepD(data):

    # DEPRECATED
    ############

    # convert string to json
    if isinstance(data, str):
        data = json.loads(data)

    # retrieve the position list
    voxel_positions = data['voxel_positions']
    # find the new point position
    newposS = copy.deepcopy(voxel_positions[0])
    newposS[random.randrange(3)] -= 1
    newposE = copy.deepcopy(voxel_positions[-1])
    newposE[random.randrange(3)] += 1
    # append
    new_voxel_positions = []
    new_voxel_positions.append(newposS)
    new_voxel_positions.extend(voxel_positions)
    new_voxel_positions.append(newposE)

    # package the results
    result = {
        'voxel_positions': new_voxel_positions,
        'to_update': data['to_update'] + ['voxels'] if 'to_update' in data else ['voxels'],
    }

    return result


def CellularAutomata():

    # retrieve cell data and voxel position
    db_cells = fb_db.child("cells").get()

    # all_users = db.child("users").get()
    # for user in all_users.each():
    #     print(user.key()) # Morty
    #     print(user.val()) # {name": "Mortimer 'Morty' Smith"}
    db_cell_data = []
    for cell in db_cells.each():
        db_cell_data.append(cell.position)

    # db_cell_data = db_cells.val()

    # voxel_positions = np.array(list(db_cell_data.values())).astype(int)
    voxel_positions = np.array(db_cell_data).astype(int)

    # construct the volume
    minbound = voxel_positions.min(axis=0)
    maxbound = voxel_positions.max(axis=0)
    volume = np.zeros(maxbound-minbound + 1).astype(int)

    # fill in the volume
    mapped_ind = voxel_positions - minbound
    volume[mapped_ind[:, 0], mapped_ind[:, 1], mapped_ind[:, 2]] = 1

    # pad the volume with zero in every direction
    volume = np.pad(volume, (1, 1), mode='constant', constant_values=(0, 0))

    # limit to 2D
    volume = volume[:, 1, :]
    volume = volume[:, np.newaxis]

    # the id of voxels (0,1,2, ... n)
    volume_inds = np.arange(volume.size).reshape(volume.shape)

    # calculating all the possible shifts to apply to the array
    # repeat set to 2, to limit to 2D
    shifts = np.array(list(itertools.product([0, -1, 1], repeat=2)))
    shifts = np.vstack((shifts[:, 0], np.zeros(9).astype(int), shifts[:, 1])).T

    # gathering all the replacements in the columns
    replaced_columns = [
        np.roll(volume_inds, shift, np.arange(3)).ravel() for shift in shifts]

    # stacking the columns
    cell_neighbors = np.stack(replaced_columns, axis=-1)

    # replace neighbours by their value in volume
    volume_flat = volume.ravel()
    neighbour_values = volume_flat[cell_neighbors]

    # sum the neighbour values
    neighbour_sum = neighbour_values.sum(axis=1)

    # turn off if less than 2 neighbours on
    volume_flat *= (neighbour_sum >= 2)

    # turn off if more than 6 neighbours on
    volume_flat *= (neighbour_sum <= 6)

    # turn on if 3 neighbours are on
    volume_flat[(neighbour_sum >= 3) * (neighbour_sum <= 4)] = 1

    # on-cells 1D-index
    oncells_1d_ind = np.argwhere(volume_flat == 1).ravel()

    # unravel the indices to 3D-index
    oncells_3d_ind = np.stack(np.unravel_index(
        oncells_1d_ind, volume.shape), axis=-1)

    # map back the indices (add initial minimum and subtract 1 for the padded layer)
    # 3D version: new_voxel_positions = oncells_3d_ind + minbound - 1
    new_voxel_positions = oncells_3d_ind + minbound - 1 + np.array([0, 1, 0])

    # remove previous cells
    fb_db.child("cells").remove()

    # add the new cells
    cell_data = {}
    for pos in new_voxel_positions.tolist():
        cell_data["cells/" + fb_db.generate_key()] = pos

    # update the database
    fb_db.update(cell_data)

    return True


def RandomWalkingAgents():

    # retrieve cell data and voxel position
    db_cells = fb_db.child("cells").get()
    db_cell_data = db_cells.val()
    voxel_positions = np.array(list(db_cell_data.values())).astype(int)

    # construct the volume
    minbound = voxel_positions.min(axis=0)
    maxbound = voxel_positions.max(axis=0)
    volume = np.zeros(maxbound-minbound + 1).astype(int)

    # fill in the volume
    mapped_ind = voxel_positions - minbound
    volume[mapped_ind[:, 0], mapped_ind[:, 1], mapped_ind[:, 2]] = 1

    # pad the volume with zero in every direction
    volume = np.pad(volume, (1, 1), mode='constant', constant_values=(0, 0))

    # limit to 2D
    volume = volume[:, 1, :]
    volume = volume[:, np.newaxis]

    # the id of voxels (0,1,2, ... n)
    volume_inds = np.arange(volume.size).reshape(volume.shape)

    # shifts to check: self + 6 neighbours of each voxel
    shifts = np.array([
        [0, 0, 0],  # self
        [1, 0, 0],  # left
        [-1, 0, 0],  # right
        # limit to 2D
        # [0, 1, 0],  # up
        # [0, -1, 0],  # down
        [0, 0, 1],  # back
        [0, 0, -1],  # front
    ])

    # gattering all the replacements in the collumns
    replaced_columns = [
        np.roll(volume_inds, shift, np.arange(3)).ravel() for shift in shifts]

    # stacking the columns
    cell_neighbors = np.stack(replaced_columns, axis=-1)

    # replace neighbours by their value in volume and flip it: 0:occupied, 1:empty
    volume_flat = volume.ravel()
    neighbor_values_flipped = 1-volume_flat[cell_neighbors]

    # multiply the cell neighbours by their flipped values to remove all occupied neighbours. +1 and -1 is to prevent mixing the empty cells and the cell id 0, so we mark the empty cells -1 instead of 0
    empty_neighbours = neighbor_values_flipped * (cell_neighbors + 1) - 1

    # extracting the id and flipped value of neighbours of the filled voxels: current position of agents
    agent_neighbour_values_flipped = neighbor_values_flipped[np.where(
        volume_flat)]
    agent_neighbour_id = cell_neighbors[np.where(volume_flat)]

    # assigning random value to each neighbour (this can later be specified by a field instead of randomvalues)
    rand_shape = agent_neighbour_values_flipped.shape
    agn_neigh_prority = agent_neighbour_values_flipped * \
        np.random.rand(rand_shape[0], rand_shape[1])

    # getting the argmax to find the selected neighbours
    neigh_selection = agn_neigh_prority.argmax(axis=1)

    # extracting the voxel id of the current position and the next selected position of all agents
    cur_pos_id = agent_neighbour_id[:, 0]
    sel_pos_id = agent_neighbour_id[np.arange(
        neigh_selection.size), neigh_selection]

    # checking for unique idsin the new_position_id: to prevent two agents merging together by moving into one voxel
    __, unq_indices = np.unique(sel_pos_id, return_index=True)

    # setting the uniqe voxels in the selected position to current position: updating the cur_pos_id. (this is computationally cheaper than setting it in a new array)
    cur_pos_id[unq_indices] = sel_pos_id[unq_indices]

    # emptying the volume and filling the selected neighbours
    volume_flat *= 0
    volume_flat[cur_pos_id] = 1

    # on-cells 1D-index
    oncells_1d_ind = np.argwhere(volume_flat == 1).ravel()

    # unravel the indices to 3D-index
    oncells_3d_ind = np.stack(np.unravel_index(
        oncells_1d_ind, volume.shape), axis=-1)

    # map back the indicies (add initial minimum and subtract 1 for the padded layer)
    # 3D version: new_voxel_positions = oncells_3d_ind + minbound - 1
    new_voxel_positions = oncells_3d_ind + minbound - 1 + np.array([0, 1, 0])

    ###########################################################################
    # ATTENTION:
    # Agents are not able to merge anymore. if two agent has chose one single
    # voxel as the next position. one of would randomly be selected to move to
    # the next position and the other one will remain in his old position
    ###########################################################################

    # remove previous cells
    fb_db.child("cells").remove()

    # add the new cells
    cell_data = {}
    for pos in new_voxel_positions.tolist():
        cell_data["cells/" + fb_db.generate_key()] = pos

    # update the database
    fb_db.update(cell_data)

    return True


def MarchingCubes(data):

    # DEPRECATED
    ############

    # convert string to json
    if isinstance(data, str):
        data = json.loads(data)

    # retrieve the position list
    voxel_positions = np.array(data['voxel_positions'])

    # construct the volume
    minbound = voxel_positions.min(axis=0)
    maxbound = voxel_positions.max(axis=0)
    volume = np.zeros(maxbound-minbound + 1).astype(int)

    # fill in the volume
    mapped_ind = voxel_positions - minbound
    volume[mapped_ind[:, 0], mapped_ind[:, 1], mapped_ind[:, 2]] = 1

    # pad the volume with zero in every direction
    volume = np.pad(volume, (1, 1), mode='constant', constant_values=(0, 0))

    # the id of voxels (0,1,2, ... n)
    volume_inds = np.arange(volume.size).reshape(volume.shape)

    # shifts to check 8 corner of cube (multiply by -1 since shift goes backward)
    shifts = np.array([
        [0, 0, 0],  # 1
        [1, 0, 0],  # 2
        [0, 1, 0],  # 4
        [1, 1, 0],  # 8
        [0, 0, 1],  # 16
        [1, 0, 1],  # 32
        [0, 1, 1],  # 64
        [1, 1, 1]   # 128
    ])*-1

    # gattering all the replacements in the collumns
    replaced_columns = [
        np.roll(volume_inds, shift, np.arange(3)).ravel() for shift in shifts]

    # stacking the columns
    cell_corners = np.stack(replaced_columns, axis=-1)

    # replace neighbours by their value in volume
    volume_flat = volume.ravel()
    neighbor_values = volume_flat[cell_corners]

    # computing the cell tile id
    # the powers of 2 in an array
    legend = 2**np.arange(8)
    # multiply the corner with the power of two, sum them, and reshape to the original volume shape
    tile_id = np.sum(legend*neighbor_values, axis=1).reshape(volume.shape)
    # drop the last column, row and page (since cube-grid is 1 less than the voxel grid in every dimension)
    cube_grid = tile_id[:-1, :-1, :-1]

    # extract cube indicies
    cube_ind = np.transpose(np.indices(cube_grid.shape),
                            (1, 2, 3, 0)).reshape(-1, 3)
    # extract cube positions
    cube_pos = cube_ind + minbound - 0.5

    # extract cube tid
    cube_tid = cube_grid.ravel()

    # remove the cube position and tid where tid is 0
    filled_cube_pos = cube_pos[cube_tid > 0]
    filled_cube_tid = cube_tid[cube_tid > 0]

    # merge the position and tile_id of the cubes in one list
    cube_data = np.concatenate(
        (filled_cube_pos, np.transpose(filled_cube_tid[np.newaxis])), axis=-1)

    # package the results
    result = {
        # 'cube_positions': filled_cube_pos.tolist(),
        # 'cube_tid': filled_cube_tid.tolist(),
        'cube_data': cube_data.tolist(),
        # check if there is already a 'to_update' key i data, if there is add the 'cubes' to that key, if not, just init a new key and only include 'cubes'
        'to_update': data['to_update'] + ['cubes'] if 'to_update' in data else ['cubes'],
    }

    # extend the data dictionary with the result dictionary
    data.update(result)

    return data


def cors_function(request):
    # For more information about CORS and CORS preflight requests, see
    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request
    # for more information.

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    return ('Hello World!', 200, headers)
