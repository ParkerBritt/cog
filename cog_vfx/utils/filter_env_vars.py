shot_vars = ["fps", "res_width", "res_height", "shot_num", "start_frame", "end_frame"]
shot_remap = {"file_name": "form_shot_num"}
asset_vars = ["name", "res_width", "res_height", "shot_num", "start_frame", "end_frame"]


def filter_env_vars(prospective_vars=None, element_type=None):
    element_vars = []
    if prospective_vars and element_type:
        if element_type == "shot":
            valid_vars = shot_vars
            remap_vars = shot_remap
        elif element_type == "asset":
            valid_vars = asset_vars
            remap_vars = None
        for key in prospective_vars:
            # print("looking at key:", key, "in prospective_vars", prospective_vars)
            if key in valid_vars:
                # print("KEY", key, "IN VALID VARS", valid_vars)
                element_vars.append({key: prospective_vars[key]})
            elif key in remap_vars:
                print("KEY", key, "IN REMAP VARS", remap_vars)
                # print("THING", {shot_remap[key]: prospective_vars[key]})
                element_vars.append({shot_remap[key]: prospective_vars[key]})
    return element_vars
