import maya.cmds as cmds
from Auto_Tail import at_ui
from Auto_Column import spline_auto_rig
from Auto_Chain_IKFK import select_tool


def open_main_rig_launcher():
    """
    Ventana central para acceder a todas las herramientas de rigging.
    """
    window_name = "mainRigLauncher"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="🎛️ Rigging Tools Launcher", widthHeight=(320, 280))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=12, columnAlign="center")

    cmds.text(label="🦾 Central de Herramientas de Rigging", height=30, align="center")
    cmds.separator(height=10, style="in")

    # --- Auto Tail Rig ---
    cmds.button(
        label="🐍 Auto Tail Rig Tool",
        bgc=(0.3, 0.5, 0.8),
        height=40,
        command=lambda *_: at_ui.auto_tail_ui(),
    )

    # --- Spine Auto Rig ---
    cmds.button(
        label="🦴 Spine Auto Rig Tool",
        bgc=(0.4, 0.7, 0.6),
        height=40,
        command=lambda *_: spline_auto_rig.open_spine_auto_rig_ui(),
    )

    # --- IK/FK Rig Tools ---
    cmds.button(
        label="🔗 IK / FK Rig Tools",
        bgc=(0.6, 0.6, 0.4),
        height=40,
        command=lambda *_: select_tool.open_ui(),
    )

    cmds.separator(height=15, style="in")
    cmds.button(
        label="❌ Cerrar",
        bgc=(0.5, 0.2, 0.2),
        command=lambda *_: cmds.deleteUI(window_name),
    )

    cmds.showWindow(window_name)


if __name__ == "__main__":
    open_main_rig_launcher()
