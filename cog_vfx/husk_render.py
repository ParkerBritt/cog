import sys, subprocess, hou

def get_render_nodes(scene_path):
    hou.hipFile.load(scene_path, ignore_load_warnings=True)
    stage_nodes = hou.node("/stage").children()
    for stage_node in stage_nodes:
        node_type = stage_node.type().name()
        if(not node_type.startswith("parker::RENDER_layer::")):
            continue
        print("__RETURN_RENDER_NODE:"+stage_node.evalParm("layer_name")+":"+stage_node.path())

def exec_render_node(scene_path, node_path):
# print("rendering scene:", scene_path)
# print("args", sys.argv)

    hou.hipFile.load(scene_path, ignore_load_warnings=True)

    layer_node = hou.node(node_path)

    layer_node.parm("render_usd").pressButton()
