import maya.cmds as cmds
import maya.mel as mel


def create_root_for_curve(curve_name):
    """
    Crea un root para la curva
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


def final_setup():
    """
    Script para los pasos finales del rigging: toroide, plano driver, locator y controles
    """
    
    poly_tail = 'PolyTail'
    
    # PASO 1: Crear toroide
    print("\n=== PASO 1: Creando toroide ===")
    
    torus = cmds.polyTorus(radius=2, name='pTorus1')[0]
    print(f"Toroide creado: {torus}")
    
    # Ubicar el toroide en el medio de polyTail aproximadamente
    poly_tail_pos = cmds.xform(poly_tail, query=True, worldSpace=True, translation=True)
    cmds.xform(torus, worldSpace=True, translation=poly_tail_pos)
    print(f"Toroide ubicado en: {poly_tail_pos}")
    
    # PASO 2: Crear plano y renombrarlo
    print("\n=== PASO 2: Creando plano ===")
    
    plane = cmds.polyPlane(width=1, height=1, subdivisionsWidth=1, subdivisionsHeight=1, name='driverPlane_target_001')[0]
    print(f"Plano creado: {plane}")
    
    # PASO 3: Match transformation entre plano y toroide
    print("\n=== PASO 3: Igualando transformaciones ===")
    
    cmds.select([plane, torus], replace=True)
    mel.eval('matchTransform')
    print("Transformaciones igualadas")
    
    # PASO 4: Ubicar plano en la base del toroide (desde right view)
    print("\n=== PASO 4: Ubicando plano en la base del toroide ===")
    
    # Obtener posición del toroide y ajustar Y hacia abajo
    torus_pos = cmds.xform(torus, query=True, worldSpace=True, translation=True)
    plane_pos = [torus_pos[0], torus_pos[1] - 1, torus_pos[2]]
    cmds.xform(plane, worldSpace=True, translation=plane_pos)
    print(f"Plano ubicado en la base del toroide")
    
    # PASO 5: Bind skin entre plano y joint_001
    print("\n=== PASO 5: Haciendo Bind Skin entre plano y joint_001 ===")
    
    joint_001 = 'joint_001'
    if not cmds.objExists(joint_001):
        cmds.warning(f"'{joint_001}' no existe")
        return False
    
    cmds.select([joint_001, plane], replace=True)
    mel.eval('SmoothBindSkin')
    print(f"Bind skin creado entre {joint_001} y {plane}")
    
    # PASO 6: Copiar skin weights de PolyTail a plano
    print("\n=== PASO 6: Copiando skin weights ===")
    
    if not cmds.objExists(poly_tail):
        cmds.warning(f"'{poly_tail}' no existe")
        return False
    
    cmds.select([poly_tail, plane], replace=True)
    mel.eval('copySkinWeights')
    print("Skin weights copiados")
    
    # PASO 7: Crear locator
    print("\n=== PASO 7: Creando locator ===")
    
    locator = cmds.spaceLocator(name='dynamic_target_002')[0]
    print(f"Locator creado: {locator}")
    
    # PASO 8: Point on Poly constraint
    print("\n=== PASO 8: Aplicando Point on Poly constraint ===")
    
    cmds.select([plane, locator], replace=True)
    mel.eval('pointOnPolyConstraint -offset 0 0 0')
    print("Point on Poly constraint aplicado")
    
    # PASO 9: Setear Driver Plane Target attributes a 0.5
    print("\n=== PASO 9: Seteando Driver Plane Target attributes ===")
    
    try:
        cmds.setAttr(f"{locator}.driverPlaneTargetU", 0.5)
        cmds.setAttr(f"{locator}.driverPlaneTargetV", 0.5)
        cmds.setAttr(f"{locator}.driverPlaneTargetW", 0.5)
        print("Driver Plane Target attributes seteados a 0.5")
    except Exception as e:
        cmds.warning(f"Error al setear attributes: {str(e)}")
    
    # PASO 10: Crear curva de control y emparentarla al locator
    print("\n=== PASO 10: Creando curva de control ===")
    
    ctrl_curve = cmds.curve(
        name='dynamic_ctrl_target_001',
        degree=1,
        point=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0)]
    )
    print(f"Curva de control creada: {ctrl_curve}")
    
    # Emparentar curva al locator
    cmds.parent(ctrl_curve, locator)
    print(f"Curva emparentada al locator")
    
    # PASO 11: Crear root para la curva
    print("\n=== PASO 11: Creando root para la curva ===")
    
    root_group = create_root_for_curve(ctrl_curve)
    if not root_group:
        return False
    
    # PASO 12: Parent constraint y scale constraint entre curva y toroide
    print("\n=== PASO 12: Creando constraints ===")
    
    try:
        # Parent constraint
        cmds.parentConstraint(ctrl_curve, torus, maintainOffset=True)
        print("Parent constraint creado")
        
        # Scale constraint
        cmds.scaleConstraint(ctrl_curve, torus, maintainOffset=True)
        print("Scale constraint creado")
    except Exception as e:
        cmds.warning(f"Error al crear constraints: {str(e)}")
        return False
    
    print("\n=== PROCESO COMPLETADO ===")
    return True


# Ejecutar el script
if __name__ == "__main__":
    final_setup()