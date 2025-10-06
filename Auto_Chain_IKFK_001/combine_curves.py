import maya.cmds as cmds


def auto_assign_curve_shapes(base_name="Leg_practice_L", version="001"):
    segments = ["upperLeg", "middleLeg", "endLeg"]

    for seg in segments:
        ctrl_name = f"{seg}_{base_name}_ctrl_{version}"
        joint_name = f"{seg}_{base_name}_joint_{version}"

        # existe joint
        if not cmds.objExists(joint_name):
            cmds.warning(f"⚠️ No existe el joint: {joint_name}")
            continue

        # existe curva (si no existe la crea)
        if not cmds.objExists(ctrl_name):
            ctrl_name = cmds.circle(name=ctrl_name, normal=(0, 1, 0), radius=2)[0]
            print(f"➕ Creada curva: {ctrl_name}")

        # Obtener shapes de la curva
        shapes = cmds.listRelatives(ctrl_name, shapes=True, fullPath=True)
        if not shapes:
            cmds.warning(f"⚠️ {ctrl_name} no tiene shapes.")
            continue

        # Parentar shapes al joint
        for sh in shapes:
            cmds.parent(sh, joint_name, add=True, shape=True, relative=True)
        print(f"✅ Shape de {ctrl_name} → {joint_name}")

        # Eliminar el transform de la curva (ya que el shape quedó en el joint)
        if cmds.objExists(ctrl_name):
            cmds.delete(ctrl_name)
