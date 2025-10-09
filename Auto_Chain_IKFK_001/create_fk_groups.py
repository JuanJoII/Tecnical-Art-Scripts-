import maya.cmds as cmds
import re

def create_fk_groups():
    """
    Crea los grupos ROOT y AUTO para cada joint que tenga sufijo '_joint_###'.
    Inserta '_root_' y '_auto_' justo antes del número de versión.
    Estructura final (de arriba hacia abajo):
        upper_root → upper_auto → upper_joint → middle_root → ...
    """
    # Buscar todos los joints válidos en escena
    all_joints = [j for j in cmds.ls(type="joint") if re.search(r"_joint_\d{3}$", j)]
    if not all_joints:
        cmds.warning("⚠️ No se encontraron joints con sufijo '_joint_###'.")
        return []

    # Detectar el joint raíz (sin padre)
    root_joint = None
    for j in all_joints:
        if not cmds.listRelatives(j, parent=True, type="joint"):
            root_joint = j
            break

    if not root_joint:
        cmds.warning("⚠️ No se pudo determinar el joint raíz.")
        return []

    # Obtener jerarquía completa en orden descendente (root → end)
    fk_joints = cmds.listRelatives(root_joint, ad=True, type="joint") or []
    fk_joints.append(root_joint)
    fk_joints.reverse()  # Invertimos porque ad=True devuelve de hijo → padre

    print("\n" + "=" * 60)
    print(f"🎯 Creando grupos ROOT/AUTO para cadena FK con {len(fk_joints)} joints.")
    print("=" * 60)

    created_groups = []
    prev_auto = None

    for jnt in fk_joints:
        root_name = re.sub(r"_joint_", "_root_", jnt)
        auto_name = re.sub(r"_joint_", "_auto_", jnt)

        # Crear grupos vacíos si no existen
        root_grp = cmds.group(em=True, name=root_name) if not cmds.objExists(root_name) else root_name
        auto_grp = cmds.group(em=True, name=auto_name) if not cmds.objExists(auto_name) else auto_name

        # Alinear al joint
        align_group_to_joint(root_grp, jnt)
        align_group_to_joint(auto_grp, jnt)

        # Parentar jerárquicamente
        cmds.parent(auto_grp, root_grp)
        try:
            cmds.parent(jnt, auto_grp)
        except RuntimeError:
            pass  # Ya está parentado correctamente

        # Parentar el siguiente root bajo el auto anterior
        if prev_auto and cmds.objExists(prev_auto):
            cmds.parent(root_grp, prev_auto)

        prev_auto = auto_grp
        created_groups.append((root_grp, auto_grp, jnt))
        print(f"✅ {root_grp} > {auto_grp} > {jnt}")

    print("\n📦 Estructura ROOT/AUTO/JNT generada correctamente en orden jerárquico.\n")
    print("=" * 60)
    return created_groups


def align_group_to_joint(group, joint):
    """Alinea un grupo vacío a la posición y orientación de un joint."""
    tmp = cmds.parentConstraint(joint, group, mo=False)
    cmds.delete(tmp)
    cmds.makeIdentity(group, apply=True, t=True, r=True, s=True)
    return group


# Ejecución directa desde Maya
if __name__ == "__main__":
    create_fk_groups()
