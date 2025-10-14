"""
Auto Chain IK/FK System - IK Setup
================================

Este módulo maneja la creación del sistema IK (Inverse Kinematics) para una cadena de 3 joints,
incluyendo la configuración del IK handle, pole vector y controles.

Pipeline Steps:
    1. Orient Joint Chain
    2. Rename Hierarchy
    3. Create IK System (este módulo)
    4. Create Orient Constraints

Estructura del Sistema IK:
    - IK Handle (RPsolver)
    - Pole Vector Control
    - Effector
    - Grupos de organización

Convención de Nombres:
    {segment}_{basename}_IK_{version}
    Ejemplo:
        - upperLeg_Leg_practice_L_IK_001
        - middleLeg_Leg_practice_L_IKpoleVector_001
        - middleLeg_Leg_practice_L_IKhandle_001
"""

import maya.cmds as cmds


def create_ik_system(base_name="Leg_practice_L", version="001"):
    """
    PASO 3 PARA AUTO CHAIN IK/FK:
    Construye un sistema IK completo para una cadena de 3 joints.

    Args:
        base_name (str): Nombre base para la nomenclatura (default: "Leg_practice_L")
        version (str): Número de versión para el sistema (default: "001")

    Returns:
        dict: Referencias a los elementos creados
            {
                "ik_handle": str,      # IK handle principal
                "effector": str,       # Effector del IK
                "pole_vector_grp": str, # Grupo del pole vector
                "pole_vector_root": str # Grupo raíz del sistema
            }

    Proceso Técnico:
        1. Validación de joints IK existentes
        2. Creación del grupo Pole Vector
           - Posicionamiento en joint medio
           - Offset de 5 unidades en Y+
        3. Setup del IK Handle
           - RPsolver para rotación natural
           - Conexión start/end joints
        4. Configuración Pole Vector
           - Constraint al IK handle
           - Grupo root para organización
        5. Control visual del Pole Vector
           - Curva circular como shape
           - Radio: 1.5 unidades
           - Normal: X axis

    Requisitos:
        - Cadena IK ya creada y renombrada
        - 3 joints en la siguiente estructura:
          * upperLeg_{base_name}_IK_{version}
          * middleLeg_{base_name}_IK_{version}
          * endLeg_{base_name}_IK_{version}

    Ejemplo:
        >>> result = create_ik_system("Leg_practice_L", "001")
        >>> print(result["ik_handle"])
        "middleLeg_Leg_practice_L_IKhandle_001"
    """
    # --- Definir nombres base ---
    upper_joint = f"upperLeg_{base_name}_IK_{version}"
    middle_joint = f"middleLeg_{base_name}_IK_{version}"
    end_joint = f"endLeg_{base_name}_IK_{version}"

    # Validar que la cadena IK exista
    for jnt in [upper_joint, middle_joint, end_joint]:
        if not cmds.objExists(jnt):
            cmds.warning(f"⚠️ El joint {jnt} no existe.")
            return

    # --- 1. Crear el grupo del Pole Vector ---
    pv_grp = f"middleLeg_{base_name}_IKpoleVector_{version}"
    pv_root = f"middleLeg_{base_name}_IKpoleVectorRoot_{version}"
    pv_ctrl_curve = f"middleLeg_{base_name}_IKpoleVectorCtrl_{version}"

    if not cmds.objExists(pv_grp):
        pv_grp = cmds.group(em=True, name=pv_grp)
        # Snap al joint medio
        cmds.delete(cmds.pointConstraint(middle_joint, pv_grp))
        # Moverlo 5 unidades en Y+
        cmds.move(0, 5, 0, pv_grp, relative=True, os=True)
        print(f"✅ Grupo Pole Vector creado: {pv_grp}")

    # --- 2. Crear el IK Handle ---
    ik_handle, effector = cmds.ikHandle(sj=upper_joint, ee=end_joint, sol="ikRPsolver")
    ik_handle = cmds.rename(ik_handle, f"middleLeg_{base_name}_IKhandle_{version}")
    effector = cmds.rename(effector, f"middleLeg_{base_name}_effector_{version}")
    print(f"✅ IK Handle creado: {ik_handle}")
    print(f"✅ Effector creado: {effector}")

    # --- 3. Crear Pole Vector Constraint ---
    if not cmds.objExists(pv_grp):
        cmds.warning(f"⚠️ El grupo {pv_grp} no existe.")
        return
    cmds.poleVectorConstraint(pv_grp, ik_handle)
    print(f"✅ Pole Vector Constraint aplicado entre {pv_grp} y {ik_handle}")

    # --- 4. Crear el grupo Root para el Pole Vector ---
    if not cmds.objExists(pv_root):
        pv_root = cmds.group(pv_grp, name=pv_root)
        print(f"✅ Grupo Root creado: {pv_root}")

    # --- 5. Crear curva de control para el Pole Vector ---
    if not cmds.objExists(pv_ctrl_curve):
        curve = cmds.circle(name=pv_ctrl_curve, normal=(1, 0, 0), radius=1.5)[0]
        # Snap a la posición del pole vector
        cmds.delete(cmds.pointConstraint(pv_grp, curve))
        # Combinar shape con el grupo pole vector
        shapes = cmds.listRelatives(curve, shapes=True, fullPath=True)
        for shape in shapes:
            cmds.parent(shape, pv_grp, r=True, s=True)
        cmds.delete(curve)
        print(f"✅ Curva de control combinada en {pv_grp}")

    print("🎯 Cadena IK creada correctamente según la documentación.")
    return {
        "ik_handle": ik_handle,
        "effector": effector,
        "pole_vector_grp": pv_grp,
        "pole_vector_root": pv_root,
    }


# Uso:
# create_leg_ik_system()
if __name__ == "__main__":
    create_ik_system()
