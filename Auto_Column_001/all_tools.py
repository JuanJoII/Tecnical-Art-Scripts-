import maya.cmds as cmds
from Auto_Column_001 import joint_slpine, locators2curve, doble_parent, create_controls, tarjet_curve, aim_const, parent_const

def open_spine_rig_ui():
    """Interfaz para crear y controlar el Spine Rig paso a paso."""
    if cmds.window("spineRigWin", exists=True):
        cmds.deleteUI("spineRigWin")

    win = cmds.window("spineRigWin", title="Spine Rig Tool", widthHeight=(400, 650))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    # --- Parámetros principales ---
    cmds.text(label="⚙️ Parámetros Spine Rig", align="center")
    num_joints_field = cmds.intFieldGrp(label="Num Joints:", value1=5)
    base_name_field = cmds.textFieldGrp(label="Base Name:", text="joint")
    curve_name_field = cmds.textFieldGrp(label="Curve Name:", text="splineCurve_001")
    radius_field = cmds.floatFieldGrp(label="Control Radius:", value1=2.0)

    cmds.separator(h=15, style="in")

    # --- Botones para cada paso ---
    cmds.text(label="▶ Ejecutar Pasos", align="center")

    cmds.button(
        label="Paso 1 - Crear Joints + Curva",
        bgc=(0.3, 0.6, 0.3),
        command=lambda *args: joint_slpine.create_spine_chain_s_shape(
            num_joints=cmds.intFieldGrp(num_joints_field, q=True, value1=True),
            base_name=cmds.textFieldGrp(base_name_field, q=True, text=True),
            curve_name=cmds.textFieldGrp(curve_name_field, q=True, text=True),
        ),
    )

    cmds.button(
        label="Paso 2 - Crear Locators",
        command=lambda *args: locators2curve.create_spine_locators(
            curve_name=cmds.textFieldGrp(curve_name_field, q=True, text=True),
            num_locs=cmds.intFieldGrp(num_joints_field, q=True, value1=True)
        ),
    )


    cmds.button(
        label="Paso 3 - Conexión Decompose",
        command=lambda *args: doble_parent.connect_locators_to_curve(
            curve_name=cmds.textFieldGrp(curve_name_field, q=True, text=True),
            num_locs=cmds.intFieldGrp(num_joints_field, q=True, value1=True)
        ),
    )


    cmds.button(
        label="Paso 4 - Crear Controles",
        command=lambda *args: create_controls.create_spine_controls(
            radius=cmds.floatFieldGrp(radius_field, q=True, value1=True)
        ),
    )

    cmds.button(
        label="Paso 5 - Crear Targets",
        command=lambda *args: tarjet_curve.create_spine_targets(
            curve_name=cmds.textFieldGrp(curve_name_field, q=True, text=True)
        ),
    )

    cmds.button(
        label="Paso 6 - Aim Constraints",
        command=lambda *args: aim_const.create_spine_target_aims(),
    )

    cmds.button(
        label="Paso 7 - Parent Constraints Joints",
        command=lambda *args: parent_const.constrain_joints_to_targets(),
    )

    cmds.showWindow(win)

if __name__ == "__main__":
    open_spine_rig_ui()