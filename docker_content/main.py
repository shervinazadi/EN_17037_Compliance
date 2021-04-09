import numpy as np
import pandas as pd
import json
import copy
import random
import itertools
import pyrebase
# import topogenesis as tg
import honeybee_plus as hb
import EN_17037_Recipes as enr
import os

with open("fb_auth.json") as json_file:
    config = json.load(json_file)

# create firebase app
firebase = pyrebase.initialize_app(config)

# access the database
fb_db = firebase.database()


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

    funcs = json.loads(list(dict(request.args).keys())[0])['functions']

    # iterate over the functions and run them one by one
    for func in funcs:
        func_name = func['func_name']
        data_key = func['main_key']
        # retrieve the requested function
        func = globals()[func_name]

        # run the requested function and updating the funcdata
        funcData = func(data_key)

    d = {
        'result': "Done"
    }
    return (funcData, 200, headers)

def intersect(main_key):
    # retrive all the data
    db = fb_db.child(main_key).get()

    # retrieve the data as dictionary
    db_data = db.val()

    # dataframes
    V_df = pd.DataFrame.from_dict(db_data["V"], orient='columns')
    F_df = pd.DataFrame.from_dict(db_data["F"], orient='columns')
    RS_df = pd.DataFrame.from_dict(db_data["RS"], orient='columns')
    RD_df = pd.DataFrame.from_dict(db_data["RD"], orient='columns')

    # project name
    project_name = main_key[1:]

    # mesh to hb surfaces
    hb_surfaces = enr.mesh_to_hbsurface(V_df.to_numpy(), F_df.to_numpy(), 0, "this_mesh", enr.material_plastic)

    # create analysis grid
    analysis_grid = enr.AnalysisGrid.from_points_and_vectors(RS_df.values.tolist(), RD_df.values.tolist(), project_name)

    # put the recipe together
    rp = enr.ContextViewGridBased(analysis_grids=(analysis_grid,),hb_objects=hb_surfaces)

    # write simulation to folder
    batch_file = rp.write(target_folder='.', project_name=project_name)

    # run the simulation
    rp.run(batch_file, debug=False)

    # load rtrace results
    rs_path = os.path.join(project_name, 'gridbased', 'rtrace_res.txt')
    rtrace_res = pd.read_csv(rs_path, skiprows=8, sep='\t', usecols=[3,4,5], header=None, names=['int_name', 'first_dist', 'last_dist'])

    # Create data dict
    data_dict = {
        main_key + "/RI": rtrace_res.T.to_dict(),
    }

    # update database
    fb_db.update(data_dict)
    
    return(f"{len(rtrace_res)} intersection found")

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
