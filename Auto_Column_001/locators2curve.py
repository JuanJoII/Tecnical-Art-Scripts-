import maya.cmds as cmds

def create_spine_locators(curve_name="splineCurve_001", num_locs=5, base_name="spineLoc_ctrl"):
    """
    Crea locators y los conecta a los control points de una spline curve.
    Cada locator controla un CV de la curva.
    """
    # Verificar curva
    if not cmds.objExists(curve_name):
        cmds.warning(f"⚠️ La curva {curve_name} no existe.")
        return []

    # Obtener shape de la curva
    shapes = cmds.listRelatives(curve_name, shapes=True)
    if not shapes:
        cmds.warning(f"⚠️ La curva {curve_name} no tiene shape.")
        return []
    curve_shape = shapes[0]

    locators = []

    for i in range(num_locs):
        # Crear locator
        loc = cmds.spaceLocator(name=f"{base_name}_{i+1:03d}")[0]
        locators.append(loc)

        # Snap inicial al CV correspondiente
        cv_pos = cmds.pointPosition(f"{curve_name}.cv[{i}]")
        cmds.xform(loc, ws=True, t=cv_pos)

        # Conectar translate del locator → controlPoint de la curva
        cmds.connectAttr(f"{loc}.translate", f"{curve_shape}.controlPoints[{i}]")

        print(f"✅ {loc} conectado a {curve_shape}.controlPoints[{i}]")

    return locators

# Uso:
# create_spine_locators()
if __name__ == "__main__":
    create_spine_locators()