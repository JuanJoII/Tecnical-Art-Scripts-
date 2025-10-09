import maya.cmds as cmds


def create_spine_target_aims(base_name="spineTarget_ctrl", num_targets=None):
    targets = cmds.ls(f"{base_name}_*", type="transform")
    num_targets = num_targets or len(targets)

    for i in range(1, num_targets):
        target = f"{base_name}_{i:03d}"
        source = f"{base_name}_{i + 1:03d}"
        if not cmds.objExists(source) or not cmds.objExists(target):
            continue
        cmds.aimConstraint(
            target,
            source,
            maintainOffset=False,
            aimVector=(0, 1, 0),
            upVector=(0, 0, 1),
            worldUpType="scene",
        )
        print(f"✅ AimConstraint: {source} → {target}")


if __name__ == "__main__":
    create_spine_target_aims()
