import maya.cmds as cmds

def create_spine_targets(curve_name="splineCurve_001", num_targets=5, base_name="spineTarget_ctrl"):
    """
    Crea locators 'spineTarget_ctrl_###' conectados a una curva con nodos pointOnCurveInfo.
    Distribuye los targets a lo largo de la curva ajustando el parámetro.
    """
    if not cmds.objExists(curve_name):
        cmds.warning(f"⚠️ La curva {curve_name} no existe.")
        return []

    shapes = cmds.listRelatives(curve_name, shapes=True)
    if not shapes:
        cmds.warning(f"⚠️ La curva {curve_name} no tiene shape.")
        return []
    curve_shape = shapes[0]

    targets = []
    step = 1.0 / (num_targets - 1) if num_targets > 1 else 1.0

    for i in range(num_targets):
        # Crear locator
        loc = cmds.spaceLocator(name=f"{base_name}_{i+1:03d}")[0]
        targets.append(loc)

        # Crear nodo pointOnCurveInfo
        poc = cmds.createNode("pointOnCurveInfo", name=f"{loc}_POC")

        # Conectar curva → pointOnCurveInfo
        cmds.connectAttr(f"{curve_shape}.worldSpace[0]", f"{poc}.inputCurve", force=True)

        # Conectar posición del poc → translate del locator
        cmds.connectAttr(f"{poc}.position", f"{loc}.translate", force=True)

        # Ajustar parámetro para distribuir a lo largo de la curva
        cmds.setAttr(f"{poc}.parameter", step * i)

        print(f"✅ {loc} conectado a {curve_shape} con {poc}, parámetro={step*i:.2f}")

    return targets

if __name__ == "__main__":
    create_spine_targets()