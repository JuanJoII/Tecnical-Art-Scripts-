"""
Auto Chain IK/FK System - Control Curves Setup
===========================================

Este módulo maneja la creación y asignación de curvas de control para el sistema IK/FK,
estableciendo la visualización y manipulación de los controles.

Pipeline Steps:
    1. Orient Joint Chain
    2. Create FK Groups
    3. Create IK/MAIN Chains
    4. Create IK System
    5. Create Control Curves (este módulo)
    6. Create FKIK Attribute
    7. Connect FKIK Nodes

Estructura de Controles:
    root_group
    └── control_shape
        └── joint_reference

Convención de Nombres:
    {segment}_{basename}_{type}_{version}
    Ejemplo:
        - upperLeg_Leg_practice_L_root_001
        - upperLeg_Leg_practice_L_ctrl_001
        - upperLeg_Leg_practice_L_joint_001
"""

import maya.cmds as cmds
import re


def auto_assign_curve_shapes():
    """
    PASO 5 PARA AUTO CHAIN IK/FK:
    Crea y asigna curvas de control a los grupos root.

    Proceso Técnico:
        1. Identificación de grupos root
           - Busca sufijo '_root_###'
           - Extrae información de nombre base
           - Obtiene versión del control

        2. Creación de Curvas
           - Genera círculo como shape base
           - Radio: 2 unidades
           - Normal: Y-up orientation
           - Nombrado según convención

        3. Alineación y Cleanup
           - Posiciona en joint correspondiente
           - Aplica rotación del joint
           - Freeze transformaciones
           - Elimina historial

        4. Parenting de Shapes
           - Transfiere shapes al root
           - Elimina transform temporal
           - Mantiene jerarquía limpia

    Requisitos:
        - Grupos root ya creados
        - Joints correspondientes existentes
        - Nomenclatura correcta (_root_###)

    Convención de Control:
        - Shape: Círculo
        - Tamaño: Radio 2
        - Orientación: Y-up
        - Transform: Matched to joint

    Returns:
        None: Opera directamente sobre los objetos en escena

    Ejemplo:
        >>> auto_assign_curve_shapes()
        🔄 Asignando curvas de control a 3 roots
        ✅ Shape de upperLeg_ctrl_001 → upperLeg_root_001
    """
    all_roots = [
        obj for obj in cmds.ls(type="transform") if re.search(r"_root_\d{3}$", obj)
    ]

    if not all_roots:
        cmds.warning("⚠️ No se encontraron roots con sufijo '_root_###'.")
        return

    print("\n" + "=" * 60)
    print(f"🔄 Asignando curvas de control a {len(all_roots)} roots.")
    print("=" * 60)

    for root in all_roots:
        base_name = re.sub(r"_root_\d{3}$", "", root)
        version_match = re.search(r"_(\d{3})$", root)
        if not version_match:
            cmds.warning(f"⚠️ No se pudo obtener versión de {root}")
            continue
        version = version_match.group(1)

        joint_name = f"{base_name}_joint_{version}"

        # Obtener posición y rotación world del joint
        if cmds.objExists(joint_name):
            joint_pos = cmds.xform(
                joint_name, query=True, worldSpace=True, translation=True
            )
            joint_rot = cmds.xform(
                joint_name, query=True, worldSpace=True, rotation=True
            )
        else:
            cmds.warning(f"⚠️ No existe el joint correspondiente: {joint_name}")
            continue

        ctrl_name = f"{base_name}_ctrl_{version}"

        # Crear curva si no existe
        if not cmds.objExists(ctrl_name):
            ctrl_name = cmds.circle(name=ctrl_name, normal=(0, 1, 0), radius=2)[0]
            print(f"➕ Creada curva: {ctrl_name}")

        # Mover la curva a la posición y rotación del joint
        cmds.xform(ctrl_name, worldSpace=True, translation=joint_pos)
        cmds.xform(ctrl_name, worldSpace=True, rotation=joint_rot)
        print(f"  📍 Posicionada en: {joint_pos}")

        # Congelar transformaciones y eliminar historial antes de parentar
        cmds.makeIdentity(
            ctrl_name, apply=True, translate=True, rotate=True, scale=True
        )
        cmds.delete(ctrl_name, constructionHistory=True)

        # Obtener shapes de la curva
        shapes = cmds.listRelatives(ctrl_name, shapes=True, fullPath=True)
        if not shapes:
            cmds.warning(f"⚠️ {ctrl_name} no tiene shapes.")
            continue

        # Parentar los shapes al root
        for sh in shapes:
            cmds.parent(sh, root, add=True, shape=True)

        # Eliminar el transform vacío del control
        cmds.delete(ctrl_name)

        print(f"✅ Shape de {ctrl_name} → {root}")

    print("\n" + "=" * 60)
    print("🎉 Curvas asignadas correctamente.")
    print("=" * 60)


# Ejecutar en Maya directamente
if __name__ == "__main__":
    auto_assign_curve_shapes()
