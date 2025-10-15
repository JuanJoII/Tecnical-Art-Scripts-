import maya.cmds as cmds


def get_joint_chain_from_selection():
    """Devuelve la cadena completa de joints desde el primer seleccionado."""
    sel = cmds.ls(selection=True, type="joint")
    if not sel:
        cmds.warning("⚠️ Selecciona el primer joint de la cadena que deseas limpiar.")
        return []

    chain = [sel[0]]
    child = cmds.listRelatives(sel[0], children=True, type="joint")
    while child:
        chain.append(child[0])
        child = cmds.listRelatives(child[0], children=True, type="joint")
    return chain


def get_next_clear_name(base="Clear"):
    """Genera un nombre de grupo 'Clear_001', 'Clear_002', etc."""
    i = 1
    while cmds.objExists(f"{base}_{i:03d}"):
        i += 1
    return f"{base}_{i:03d}"


def clear_rig_chain():
    """
    Duplica la cadena seleccionada (manteniendo nombres originales)
    y agrupa TODO lo demás (incluyendo la cadena vieja) dentro de un grupo Clear_###.
    El grupo Clear se deja oculto para simular que fue eliminado.
    """
    chain = get_joint_chain_from_selection()
    if not chain:
        return

    root_joint = chain[0]

    # Crear grupo de limpieza
    clear_grp = get_next_clear_name()
    cmds.group(empty=True, name=clear_grp)
    print(f"🧹 Creando grupo de limpieza: {clear_grp}")

    # Agrupar TODO (incluyendo la cadena original) dentro del grupo Clear
    all_objs = cmds.ls(assemblies=True)
    for obj in all_objs:
        if obj != clear_grp:
            try:
                cmds.parent(obj, clear_grp)
            except Exception:
                pass

    # Duplicar la cadena desde dentro del grupo Clear con sufijo temporal
    try:
        dup_root = cmds.duplicate(f"{clear_grp}|{root_joint}", renameChildren=True)[0]
    except Exception as e:
        cmds.warning(f"⚠️ Error al duplicar la cadena: {e}")
        return

    # Sacar el duplicado fuera del grupo Clear
    cmds.parent(dup_root, world=True)

    # Obtener lista ordenada de joints del duplicado
    dup_chain = [dup_root] + (
        cmds.listRelatives(dup_root, allDescendents=True, type="joint") or []
    )
    dup_chain = list(reversed(dup_chain))

    # Renombrar duplicados con sufijo temporal para evitar conflictos
    temp_names = []
    for jnt in dup_chain:
        new_name = f"{jnt}_TMP"
        renamed = cmds.rename(jnt, new_name)
        temp_names.append(renamed)

    # Renombrar los temporales con los nombres originales
    for temp_jnt, orig_jnt in zip(temp_names, chain):
        try:
            cmds.rename(temp_jnt, orig_jnt)
        except Exception as e:
            cmds.warning(f"⚠️ Error al renombrar {temp_jnt} → {orig_jnt}: {e}")

    # Ocultar el grupo de limpieza
    cmds.setAttr(f"{clear_grp}.visibility", 0)

    # Seleccionar la nueva cadena limpia
    cmds.select(root_joint, replace=True)

    print(f"✅ Cadena '{root_joint}' limpia creada sin conflictos de nombres.")
    print(f"🫧 Todo el rig anterior fue movido y ocultado en '{clear_grp}'.")


if __name__ == "__main__":
    clear_rig_chain()
