import maya.cmds as cmds


def create_root_for_curve(curve_name):
    """
    Crea un root para la curva siguiendo estos pasos:
    1. Crea un grupo vacío
    2. Emparenta el grupo a la curva
    3. Setea las transformaciones del grupo a 0
    4. Desemparenta el grupo de la curva (el grupo hereda las transformaciones)
    5. Emparenta la curva al grupo (la curva queda en 0)
    """
    print("\n=== Creando Root para la curva ===")

    if not cmds.objExists(curve_name):
        cmds.warning(f"La curva '{curve_name}' no existe.")
        return None

    # Paso 1: Crear grupo vacío
    root_group = cmds.group(empty=True, name=f"{curve_name}_root")
    print(f"Grupo root creado: {root_group}")

    # Paso 2: Emparentar el grupo a la curva
    cmds.parent(root_group, curve_name)
    print("Grupo emparentado a la curva")

    # Paso 3: Setear transformaciones del grupo a 0
    cmds.xform(root_group, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    print("Transformaciones del grupo seteadas a 0")

    # Paso 4: Desemparentar el grupo de la curva
    cmds.parent(root_group, world=True)
    print("Grupo desemparentado de la curva")

    # Paso 5: Emparentar la curva al grupo
    cmds.parent(curve_name, root_group)
    print("Curva emparentada al grupo root")

    return root_group


def create_ik_joint_chain(first_joint):
    """
    Duplica la cadena de joints original y la renombra con sufijo _IK_
    Retorna el primer y último joint de la cadena IK
    """
    print("\n=== Creando cadena de joints IK ===")

    # Seleccionar el primer joint y duplicar toda la cadena
    cmds.select(first_joint, replace=True)
    duplicated = cmds.duplicate(first_joint, renameChildren=True)[0]

    # Recorrer la cadena duplicada y renombrar todos los joints
    ik_joints_list = []

    def rename_joint_chain(joint, index=[1]):
        new_name = f"joint_IK_{index[0]:03d}"
        renamed = cmds.rename(joint, new_name)
        ik_joints_list.append(renamed)
        print(f"Joint IK creado: {renamed}")

        # Procesar hijos
        children = cmds.listRelatives(renamed, children=True, type="joint") or []
        for child in children:
            index[0] += 1
            rename_joint_chain(child, index)

        return renamed

    ik_root = rename_joint_chain(duplicated)
    ik_last = ik_joints_list[-1]

    print(f"Cadena IK creada con raíz: {ik_root} y último: {ik_last}")

    return ik_root, ik_last


def hair_rigging_setup():
    """
    Script para configurar el rigging de cabello dinámico.
    Realiza: renombrado de curva, IK Spline, gravedad, Point Lock, control curve y snap.
    """

    # PASO 1: Obtener y preparar joints
    print("=== PASO 1: Obteniendo cadena de joints ===")

    all_joints = cmds.ls(type="joint")
    if len(all_joints) < 2:
        cmds.warning("Se necesitan al menos 2 joints para crear el IK Spline.")
        return False

    # Filtrar solo joints originales (sin sufijo IK)
    original_joints = [j for j in all_joints if "_IK_" not in j]
    original_joints.sort()

    first_joint = original_joints[0]
    last_joint = original_joints[-1]

    print(f"Primer joint: {first_joint}")
    print(f"Último joint: {last_joint}")

    # PASO 2: Crear cadena de joints IK
    ik_joints = create_ik_joint_chain(original_joints)
    print("\n=== PASO 3: Renombrando curva de salida ===")

    output_group = "hairSystem1OutputCurves"
    if not cmds.objExists(output_group):
        cmds.warning(f"El grupo '{output_group}' no existe.")
        return False

    # Obtener las curvas dentro del grupo
    curves = cmds.listRelatives(output_group, children=True, type="transform")
    if not curves:
        cmds.warning(f"No hay curvas dentro de '{output_group}'")
        return False

    # Buscar curve1 y renombrar a dynamic_cv_002
    curve1_found = False
    for curve in curves:
        if curve == "curve1":
            cmds.rename(curve, "dynamic_cv_002")
            print("Curva renombrada a: dynamic_cv_002")
            curve1_found = True
            break

    if not curve1_found:
        cmds.warning("No se encontró 'curve1' en el grupo de salida.")
        return False

    # PASO 4: Crear IK Spline Handle sin auto create curve
    print("\n=== PASO 4: Creando IK Spline Handle ===")

    ik_handle = cmds.ikHandle(
        startJoint=ik_joints[0],
        endEffector=ik_joints[1],
        solver="ikSplineSolver",
        curve="dynamic_cv_002",
        createCurve=False,
    )[0]

    print(f"IK Spline Handle creado: {ik_handle}")

    # PASO 5: Setear gravedad a 98 en nucleus
    print("\n=== PASO 5: Configurando Nucleus ===")

    nucleus_nodes = cmds.ls(type="nucleus")
    if not nucleus_nodes:
        cmds.warning("No se encontró nodo nucleus en la escena.")
        return False

    nucleus_node = nucleus_nodes[0]

    # Setear gravedad
    try:
        cmds.setAttr(f"{nucleus_node}.gravity", 98)
        print(f"Gravedad establecida a 98 en {nucleus_node}")
    except Exception as e:
        cmds.warning(f"Error al setear gravedad: {str(e)}")

    # PASO 6: Cambiar Point Lock a "base" en follicleShape1
    print("\n=== PASO 6: Configurando Follicle Point Lock ===")

    if not cmds.objExists("follicleShape1"):
        cmds.warning("No se encontró 'follicleShape1'")
        return False

    try:
        # Point Lock base = 1
        cmds.setAttr("follicleShape1.pointLock", 1)
        print("Point Lock configurado a 'base' en follicleShape1")
    except Exception as e:
        cmds.warning(f"Error al setear Point Lock: {str(e)}")

    # PASO 7: Crear curva de control 'dynamic_ctrl_001'
    print("\n=== PASO 7: Creando curva de control ===")

    # Crear una curva simple de control (CV curve)
    ctrl_curve = cmds.curve(
        name="dynamic_ctrl_001",
        degree=1,
        point=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0)],
    )
    print(f"Curva de control creada: {ctrl_curve}")

    # PASO 8: Llevar la curva al primer joint usando snap (v)
    print("\n=== PASO 8: Snapping control curve al primer joint ===")

    try:
        # Obtener la posición del primer joint
        joint_pos = cmds.xform(
            first_joint, query=True, worldSpace=True, translation=True
        )

        # Mover la curva de control a la posición del joint
        cmds.xform(ctrl_curve, worldSpace=True, translation=joint_pos)

        print(f"Curva de control alineada a la posición del primer joint: {joint_pos}")
    except Exception as e:
        cmds.warning(f"Error al hacer snap: {str(e)}")

    # PASO 9: Crear root para la curva de control
    print("\n=== PASO 9: Creando root para la curva de control ===")

    root_group = create_root_for_curve(ctrl_curve)
    if root_group:
        print(f"Root creado exitosamente: {root_group}")
    else:
        cmds.warning("Error al crear el root para la curva")
        return False

    print("\n=== PROCESO COMPLETADO ===")
    return True


# Ejecutar el script
if __name__ == "__main__":
    hair_rigging_setup()
