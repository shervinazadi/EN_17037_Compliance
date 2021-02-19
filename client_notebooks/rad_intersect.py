import pyrebase
import json
import trimesh as tm
import pandas as pd
import requests

with open("../docker_content/fb_auth.json") as json_file:
    config = json.load(json_file)

# create firebase app
firebase = pyrebase.initialize_app(config)

# access the database
fb_db = firebase.database()

def intersect(mesh, ray_src, ray_dir, server_address):

    # init a new data key
    main_key = fb_db.generate_key()

    # extract data
    V = pd.DataFrame(mesh.vertices, columns=["X", "Y", "Z"])
    F = pd.DataFrame(mesh.faces, columns=["V0", "V1", "V2"])
    RS = pd.DataFrame(ray_src, columns=["X", "Y", "Z"])
    RD = pd.DataFrame(ray_dir, columns=["X", "Y", "Z"])

    # Create data dict
    data_dict = {
        main_key + "/V": V.T.to_dict(),
        main_key + "/F": F.T.to_dict(),
        main_key + "/RS": RS.T.to_dict(),
        main_key + "/RD": RD.T.to_dict(),
    }
    
    # update database
    fb_db.update(data_dict)

    # send request
    req_data = {
        "functions": [
            { 
          "func_name": "intersect",
          "main_key": main_key,
        }
        ],
      }
    # send request
    response = requests.get(server_address, params = json.dumps(req_data))

    # req = urllib2.Request(server_address)
    # req.add_header('Content-Type', 'application/json')

    # # receive the response
    # response = urllib2.urlopen(req, json.dumps(req_data))
    print(response.text)