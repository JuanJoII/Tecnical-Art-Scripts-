import maya.cmds as cmds

def constrain_joints_to_targets(joint_base="joint", target_base="spineTarget_ctrl", num_pairs=5):
    """
    Crea Parent Constraints entre cada joint y su target correspondiente.
    Mantiene offset activado.
    """
    constraints = []

    for i in range(1, num_pairs+1):
        jnt = f"{joint_base}_{i:03d}"
        tgt = f"{target_base}_{i:03d}"

        if not cmds.objExists(jnt) or not cmds.objExists(tgt):
            cmds.warning(f"⚠️ No se encontró {jnt} o {tgt}, se omite.")
            continue

        con = cmds.parentConstraint(
            tgt, jnt,
            maintainOffset=True
        )[0]

        constraints.append(con)
        print(f"✅ ParentConstraint creado: {jnt} ← {tgt}")

    return constraints

if __name__ == "__main__":
    constrain_joints_to_targets()