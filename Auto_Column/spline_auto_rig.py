import maya.cmds as cmds
from Auto_Column import (
    locators2curve,
    doble_parent,
    create_controls,
    tarjet_curve,
    aim_const,
    parent_const,
    all_tools,
)


def get_joint_chain_from_selection():
    """Devuelve la cadena completa de joints desde el primer seleccionado."""
    sel = cmds.ls(selection=True, type="joint")
    if not sel:
        cmds.warning("⚠️ Selecciona el primer joint de la cadena.")
        return []

    chain = [sel[0]]
    child = cmds.listRelatives(sel[0], children=True, type="joint")
    while child:
        chain.append(child[0])
        child = cmds.listRelatives(child[0], children=True, type="joint")
    return chain


def rename_joint_chain_if_needed(chain):
    """
    Renombra la cadena de joints seleccionada si el root no se llama 'joint_001'.
    Usa el patrón estándar: joint_001, joint_002, joint_003, etc.
    """
    if not chain:
        return chain

    root_name = chain[0]
    if root_name == "joint_001":
        print("✅ Los joints ya tienen el nombre correcto, no se renombrará.")
        return chain

    print("🧩 Renombrando cadena de joints al formato 'joint_001'...")
    renamed_chain = []

    for i, jnt in enumerate(chain, start=1):
        new_name = f"joint_{i:03d}"
        try:
            new_name = cmds.rename(jnt, new_name)
            renamed_chain.append(new_name)
            print(f"   {jnt} → {new_name}")
        except Exception as e:
            cmds.warning(f"⚠️ No se pudo renombrar {jnt}: {e}")
            renamed_chain.append(jnt)

    print("✅ Cadena renombrada correctamente.")
    return renamed_chain


def build_spine_from_existing_chain():
    """Crea la estructura del rig a partir de una cadena existente."""
    chain = get_joint_chain_from_selection()
    if not chain:
        return

    # 🔁 Renombrar si es necesario
    chain = rename_joint_chain_if_needed(chain)

    num_joints = len(chain)
    base_name = chain[0].split("_")[0]  # inferencia del prefijo
    curve_name = f"{base_name}_curve"

    # Obtener posiciones
    positions = [cmds.xform(j, q=True, ws=True, t=True) for j in chain]

    # Crear curva usando esas posiciones
    curve = cmds.curve(name=curve_name, degree=1, ep=positions)

    # Crear el resto del pipeline
    locators2curve.create_spine_locators(curve_name=curve_name, num_locs=num_joints)
    doble_parent.connect_locators_to_curve(curve_name=curve_name, num_locs=num_joints)
    create_controls.create_spine_controls(num_ctrls=num_joints)
    tarjet_curve.create_spine_targets(curve_name=curve_name, num_targets=num_joints)
    aim_const.create_spine_target_aims(num_targets=num_joints)
    parent_const.constrain_joints_to_targets(num_pairs=num_joints)

    print(f"✅ Rig de columna generado a partir de {num_joints} joints existentes.")


def open_spine_auto_rig_ui():
    """Interfaz con opción de crear o usar joints existentes."""
    if cmds.window("spineAutoRigWin", exists=True):
        cmds.deleteUI("spineAutoRigWin")

    win = cmds.window(
        "spineAutoRigWin", title="Spine Auto Rig Tool", widthHeight=(300, 200)
    )
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="🦴 Spine Auto Rig Tool", align="center", height=30)
    cmds.button(
        label="Crear desde cero",
        bgc=(0.3, 0.6, 0.3),
        command=lambda *args: all_tools.open_spine_rig_ui(),
    )
    cmds.button(
        label="Usar joints seleccionados",
        bgc=(0.3, 0.5, 0.8),
        command=lambda *args: build_spine_from_existing_chain(),
    )

    cmds.showWindow(win)


if __name__ == "__main__":
    open_spine_auto_rig_ui()