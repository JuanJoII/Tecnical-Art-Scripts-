import maya.cmds as cmds


def create_spine_locators(
    curve_name="splineCurve_001", num_locs=None, base_name="spineLoc_ctrl"
):
    """
    Paso 2: Crea y alinea locators en cada CV de la curva spline.
    No realiza ninguna conexión nodal (eso lo hace el paso 3).
    """
    if not cmds.objExists(curve_name):
        cmds.warning(f"⚠️ La curva {curve_name} no existe.")
        return []

    # Obtener shape de la curva
    shapes = cmds.listRelatives(curve_name, shapes=True, fullPath=True)
    if not shapes:
        cmds.warning(f"⚠️ La curva {curve_name} no tiene shape.")
        return []
    curve_shape = shapes[0]

    # Detectar cantidad de CVs
    num_cvs = cmds.getAttr(f"{curve_shape}.controlPoints", size=True)
    num_locs = num_locs or num_cvs
    if num_locs > num_cvs:
        num_locs = num_cvs

    locators = []
    for i in range(num_locs):
        loc_name = f"{base_name}_{i + 1:03d}"

        # Crear locator (si no existe)
        if cmds.objExists(loc_name):
            loc = loc_name
        else:
            loc = cmds.spaceLocator(name=loc_name)[0]

        # Obtener posición del CV en espacio mundial
        world_pos = cmds.pointPosition(f"{curve_name}.cv[{i}]", world=True)
        cmds.xform(loc, ws=True, t=world_pos)

        locators.append(loc)
        print(f"✅ {loc} posicionado sobre {curve_name}.cv[{i}]")

    # Agrupar los locators bajo la curva (solo si aún no están)
    safe_to_parent = []
    for loc in locators:
        parent = cmds.listRelatives(loc, parent=True)
        if not parent or parent[0] != curve_name:
            safe_to_parent.append(loc)

    if safe_to_parent:
        try:
            cmds.parent(safe_to_parent, curve_name)
            print(f"📌 {len(safe_to_parent)} locators emparentados bajo {curve_name}")
        except RuntimeError as e:
            cmds.warning(f"⚠️ No se pudieron emparentar todos los locators: {e}")
    else:
        print("♻️ Todos los locators ya estaban correctamente parentados.")

    print(f"📍 {len(locators)} locators creados y posicionados en {curve_name}")
    return locators


# Prueba rápida
if __name__ == "__main__":
    create_spine_locators()
