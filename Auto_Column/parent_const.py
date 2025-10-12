import maya.cmds as cmds


def constrain_joints_to_targets(
    joint_base="joint", target_base="spineTarget_ctrl", num_pairs=None
):
    joints = cmds.ls(f"{joint_base}_*", type="joint")
    targets = cmds.ls(f"{target_base}_*", type="transform")
    num_pairs = num_pairs or min(len(joints), len(targets))

    for i in range(num_pairs):
        jnt = f"{joint_base}_{i + 1:03d}"
        tgt = f"{target_base}_{i + 1:03d}"
        if not cmds.objExists(jnt) or not cmds.objExists(tgt):
            continue
        cmds.parentConstraint(tgt, jnt, maintainOffset=True)
        print(f"✅ ParentConstraint: {jnt} ← {tgt}")


if __name__ == "__main__":
    constrain_joints_to_targets()
