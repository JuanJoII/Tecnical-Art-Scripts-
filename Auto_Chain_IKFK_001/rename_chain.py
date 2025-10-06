import maya.cmds as cmds
import re


def rename_hierarchy(
    chain_type: str = "joint",
    increment_version: bool = True,
    base_name: str = "Leg_practice_L",
):
    selection = cmds.ls(selection=True, type="joint")
    if not selection:
        cmds.warning("⚠️ Selecciona el joint raíz de la cadena a renombrar.")
        return

    root = selection[0]
    version_pattern = re.compile(r"(\d+)$")

    # Recorrer jerarquía en profundidad
    def walk_chain(node):
        yield node
        children = cmds.listRelatives(node, type="joint", children=True) or []
        for child in children:
            yield from walk_chain(child)

    joints = list(walk_chain(root))
    if not joints:
        cmds.warning(f"⚠️ No se encontraron joints hijos de {root}")
        return

    for i, obj in enumerate(joints, 1):
        # Segmento según profundidad
        if i == 1:
            segment = "upperLeg"
        elif i == 2:
            segment = "middleLeg"
        else:
            segment = "endLeg"

        if increment_version:
            match = version_pattern.search(obj)
            current_version = int(match.group(1)) + 1 if match else i
        else:
            current_version = 1

        new_name = f"{segment}_{base_name}_{chain_type}_{current_version:03d}"
        cmds.rename(obj, new_name)
        print(f"✅ {obj} → {new_name}")


def open_rename_parameters():
    if cmds.window("renameWin", exists=True):
        cmds.deleteUI("renameWin")

    win = cmds.window("renameWin", title="Rename Chain Tool", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

    base_name_field = cmds.textFieldGrp(label="Base Name:", text="Leg_practice_L")
    chain_type_field = cmds.textFieldGrp(label="Chain Type:", text="joint")
    increment_cb = cmds.checkBoxGrp(label="Increment: ", value1=False)

    def apply_rename(*args):
        base_name = cmds.textFieldGrp(base_name_field, q=True, text=True)
        chain_type = cmds.textFieldGrp(chain_type_field, q=True, text=True)
        increment_version = cmds.checkBoxGrp(increment_cb, q=True, value1=True)
        rename_hierarchy(chain_type, increment_version, base_name)

    cmds.button(label="Rename Selection", bgc=(0.3, 0.6, 0.3), command=apply_rename)
    cmds.showWindow(win)
