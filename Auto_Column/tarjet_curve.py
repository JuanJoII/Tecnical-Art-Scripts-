import maya.cmds as cmds


def create_spine_targets(
    curve_name="splineCurve_001", num_targets=None, base_name="spineTarget_ctrl"
):
    """
    Crea locators 'spineTarget_ctrl_###' distribuidos uniformemente sobre una curva.
    Usa arcLengthDimension para parametrizar de 0 a 1 independientemente de la longitud real.
    """
    if not cmds.objExists(curve_name):
        cmds.warning(f"⚠️ La curva {curve_name} no existe.")
        return []

    shapes = cmds.listRelatives(curve_name, shapes=True)
    if not shapes:
        cmds.warning(f"⚠️ La curva {curve_name} no tiene shape.")
        return []
    curve_shape = shapes[0]

    # Detectar número de CVs
    num_cvs = cmds.getAttr(f"{curve_shape}.controlPoints", size=True)
    num_targets = num_targets or num_cvs

    # Crear un nodo temporal para obtener la longitud total
    arc_len_node = cmds.arclen(curve_name, constructionHistory=True)
    curve_length = cmds.getAttr(f"{arc_len_node}.arcLength")
    cmds.delete(arc_len_node)

    step = curve_length / (num_targets - 1)
    targets = []

    for i in range(num_targets):
        loc = cmds.spaceLocator(name=f"{base_name}_{i + 1:03d}")[0]
        poc = cmds.createNode("pointOnCurveInfo", name=f"{loc}_POC")
        cmds.connectAttr(
            f"{curve_shape}.worldSpace[0]", f"{poc}.inputCurve", force=True
        )
        cmds.connectAttr(f"{poc}.position", f"{loc}.translate", force=True)
        cmds.setAttr(f"{poc}.turnOnPercentage", 0)
        cmds.setAttr(f"{poc}.parameter", i * step)
        targets.append(loc)
        print(f"✅ {loc} colocado a lo largo de la curva (param={i * step:.2f})")

    print(f"📍 {len(targets)} targets creados sobre {curve_name}")
    return targets


# Prueba del modulo
if __name__ == "__main__":
    create_spine_targets()
