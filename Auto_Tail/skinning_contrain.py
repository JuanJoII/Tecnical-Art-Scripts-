import maya.cmds as cmds


def skin_and_constraint_setup():
    """
    Script para hacer bind skin y crear parent constraints entre joints.
    """

    poly_tail = "PolyTail"

    # PASO 1: Bind skin entre joint_001 y PolyTail
    print("\n=== PASO 1: Haciendo Bind Skin ===")

    if not cmds.objExists(poly_tail):
        cmds.warning(f"'{poly_tail}' no existe en la escena.")
        return False

    # Obtener todos los joints de la cadena
    all_joints = cmds.ls(type="joint")
    if not all_joints:
        cmds.warning("No se encontraron joints en la escena.")
        return False

    # Crear bind skin con los joints y PolyTail
    try:
        # Seleccionar joints y PolyTail para bind skin
        cmds.select(all_joints, replace=True)
        cmds.select(poly_tail, add=True)

        # Usar mel para bind skin con configuración default
        import maya.mel as mel

        mel.eval("SmoothBindSkin")
        print(f"Bind skin creado entre joints y {poly_tail}")
    except Exception as e:
        cmds.warning(f"Error en bind skin: {str(e)}")
        return False

    # PASO 2: Crear parent constraints entre joints
    print("\n=== PASO 2: Creando Parent Constraints ===")

    # Obtener joints normales y joints IK
    normal_joints = [j for j in all_joints if "IK" not in j]
    ik_joints = [j for j in all_joints if "IK" in j]

    if not normal_joints or not ik_joints:
        cmds.warning("No se encontraron joints normales o IK suficientes.")
        return False

    # Crear parent constraints entre joints correspondientes
    # joint_001 -> joint_IK_001, joint_002 -> joint_IK_002, etc.
    constraint_count = 0

    for normal_joint in normal_joints:
        # Encontrar el joint IK correspondiente
        # Asumir que los nombres siguen un patrón similar
        ik_joint = None

        for ik_j in ik_joints:
            if (
                normal_joint.replace("_", "_IK_") == ik_j
                or normal_joint.replace("joint", "joint_IK") == ik_j
                or ik_j
                == f"{normal_joint.split('_')[0]}_IK_{normal_joint.split('_')[-1]}"
            ):
                ik_joint = ik_j
                break

        if ik_joint:
            try:
                cmds.parentConstraint(ik_joint, normal_joint, maintainOffset=True)
                print(f"Parent constraint creado: {ik_joint} -> {normal_joint}")
                constraint_count += 1
            except Exception as e:
                cmds.warning(
                    f"Error creando constraint entre {ik_joint} y {normal_joint}: {str(e)}"
                )

    if constraint_count == 0:
        cmds.warning(
            "No se pudieron crear constraints. Verifica los nombres de los joints."
        )
        return False

    print(f"\n{constraint_count} parent constraints creados exitosamente")
    print("\n=== PROCESO COMPLETADO ===")
    return True


# Ejecutar el script
if __name__ == "__main__":
    skin_and_constraint_setup()
