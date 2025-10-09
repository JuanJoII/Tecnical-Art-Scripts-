import maya.cmds as cmds
import re


import maya.cmds as cmds

def orient_joint_chain(root_joint):
    """
    Orienta correctamente toda la jerarquía de joints desde el root hacia abajo.
    Coincide con las opciones del Orient Joint Tool:
      - Primary Axis: X
      - Secondary Axis: Y
      - Secondary Axis World Orientation: Z+
      - Orient children: True
      - Reorient local scale axes: True
    Limpia el jointOrient del último joint.
    """
    if not cmds.objExists(root_joint):
        cmds.warning(f"⚠️ No existe el joint raíz {root_joint}")
        return

    print(f"\n🧭 Orientando jerarquía completa desde: {root_joint}")

    cmds.select(clear=True)
    try:
        cmds.joint(
            root_joint,
            e=True,
            orientJoint="xyz",          # Primary X, Secondary Y
            secondaryAxisOrient="zup",  # World orientation Z+
            children=True,              # Orientar hijos
            zeroScaleOrient=True        # Reorientar local scale axes
        )
    except Exception as e:
        cmds.warning(f"⚠️ Error aplicando joint orientation en {root_joint}: {e}")
        return

    # Resetear jointOrient del último joint
    end_joint = get_last_joint(root_joint)
    if end_joint:
        for axis in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
            try:
                cmds.setAttr(f"{end_joint}.{axis}", 0)
            except Exception:
                pass
        print(f"🔹 Último joint limpio (sin jointOrient): {end_joint}")

    print("✅ Orientación aplicada correctamente (X primary, Y secondary, Z+ world).")


def get_last_joint(root_joint):
    """Devuelve el último joint en una cadena."""
    current = root_joint
    while True:
        children = cmds.listRelatives(current, type="joint", children=True) or []
        if not children:
            return current
        current = children[0]



def rename_hierarchy(
    chain_type: str = "joint",
    increment_version: bool = True,
    base_name: str = "Leg_practice_L",
):
    """
    Renombra la jerarquía seleccionada y orienta la cadena renombrada.
    Retorna la lista de nombres renombrados (en orden root→end).
    Además selecciona el nuevo root para facilitar pasos siguientes.
    """
    selection = cmds.ls(selection=True, type="joint")
    if not selection:
        cmds.warning("⚠️ Selecciona el joint raíz de la cadena a renombrar.")
        return []

    original_root = selection[0]
    version_pattern = re.compile(r"(\d+)$")

    # Recorrido jerárquico (root → hijos)
    def walk_chain(node):
        yield node
        children = cmds.listRelatives(node, type="joint", children=True) or []
        for child in children:
            yield from walk_chain(child)

    joints = list(walk_chain(original_root))
    if not joints:
        cmds.warning(f"⚠️ No se encontraron joints hijos de {original_root}")
        return []

    renamed = []
    for i, obj in enumerate(joints, 1):
        if i == 1:
            segment = "upperLeg"
        elif i == 2:
            segment = "middleLeg"
        else:
            segment = "endLeg"

        if increment_version:
            match = version_pattern.search(obj)
            # Si el nombre original tiene un número, incrementarlo; si no, usar i
            current_version = int(match.group(1)) + 1 if match else i
        else:
            current_version = 1

        new_name = f"{segment}_{base_name}_{chain_type}_{current_version:03d}"
        try:
            renamed_joint = cmds.rename(obj, new_name)
        except Exception as e:
            cmds.warning(f"⚠️ Error renombrando {obj} → {new_name}: {e}")
            renamed_joint = obj  # fallback al nombre original
        renamed.append(renamed_joint)
        print(f"✅ {obj} → {renamed_joint}")

    # Nuevo root después del renombrado
    new_root = renamed[0]
    # Seleccionar el nuevo root para que las siguientes funciones trabajen sobre él
    try:
        cmds.select(new_root, replace=True)
    except Exception:
        pass

    # Orientar toda la cadena usando el nuevo nombre (no el antiguo)
    orient_joint_chain(new_root)

    return renamed


