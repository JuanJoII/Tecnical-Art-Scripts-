import maya.cmds as cmds


def get_joint_chain_from_selection():
    """Devuelve la cadena completa de joints desde el primer seleccionado (root→end)."""
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


def create_clean_chain_from_selection():
    """
    Flujo seguro para "limpiar" una cadena con rig:
    1) agrupa todo en Clear_### y lo oculta,
    2) renombra la cadena antigua (añade sufijo _OLD_<idx>),
    3) crea una nueva cadena de joints (root→end) en las mismas posiciones con los nombres originales.
    """
    chain = get_joint_chain_from_selection()
    if not chain:
        return

    orig_names = list(chain)
    root_joint = chain[0]
    num_joints = len(chain)
    clear_grp = get_next_clear_name()
    clear_grp = cmds.group(empty=True, name=clear_grp)
    print(f"🧹 Creando grupo de limpieza: {clear_grp}")

    all_roots = cmds.ls(assemblies=True)
    for obj in all_roots:
        if obj != clear_grp:
            try:
                cmds.parent(obj, clear_grp)
            except Exception:
                pass

    suffix = f"_OLD_{clear_grp.split('_')[-1]}"

    try:
        old_root_path = f"{clear_grp}|{root_joint}"
        if not cmds.objExists(old_root_path):
            candidates = (
                cmds.listRelatives(clear_grp, allDescendents=True, type="joint") or []
            )
            old_chain_paths = []
            for n in orig_names:
                found = [c for c in candidates if c.split("|")[-1] == n]
                if found:
                    old_chain_paths.append(found[0])
                else:
                    old_chain_paths.append(None)
        else:
            old_chain_paths = [old_root_path]
            children = (
                cmds.listRelatives(old_root_path, allDescendents=True, type="joint")
                or []
            )
            if children:
                desc = list(reversed(children))
                old_chain_paths += desc
    except Exception:
        old_chain_paths = None

    if not old_chain_paths:
        old_chain_paths = []
        candidates = (
            cmds.listRelatives(clear_grp, allDescendents=True, type="joint") or []
        )

        def depth(p):
            return p.count("|")

        candidates_sorted = sorted(candidates, key=depth)
        for name in orig_names:
            found = next(
                (c for c in candidates_sorted if c.split("|")[-1] == name), None
            )
            old_chain_paths.append(found)

    for orig_name, old_path in zip(reversed(orig_names), reversed(old_chain_paths)):
        if not old_path:
            cmds.warning(
                f"⚠️ No se encontró nodo antiguo para '{orig_name}' dentro de {clear_grp}."
            )
            continue
        new_old_name = f"{orig_name}{suffix}"
        try:
            cmds.rename(old_path, new_old_name)
            print(f"   Renombrado antiguo: {old_path} → {new_old_name}")
        except Exception as e:
            cmds.warning(f"⚠️ Error renombrando {old_path} → {new_old_name}: {e}")

    positions = []
    for orig_name in orig_names:
        old_name_with_suffix = f"{orig_name}{suffix}"
        if not cmds.objExists(old_name_with_suffix):
            cmds.warning(
                f"⚠️ No se encontró {old_name_with_suffix} para leer posición; se usará 0,0,0."
            )
            positions.append([0, 0, 0])
        else:
            pos = cmds.xform(
                old_name_with_suffix, query=True, worldSpace=True, translation=True
            )
            positions.append(pos)

    cmds.select(clear=True)
    new_root = None
    created_joints = []
    for i, (name, pos) in enumerate(zip(orig_names, positions)):
        if i == 0:
            new_root = cmds.joint(name=name, position=pos)
            created_joints.append(new_root)
        else:
            j = cmds.joint(name=name, position=pos)
            created_joints.append(j)

    try:
        cmds.joint(
            created_joints[0],
            e=True,
            orientJoint="xyz",
            secondaryAxisOrient="zup",
            children=True,
            zeroScaleOrient=True,
        )
        last = created_joints[-1]
        for axis in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
            if cmds.objExists(f"{last}.{axis}"):
                try:
                    cmds.setAttr(f"{last}.{axis}", 0)
                except Exception:
                    pass
    except Exception as e:
        cmds.warning(f"⚠️ No se pudo orientar automáticamente la nueva cadena: {e}")

    try:
        cmds.setAttr(f"{clear_grp}.visibility", 0)
    except Exception:
        pass

    try:
        cmds.select(created_joints[0], replace=True)
    except Exception:
        pass

    print(f"\n✅ Cadena limpia creada: {created_joints[0]}")
    print(f"🫧 El rig antiguo y demás se movieron y ocultaron en '{clear_grp}'.")
    return {
        "clear_group": clear_grp,
        "old_names_suffix": suffix,
        "new_chain": created_joints,
    }


if __name__ == "__main__":
    create_clean_chain_from_selection()
