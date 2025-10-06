import maya.cmds as cmds
from . import rename_chain, orient_constrain, combine_curves


def open_ui():
    # Crear Ventana
    if cmds.window("simpleToolsWin", exists=True):
        cmds.deleteUI("simpleToolsWin")

    win = cmds.window("simpleToolsWin", title="Rig Tools", widthHeight=(200, 120))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    # Menú para elegir herramienta
    tool_menu = cmds.optionMenu(label="Elegir herramienta:")
    cmds.menuItem(label="Renombrar cadena")
    cmds.menuItem(label="Crear orient constrain")
    cmds.menuItem(label="Asignar curvas de control")

    # Botón ejecutar
    def run_tool(*args):
        choice = cmds.optionMenu(tool_menu, q=True, value=True)
        if choice == "Renombrar cadena":
            rename_chain.open_rename_parameters()
        elif choice == "Crear orient constrain":
            orient_constrain.create_leg_orient_constraints()
        elif choice == "Asignar curvas de control":
            combine_curves.auto_assign_curve_shapes()

    cmds.button(label="▶ Ejecutar", height=40, bgc=(0.3, 0.6, 0.3), command=run_tool)
    cmds.showWindow(win)
