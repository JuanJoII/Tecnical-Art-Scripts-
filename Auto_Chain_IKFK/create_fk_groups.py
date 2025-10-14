import maya.cmds as cmds
import re


"""
Auto Chain IK/FK System - FK Groups Setup
=======================================

Este módulo maneja la creación de grupos de control FK para una cadena de joints,
estableciendo la jerarquía necesaria para animación y control.

Pipeline Steps:
    1. Orient Joint Chain
    2. Create FK Groups (este módulo)
    3. Create IK/MAIN Chains
    4. Create IK System
    5. Create Orient Constraints
    6. Create FKIK Attribute

Estructura Jerárquica:
    root_group
    └── auto_group
        └── joint
            └── child_root_group
                └── child_auto_group
                    └── child_joint

Convención de Nombres:
    {segment}_{basename}_{type}_{version}
    Tipos:
        - _root_: Grupo de offset/space switch
        - _auto_: Grupo de automatización
        - _joint_: Joint original
"""


def create_fk_groups():
    """
    PASO 2 PARA AUTO CHAIN IK/FK:
    Crea los grupos ROOT y AUTO para cada joint FK.

    Returns:
        list[tuple]: Lista de grupos creados
            [(root_grp, auto_grp, joint), ...]

    Proceso Técnico:
        1. Identificación de joints FK
           - Busca sufijo '_joint_###'
           - Determina joint raíz
           - Ordena jerarquía

        2. Creación de Grupos
           - ROOT: Control de offset/space
           - AUTO: Automatizaciones/constraints
           - Mantiene nombres originales

        3. Estructura Jerárquica
           - Alinea grupos a joints
           - Establece parentesco
           - Preserva transformaciones

    Requisitos:
        - Joints ya creados y renombrados
        - Sufijo '_joint_###' en cada joint
        - Jerarquía válida (padre→hijo)

    Ejemplo:
        >>> groups = create_fk_groups()
        >>> print(groups[0])  # (root, auto, joint) del primer set
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
        root_grp = (
            cmds.group(em=True, name=root_name)
            if not cmds.objExists(root_name)
            else root_name
        )
        auto_grp = (
            cmds.group(em=True, name=auto_name)
            if not cmds.objExists(auto_name)
            else auto_name
        )

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
    """
    Alinea un grupo vacío a un joint específico.

    Args:
        group (str): Nombre del grupo a alinear
        joint (str): Nombre del joint objetivo

    Returns:
        str: Nombre del grupo alineado

    Proceso:
        1. Parent constraint temporal
        2. Limpieza del constraint
        3. Freeze transformaciones
    """
    tmp = cmds.parentConstraint(joint, group, mo=False)
    cmds.delete(tmp)
    cmds.makeIdentity(group, apply=True, t=True, r=True, s=True)
    return group


# Ejecución directa desde Maya
if __name__ == "__main__":
    create_fk_groups()
