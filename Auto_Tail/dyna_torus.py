import maya.cmds as cmds


def create_dynamic_object():
    """
    Script de rigging dinámico para Maya.
    Crea un sistema completo de control dinámico para un objeto seleccionado.
    """

    # Obtener la selección actual
    selection = cmds.ls(selection=True)

    # Verificar que hay algo seleccionado
    if not selection:
        cmds.error("Por favor, selecciona el toroide primero")

    target_object = selection[0]

    # Eliminar plano anterior si existe
    if cmds.objExists("driverPlane_target_001"):
        cmds.delete("driverPlane_target_001")

    # Crear plano sin subdivisiones
    plane = cmds.polyPlane(
        name="driverPlane_target_001", subdivisionsWidth=1, subdivisionsHeight=1
    )
    plane_name = plane[0]

    print(f"✓ Plano creado: {plane_name}")

    # Hacer match transformation (el plano toma la transformación del objeto seleccionado)
    cmds.matchTransform(plane_name, target_object)
    print(f"✓ Match transformation aplicado: {plane_name} -> {target_object}")

    # Deseleccionar
    cmds.select(clear=True)

    # ===== PARTE 2: BIND SKIN =====
    print("\n--- Iniciando Bind Skin ---")

    # Seleccionar plano y joint_001
    plane_name_full = plane_name if isinstance(plane, str) else plane[0]
    joint = "joint_001"

    if not cmds.objExists(joint):
        cmds.error(f"No se encontró '{joint}' en la escena")

    cmds.select(plane_name_full, joint)
    print(f"✓ Seleccionado: {plane_name_full} y {joint}")

    # Hacer bind skin
    cmds.skinCluster(joint, plane_name_full, toSelectedBones=True)
    print("✓ Bind Skin aplicado")

    # ===== PARTE 3: COPY SKIN WEIGHTS =====
    print("\n--- Copiando Skin Weights ---")

    poly_tail = "PolyTail"

    if not cmds.objExists(poly_tail):
        cmds.error(f"No se encontró '{poly_tail}' en la escena")

    cmds.select(poly_tail, plane_name_full)
    print(f"✓ Seleccionado: {poly_tail} y {plane_name_full}")

    # Copy skin weights
    cmds.copySkinWeights(
        sourceSkin="skinCluster1",
        destinationSkin="skinCluster2",
        noMirror=True,
        influenceAssociation="oneToOne",
    )
    print("✓ Skin Weights copiados")

    # ===== PARTE 4: CREATE LOCATOR =====
    print("\n--- Creando Locator ---")

    # Eliminar locator anterior si existe
    if cmds.objExists("dynamic_target_002"):
        cmds.delete("dynamic_target_002")

    # Crear locator
    locator = cmds.spaceLocator(name="dynamic_target_002")
    locator_name = locator[0]
    print(f"✓ Locator creado: {locator_name}")

    # ===== PARTE 5: POINT ON POLY CONSTRAINT =====
    print("\n--- Aplicando Point On Poly Constraint ---")

    # Seleccionar plano y locator
    cmds.select(plane_name_full, locator_name)
    print(f"✓ Seleccionado: {plane_name_full} y {locator_name}")

    # Aplicar pointOnPolyConstraint con offset apagado
    constraint = cmds.pointOnPolyConstraint(
        plane_name_full, locator_name, offset=(0, 0, 0)
    )
    constraint_name = constraint[0]
    print(f"✓ Point On Poly Constraint aplicado: {constraint_name}")

    # ===== PARTE 6: CONFIGURAR DRIVER PLANE TARGET =====
    print("\n--- Configurando Driver Plane Target ---")

    # Obtener los atributos del constraint y establecerlos a 0.5
    try:
        # Buscar los atributos correctos
        w_attr = f"{constraint_name}.{plane_name_full}W0"
        u_attr = f"{constraint_name}.{plane_name_full}U0"
        v_attr = f"{constraint_name}.{plane_name_full}V0"

        cmds.setAttr(w_attr, 0.5)
        cmds.setAttr(u_attr, 0.5)
        cmds.setAttr(v_attr, 0.5)

        print("✓ Atributos Driver Plane Target establecidos a 0.5")
        print(f"  - {w_attr} = 0.5")
        print(f"  - {u_attr} = 0.5")
        print(f"  - {v_attr} = 0.5")

    except Exception as e:
        print(f"⚠ Error al configurar atributos: {e}")
        print("Verifica que los nombres de los atributos sean correctos")

    # ===== PARTE 7: CREAR CURVA CONTROL =====
    print("\n--- Creando Curva Control ---")

    # Obtener posición del pivote del toroide
    torus_pivot = cmds.xform(
        target_object, query=True, worldSpace=True, rotatePivot=True
    )

    # Crear una curva control simple (círculo)
    curve = cmds.circle(name="dynamic_ctrl_002", normal=(0, 1, 0), radius=1.0)
    curve_name = curve[0]

    # Posicionar la curva en el pivote del toroide + 1.5 unidades arriba en Y
    cmds.xform(
        curve_name,
        worldSpace=True,
        translation=(torus_pivot[0], torus_pivot[1] + 0.2, torus_pivot[2]),
    )

    print(f"✓ Curva control creada: {curve_name}")
    print(f"  Posición: ({torus_pivot[0]}, {torus_pivot[1] + 1.5}, {torus_pivot[2]})")

    # ===== PARTE 8: CREAR ROOT DE LA CURVA =====
    print("\n--- Creando Root de la Curva ---")

    def create_root(obj_name):
        """
        Crea un grupo root para un objeto siguiendo el procedimiento:
        1. Crear grupo vacío
        2. Emparentar grupo a objeto
        3. Resetear transformaciones del objeto
        4. Desagrupar (el grupo hereda las transformaciones)
        5. Emparentar objeto al grupo
        """
        # 1. Crear grupo vacío
        root_name = f"{obj_name}_root"
        root_group = cmds.group(empty=True, name=root_name)

        # 2. Emparentar grupo a objeto
        cmds.parent(root_group, obj_name)

        # 3. Resetear transformaciones del objeto
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
            cmds.setAttr(f"{obj_name}.{attr}", 0 if "s" not in attr else 1)

        # 4. Desagrupar (unparent) - el grupo hereda las transformaciones
        cmds.parent(root_group, world=True)

        # 5. Emparentar objeto al grupo
        cmds.parent(obj_name, root_group)

        return root_group

    root_name = create_root(curve_name)
    print(f"✓ Root creado: {root_name}")

    # ===== PARTE 9: EMPARENTAR ROOT AL LOCATOR =====
    print("\n--- Emparentando Root al Locator ---")

    # Hacer match transformation entre root y locator antes de emparentar
    cmds.matchTransform(root_name, locator_name)
    print(f"✓ Match transformation entre {root_name} y {locator_name}")

    cmds.parent(root_name, locator_name)
    print(f"✓ {root_name} emparentado a {locator_name}")

    # ===== PARTE 10: PARENT CONSTRAIN Y SCALE CONSTRAIN =====
    print("\n--- Aplicando Constraints ---")

    cmds.select(curve_name, target_object)
    print(f"✓ Seleccionado: {curve_name} y {target_object}")

    # Parent Constraint: el toroide sigue a la curva (curve -> torus)
    parent_constraint = cmds.parentConstraint(
        curve_name, target_object, maintainOffset=True
    )
    print("✓ Parent Constraint aplicado (maintain offset: ON)")

    # Scale Constraint: el toroide sigue la escala de la curva (curve -> torus)
    scale_constraint = cmds.scaleConstraint(
        curve_name, target_object, maintainOffset=True
    )
    print("✓ Scale Constraint aplicado (maintain offset: ON)")

    # Deseleccionar
    cmds.select(clear=True)
    print("\n✓ PROCESO COMPLETADO EXITOSAMENTE ✓")


if __name__ == "__main__":
    create_dynamic_object()
