import maya.cmds as cmds

def connect_locators_to_curve(curve_name="splineCurve_001", base_name="spineLoc_ctrl", num_locs=5):
    """
    Conecta locators a los CVs de una curva spline usando nodos decomposeMatrix.
    """
    # Verificar curva y shape
    if not cmds.objExists(curve_name):
        cmds.warning(f"⚠️ La curva {curve_name} no existe.")
        return
    shapes = cmds.listRelatives(curve_name, shapes=True)
    if not shapes:
        cmds.warning(f"⚠️ La curva {curve_name} no tiene shape.")
        return
    curve_shape = shapes[0]

    for i in range(num_locs):
        loc = f"{base_name}_{i+1:03d}"
        if not cmds.objExists(loc):
            cmds.warning(f"⚠️ Locator {loc} no existe, se omite.")
            continue

        # Crear nodo decomposeMatrix
        decomp = cmds.createNode("decomposeMatrix", name=f"{loc}_decompMatrix")

        # Conexiones
        cmds.connectAttr(f"{loc}.worldMatrix[0]", f"{decomp}.inputMatrix", force=True)
        cmds.connectAttr(f"{decomp}.outputTranslate", f"{curve_shape}.controlPoints[{i}]", force=True)

        print(f"✅ {loc} conectado con {decomp} → {curve_shape}.controlPoints[{i}]")

    # Emparentar locators bajo la curva
    cmds.parent([f"{base_name}_{i+1:03d}" for i in range(num_locs)], curve_name)

    print(f"📌 Todos los locators emparentados bajo {curve_name}")