def create_ik_main_chains(base_name: str = "Leg_practice_L", chain_type: str = "joint"):
    """
    Duplica la cadena renombrada (de la selección actual) y crea versiones IK y MAIN.
    Cada duplicado se renombra y se orienta automáticamente.
    Retorna un diccionario con referencias a las cadenas creadas.
    """
    selection = cmds.ls(selection=True, type="joint")
    if not selection:
        cmds.warning("⚠️ Selecciona el joint raíz de la cadena (debe ser el renombrado).")
        return None

    root = selection[0]  # este debe ser el nuevo nombre devuelto por rename_hierarchy
    version_pattern = re.compile(r"(\d+)$")

    print("\n--- Creando cadenas IK y MAIN ---")

    def walk_chain(node):
        yield node
        children = cmds.listRelatives(node, type="joint", children=True) or []
        for child in children:
            yield from walk_chain(child)

    joints = list(walk_chain(root))
    if not joints:
        cmds.warning(f"⚠️ No se encontraron joints bajo {root}")
        return None

    first_joint_name = joints[0].split("|")[-1]
    version_match = version_pattern.search(first_joint_name)
    original_version = version_match.group(1) if version_match else "001"

    result = {}

    # Crear cadena IK
    print("📋 Creando cadena IK...")
    try:
        ik_duplicate = cmds.duplicate(root, renameChildren=True)[0]
    except Exception as e:
        cmds.warning(f"⚠️ Error duplicando para IK: {e}")
        return None

    ik_renamed = rename_duplicate_chain(ik_duplicate, base_name, "IK", original_version)
    # orientamos la cadena IK usando su nuevo root (primer elemento)
    if ik_renamed:
        orient_joint_chain(ik_renamed[0])
        print("✅ Cadena IK creada y orientada correctamente")
        result["ik"] = ik_renamed
    else:
        cmds.warning("⚠️ Renombrado de IK falló.")

    # Crear cadena MAIN
    print("📋 Creando cadena MAIN...")
    try:
        main_duplicate = cmds.duplicate(root, renameChildren=True)[0]
    except Exception as e:
        cmds.warning(f"⚠️ Error duplicando para MAIN: {e}")
        return result

    main_renamed = rename_duplicate_chain(main_duplicate, base_name, "MAIN", original_version)
    if main_renamed:
        orient_joint_chain(main_renamed[0])
        print("✅ Cadena MAIN creada y orientada correctamente")
        result["main"] = main_renamed
    else:
        cmds.warning("⚠️ Renombrado de MAIN falló.")

    return result


def rename_duplicate_chain(root_node, base_name, suffix, version):
    """
    Renombra todos los joints de una cadena duplicada con el sufijo y versión coherente.
    Retorna la lista de nombres renombrados (root→end).
    """
    def walk_chain(node):
        yield node
        children = cmds.listRelatives(node, type="joint", children=True) or []
        for child in children:
            yield from walk_chain(child)

    joints = list(walk_chain(root_node))
    if not joints:
        return []

    renamed = []
    for i, joint in enumerate(joints, 1):
        current_name = joint.split("|")[-1]

        if i == 1:
            segment = "upperLeg"
        elif i == 2:
            segment = "middleLeg"
        else:
            segment = "endLeg"

        new_name = f"{segment}_{base_name}_{suffix}_{version}"
        try:
            renamed_joint = cmds.rename(joint, new_name)
        except Exception as e:
            cmds.warning(f"⚠️ Error renombrando {joint} → {new_name}: {e}")
            renamed_joint = joint  # fallback
        renamed.append(renamed_joint)
        print(f"  {current_name} → {renamed_joint}")

    return renamed


def open_rename_parameters():
    if cmds.window("renameWin", exists=True):
        cmds.deleteUI("renameWin")

    win = cmds.window("renameWin", title="Rename Chain Tool", widthHeight=(350, 250))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    base_name_field = cmds.textFieldGrp(label="Base Name:", text="Leg_practice_L")
    chain_type_field = cmds.textFieldGrp(label="Chain Type:", text="joint")
    increment_cb = cmds.checkBoxGrp(label="Increment: ", value1=False)

    def apply_rename(*args):
        base_name = cmds.textFieldGrp(base_name_field, q=True, text=True)
        chain_type = cmds.textFieldGrp(chain_type_field, q=True, text=True)
        increment_version = cmds.checkBoxGrp(increment_cb, q=True, value1=True)
        renamed = rename_hierarchy(chain_type, increment_version, base_name)
        if renamed:
            # seleccionar el nuevo root para facilitar el siguiente paso
            try:
                cmds.select(renamed[0], replace=True)
            except Exception:
                pass

    def create_ik_main(*args):
        base_name = cmds.textFieldGrp(base_name_field, q=True, text=True)
        chain_type = cmds.textFieldGrp(chain_type_field, q=True, text=True)
        create_ik_main_chains(base_name, chain_type)

    cmds.button(label="Rename Selection", bgc=(0.3, 0.6, 0.3), command=apply_rename)
    cmds.separator()
    cmds.button(label="Create IK and MAIN Chains", bgc=(0.6, 0.4, 0.2), command=create_ik_main)

    cmds.showWindow(win)


# Permite ejecutar directo desde Script Editor
if __name__ == "__main__":
    open_rename_parameters()
