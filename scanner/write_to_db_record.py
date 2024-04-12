import os 
import json
import requests

def put_node_package_ddb(item):
    # requests.post('http://localhost:3000/api/node/putNodePackage', json=item, headers={'Authorization': 'Bearer ' + 'token'})
    requests.post('http://127.0.0.1:6233/putNodePackage', json=item)

def put_node_ddb(item):
    requests.post('http://127.0.0.1:6233/putNode', json=item)

######v3

def custom_serializer(obj):
    """Convert non-serializable objects."""
    if isinstance(obj, (list, tuple, set)):
        return list(obj)  # Convert tuples and sets to lists
    elif isinstance(obj, dict):
        # Recursively apply to dictionary entries
        return {str(key): custom_serializer(value) for key, value in obj.items()}
    else:
        return obj

from .githubUtils import get_repo_user_and_name
from decimal import Decimal
import time
from  scanner.analyze_node_input import analyze_class

def write_to_db_record(input_dict): 
    time_before = input_dict['time_before']
    import_time = time.perf_counter() - time_before
    NODE_CLASS_MAPPINGS = input_dict['NODE_CLASS_MAPPINGS']
    NODE_DISPLAY_NAME_MAPPINGS = input_dict['NODE_DISPLAY_NAME_MAPPINGS']
    cur_node_package = input_dict['cur_node_package']
    module_path = input_dict['module_path']
    prev_nodes = input_dict['prev_nodes']
    success = input_dict['success']
    if 'ComfyUI-Manager' in module_path:
        return
    nodes_count = len(NODE_CLASS_MAPPINGS) - len(prev_nodes)
    
    print('🍻 nodes_count',nodes_count, 'cur_node_package',cur_node_package)
    if not os.path.isdir(module_path):
        return
    username, repo_name, default_branch_name, latest_commit = get_repo_user_and_name(module_path)
    packageID = username + '_' + repo_name
    custom_node_defs = {}
    for name in NODE_CLASS_MAPPINGS:
        try:
            if name not in prev_nodes: 
                paths = analyze_class(NODE_CLASS_MAPPINGS[name])
                # all_node = fetch_node_info()
                node_def = node_info(input_dict, name)
                data = {
                    "id": name+"~"+packageID,
                    "nodeType": name, 
                    "nodeDef": json.dumps(node_def), 
                    "packageID": packageID,
                    "gitRepo": username + '/' + repo_name,
                    "latestCommit": latest_commit}
                custom_node_defs[name] = node_def
                if paths is not None and len(paths) > 0:
                    data['folderPaths'] = json.dumps(paths, default=custom_serializer)
                put_node_ddb(data)
        except Exception as e:
            print("❌analyze imported node: error",e)
    put_node_package_ddb({
        **cur_node_package,
        'id': packageID,
        'gitRepo': username + '/' + repo_name,
        'gitHtmlUrl': 'https://github.com/'+username + '/' + repo_name,
        'nameID': repo_name,
        'authorID': 'admin',
        'status': 'IMPORT_'+ ('SUCCESS' if success else 'FAILED'),
        'defaultBranch': default_branch_name,
        'totalNodes':nodes_count,
        "importTime":str(import_time),
        'nodeDefs': json.dumps(custom_node_defs),
        "latestCommit": latest_commit
    })

# For COMFYUI BASE NODES
def save_base_nodes_to_ddb(NODE_CLASS_MAPPINGS):
    baseNodeDefs = {}
    for name in NODE_CLASS_MAPPINGS: 
        paths = analyze_class(NODE_CLASS_MAPPINGS[name])
        node_def = node_info(name)
        data = {
            "id": name+"~"+'comfyanonymous_ComfyUI',
            "nodeType": name, 
            "nodeDef": json.dumps(node_def), 
            "packageID": 'comfyanonymous_ComfyUI',
            "gitRepo": 'comfyanonymous/ComfyUI'}
        baseNodeDefs[name] = node_def
        if paths is not None and len(paths) > 0:
            data['folderPaths'] = json.dumps(paths, default=custom_serializer)
        put_node_ddb(data)
    put_node_package_ddb({
                    'id': 'comfyanonymous_ComfyUI',
                    'gitRepo': "comfyanonymous/ComfyUI",
                    'gitHtmlUrl': 'https://github.com/comfyanonymous/ComfyUI',
                    'nameID': 'ComfyUI',
                    'authorID': 'admin',
                    'status': 'IMPORT_SUCCESS',
                    'defaultBranch': 'master',
                    'totalNodes':len(NODE_CLASS_MAPPINGS),
                    'nodeDefs': json.dumps(baseNodeDefs)
                })

# copied from server.py
def node_info(input_dict, node_class:str):
    NODE_CLASS_MAPPINGS = input_dict['NODE_CLASS_MAPPINGS']
    NODE_DISPLAY_NAME_MAPPINGS = input_dict['NODE_DISPLAY_NAME_MAPPINGS']
    obj_class = NODE_CLASS_MAPPINGS[node_class]
    info = {}
    info['input'] = obj_class.INPUT_TYPES()
    info['output'] = obj_class.RETURN_TYPES
    info['output_is_list'] = obj_class.OUTPUT_IS_LIST if hasattr(obj_class, 'OUTPUT_IS_LIST') else [False] * len(obj_class.RETURN_TYPES)
    info['output_name'] = obj_class.RETURN_NAMES if hasattr(obj_class, 'RETURN_NAMES') else info['output']
    info['name'] = node_class
    info['display_name'] = NODE_DISPLAY_NAME_MAPPINGS[node_class] if node_class in NODE_DISPLAY_NAME_MAPPINGS.keys() else node_class
    info['description'] = obj_class.DESCRIPTION if hasattr(obj_class,'DESCRIPTION') else ''
    info['category'] = 'sd'
    if hasattr(obj_class, 'OUTPUT_NODE') and obj_class.OUTPUT_NODE == True:
        info['output_node'] = True
    else:
        info['output_node'] = False

    if hasattr(obj_class, 'CATEGORY'):
        info['category'] = obj_class.CATEGORY
    return info


import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

def fetch_node_info():
    url = "http://localhost:8188/object_info"
    
    try:
        with urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data
            else:
                print(f"Failed to fetch node info. Status code: {response.status}")
                return None
    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except URLError as e:
        print(f"URL Error: {e.reason}")
        return None
