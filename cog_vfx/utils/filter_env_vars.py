shot_vars = ["fps", "res_width", "res_height", "shot_num", "start_frame", "end_frame"]
asset_vars = ["name", "res_width", "res_height", "shot_num", "start_frame", "end_frame"]

def filter_env_vars(prospective_vars=None,element_type=None):
    element_vars = []
    if(prospective_vars and element_type):
        if(element_type=="shot"):
            valid_vars = shot_vars
        elif(element_type=="asset"):
            valid_vars = asset_vars
        for key in prospective_vars:
            if(key in valid_vars):
                element_vars.append({key:prospective_vars[key]})
    return element_vars

