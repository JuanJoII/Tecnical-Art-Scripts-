import maya.cmds as cmds

def create_spine_target_aims(base_name="spineTarget_ctrl", num_targets=5):
    """
    Crea Aim Constraints secuenciales entre los spineTarget_ctrl_###.
    Desactiva Maintain Offset como indica la documentación.
    """
    aims = []

    for i in range(1, num_targets):
        target = f"{base_name}_{i:03d}"       # objeto hacia donde apunta
        source = f"{base_name}_{i+1:03d}"     # objeto que apunta

        if not cmds.objExists(source) or not cmds.objExists(target):
            cmds.warning(f"⚠️ Faltan {source} o {target}, se omite este constraint.")
            continue

        # Crear Aim Constraint (sin offset)
        aim = cmds.aimConstraint(
            target,
            source,
            maintainOffset=False,
            aimVector=(0,1,0),     # eje que apunta (ajústalo según tu rig)
            upVector=(0,0,1),      # eje de up
            worldUpType="scene"    # usa el up global de la escena
        )[0]

        aims.append(aim)
        print(f"✅ AimConstraint creado: {source} → {target}")

    return aims

if __name__ == "__main__":
    create_spine_target_aims()