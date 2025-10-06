import maya.cmds as cmds

import maya.cmds as cmds

def create_spine_controls(base_name="spineLoc_ctrl", num_ctrls=5, radius=2.0):
    """
    Crea NURBS circles horizontales y los combina como shapes en los locators spineLoc_ctrl_###.
    No crea roots ni hace emparentamientos adicionales.
    """
    controls = []

    for i in range(num_ctrls):
        loc = f"{base_name}_{i+1:03d}"
        if not cmds.objExists(loc):
            cmds.warning(f"⚠️ Locator {loc} no existe, se omite.")
            continue

        # Crear círculo horizontal (normal en Y)
        circle = cmds.circle(name=f"{loc}_circle", normal=(0,1,0), radius=radius)[0]

        # Snapping: mover el círculo al locator
        pos = cmds.xform(loc, q=True, ws=True, t=True)
        cmds.xform(circle, ws=True, t=pos)

        # Combinar shapes del círculo en el locator
        shapes = cmds.listRelatives(circle, shapes=True, fullPath=True) or []
        for shape in shapes:
            cmds.parent(shape, loc, add=True, shape=True)

        # Eliminar transform sobrante
        cmds.delete(circle)

        print(f"✅ Shape de {circle} combinado en {loc}")
        controls.append(loc)

    return controls


if __name__ == "__main__":
    create_spine_controls()