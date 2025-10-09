import maya.cmds as cmds


def create_spine_controls(base_name="spineLoc_ctrl", num_ctrls=None, radius=2.0):
    """
    Crea NURBS circles y los combina como shapes en los locators existentes.
    """
    # Detectar cuántos locators existen
    locators = cmds.ls(f"{base_name}_*", type="transform")
    num_ctrls = num_ctrls or len(locators)

    for i in range(num_ctrls):
        loc = f"{base_name}_{i + 1:03d}"
        if not cmds.objExists(loc):
            continue

        circle = cmds.circle(name=f"{loc}_circle", normal=(0, 1, 0), radius=radius)[0]
        pos = cmds.xform(loc, q=True, ws=True, t=True)
        cmds.xform(circle, ws=True, t=pos)
        shapes = cmds.listRelatives(circle, shapes=True, fullPath=True) or []
        for shape in shapes:
            cmds.parent(shape, loc, add=True, shape=True)
        cmds.delete(circle)
        print(f"✅ Control agregado a {loc}")


# Prueba del modulo
if __name__ == "__main__":
    create_spine_controls()
