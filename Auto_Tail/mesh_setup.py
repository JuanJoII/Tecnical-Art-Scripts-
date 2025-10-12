import maya.cmds as cmds
import math


def tail_mesh_setup():
    """
    Script para configurar el mesh de la cola dinámico.
    Realiza hasta el posicionamiento del cilindro.
    """

    first_joint = "joint1"
    last_joint = "joint6"

    # PASO 1: Emparentar hairSystem1Follicles a la curva
    print("\n=== PASO 1: Emparentando hairSystem1Follicles ===")

    ctrl_curve = "dynamic_ctrl_001"
    follicles_group = "hairSystem1Follicles"

    if not cmds.objExists(follicles_group):
        cmds.warning(f"El grupo '{follicles_group}' no existe.")
        return False

    cmds.parent(follicles_group, ctrl_curve)
    print(f"'{follicles_group}' emparentado a '{ctrl_curve}'")

    # PASO 2: Crear cilindro
    print("\n=== PASO 2: Creando cilindro ===")

    cylinder = cmds.polyCylinder(
        radius=1,
        height=2,
        subdivisionsAxis=8,
        subdivisionsHeight=1,
        subdivisionsCaps=1,
        axis=(0, 1, 0),
        roundCap=False,
        constructionHistory=True,
        name="pCylinder1",
    )[0]
    print(f"Cilindro creado: {cylinder}")

    # PASO 3: Mover pivote al vértice inferior del cilindro
    print("\n=== PASO 3: Ajustando pivote del cilindro ===")

    # Seleccionar el vértice inferior central (vtx[16])
    cmds.select(f"{cylinder}.vtx[16]", replace=True)
    vertex_pos = cmds.xform(
        f"{cylinder}.vtx[16]", query=True, worldSpace=True, translation=True
    )

    # Mover el pivote a ese vértice
    cmds.xform(cylinder, pivots=vertex_pos, worldSpace=True)
    print("Pivote movido al vértice 16 del cilindro")

    # PASO 4: Mover cilindro al inicio de la curva (primer joint)
    print("\n=== PASO 4: Posicionando cilindro en el primer joint ===")

    first_joint_pos = cmds.xform(
        first_joint, query=True, worldSpace=True, translation=True
    )
    cmds.xform(cylinder, worldSpace=True, translation=first_joint_pos)
    print("Cilindro movido a la posición del primer joint")

    # PASO 5: Rotar ligeramente el cilindro para que coincida con la curva
    print("\n=== PASO 5: Rotando cilindro para coincidir con la curva ===")

    last_joint_pos = cmds.xform(
        last_joint, query=True, worldSpace=True, translation=True
    )

    # Calcular vector de dirección
    dir_x = last_joint_pos[0] - first_joint_pos[0]
    dir_y = last_joint_pos[1] - first_joint_pos[1]
    dir_z = last_joint_pos[2] - first_joint_pos[2]

    # Calcular ángulo en Y
    angle_y = math.degrees(math.atan2(dir_x, dir_z))

    cmds.xform(cylinder, rotation=(0, angle_y, 0), worldSpace=True)
    print(f"Cilindro rotado {angle_y} grados")

    # PASO 6: Seleccionar caras inferiores del cilindro
    print("\n=== PASO 6: Seleccionando caras inferiores ===")

    # Las caras inferiores son f[8:15]
    cmds.select(f"{cylinder}.f[8:15]", replace=True)
    print("Caras inferiores seleccionadas")

    # PASO 7: Agregar la curva a la selección y extruir
    print("\n=== PASO 7: Extrudiendo a lo largo de la curva ===")

    dynamic_curve = "dynamic_cv_002"

    if cmds.objExists(dynamic_curve):
        # Agregar la curva a la selección
        cmds.select(dynamic_curve, add=True)

        try:
            # Extruir siguiendo la curva
            extrude_result = cmds.polyExtrudeFacet(
                constructionHistory=True,
                keepFacesTogether=True,
                divisions=1,
                twist=0,
                taper=1,
                thickness=0,
                inputCurve=dynamic_curve,
            )
            extrude_node = extrude_result[0]
            print(f"Extrusión creada: {extrude_node}")

            # Ajustar divisiones y taper
            cmds.setAttr(f"{extrude_node}.divisions", 15)
            cmds.setAttr(f"{extrude_node}.taper", 0.1)
            print("Divisiones ajustadas a 15, taper ajustado a 0.1")
        except Exception as e:
            cmds.warning(f"Error en la extrusión: {str(e)}")
    else:
        cmds.warning(f"No se encontró la curva '{dynamic_curve}'")

    # PASO 8: Freezear y borrar historial
    print("\n=== PASO 8: Freezeando transformaciones y borrando historial ===")

    cmds.select(cylinder, replace=True)
    cmds.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
    print("Transformaciones freezeadas")

    cmds.delete(cylinder, constructionHistory=True)
    print("Historial borrado")

    # PASO 9: Renombrar cilindro como PolyTail
    print("\n=== PASO 9: Renombrando cilindro ===")

    poly_tail = cmds.rename(cylinder, "PolyTail")
    print(f"Cilindro renombrado a: {poly_tail}")

    print("\n=== PROCESO COMPLETADO ===")
    return True


# Ejecutar el script
if __name__ == "__main__":
    tail_mesh_setup()
