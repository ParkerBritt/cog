import subprocess
import sys

import hou


def get_render_nodes(scene_path):
    render_node_types = ["RENDER_layer", "SCENE_layer_shadow"]
    hou.hipFile.load(scene_path, ignore_load_warnings=True)
    stage_nodes = hou.node("/stage").children()
    for stage_node in stage_nodes:
        node_type_full = stage_node.type().name()
        print("node_type", node_type_full)
        if not node_type_full.startswith("parker::"):
            print("doesn't start with parker")
            continue
        node_type_split = node_type_full.split("::")
        print("split", node_type_split)
        if len(node_type_split) < 2 or not node_type_split[1] in render_node_types:
            continue
        print(
            f"__RETURN_RENDER_NODE:{stage_node.evalParm('layer_name')}:{stage_node.path()}"
        )

    # close hip file
    hou.hipFile.clear()


def exec_render_node(scene_path, node_path):
    # print("rendering scene:", scene_path)
    # print("args", sys.argv)

    hou.hipFile.load(scene_path, ignore_load_warnings=True)

    layer_node = hou.node(node_path)

    layer_node.parm("render_context").set(0)
    layer_node.parm("render_usd").pressButton()

    # close hip file
    hou.hipFile.clear()
