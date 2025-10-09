import maya.cmds as cmds
from Auto_Chain_IKFK_001 import rename_chain, create_fk_groups, ik_system, combine_curves, orient_constrain, create_fkik_atr, conect_fkik_nodes


def open_ui():
    # Crear Ventana
    if cmds.window("simpleToolsWin", exists=True):
        cmds.deleteUI("simpleToolsWin")

    win = cmds.window("simpleToolsWin", title="Rig Tools", widthHeight=(200, 120))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    # Menú para elegir herramienta
    tool_menu = cmds.optionMenu(label="Elegir herramienta:")
    cmds.menuItem(label="Renombrar cadena")
    cmds.menuItem(label="Crear grupos 'Root' y 'Auto'")
    cmds.menuItem(label="Crear sistema IK")
    cmds.menuItem(label="Crear orient constrain")
    cmds.menuItem(label="Asignar curvas de control")
    cmds.menuItem(label="Crear atributo FKIK")
    cmds.menuItem(label="Conectar nodos FKIK")

    # Botón ejecutar
    def run_tool(*args):
        choice = cmds.optionMenu(tool_menu, q=True, value=True)
        if choice == "Renombrar cadena":
            rename_chain.open_rename_parameters()
        elif choice == "Crear grupos 'Root' y 'Auto'":
            create_fk_groups.create_fk_groups()
        elif choice == "Crear sistema IK":
            ik_system.create_ik_system()
        elif choice == "Crear orient constrain":
            orient_constrain.create_leg_orient_constraints()
        elif choice == "Asignar curvas de control":
            combine_curves.auto_assign_curve_shapes()
        elif choice == "Crear atributo FKIK":
            create_fkik_atr.create_fkik_attribute()
        elif choice == "Conectar nodos FKIK":
            conect_fkik_nodes.connect_fkik_nodes()

    cmds.button(label="▶ Ejecutar", height=40, bgc=(0.3, 0.6, 0.3), command=run_tool)
    cmds.showWindow(win)


if __name__ == "__main__":
    open_ui()
