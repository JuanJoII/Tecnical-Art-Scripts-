# dyna_torus_fixed.py
import maya.cmds as cmds
import maya.mel as mel

def create_root_for_curve(curve_name):
    """
    Crea <curve_name>_root si no existe y parenta la curva dentro,
    preservando transformaciones world. Si ya existe, lo reutiliza.
    """
    if not cmds.objExists(curve_name):
        cmds.warning(f"[create_root_for_curve] La curva '{curve_name}' no existe.")
        return None

    root_name = f"{curve_name}_root"
    if cmds.objExists(root_name):
        # Ya existe el root, asegúrate de que la curva esté bajo él
        parents = cmds.listRelatives(curve_name, parent=True, fullPath=True) or []
        if parents and root_name in parents[0]:
            return root_name
        try:
            cmds.parent(curve_name, root_name)
        except Exception:
            # si no se puede parentar (quizá ya está en world), ignorar
            pass
        return root_name

    # Crear grupo y ubicarlo en la transform world actual de la curva
    # Obtener world transform de la curva
    ws_pos = cmds.xform(curve_name, query=True, worldSpace=True, translation=True)
    ws_rot = cmds.xform(curve_name, query=True, worldSpace=True, rotation=True)

    root = cmds.group(empty=True, name=root_name)
    # setear transforms del root a la transform de la curva
    cmds.xform(root, worldSpace=True, translation=ws_pos)
    cmds.xform(root, worldSpace=True, rotation=ws_rot)
    # parentar la curva bajo el root preservando transform
    cmds.parent(curve_name, root)
    return root

def get_skinCluster_on(obj):
    """
    Retorna el nombre del skinCluster conectado al objeto (si existe), o None.
    """
    if not cmds.objExists(obj):
        return None
    hist = cmds.listHistory(obj) or []
    skins = [n for n in hist if cmds.nodeType(n) == 'skinCluster']
    return skins[0] if skins else None

def get_mid_vertex_position_of_mesh(transform_name):
    if not cmds.objExists(transform_name):
        return None
    shapes = cmds.listRelatives(transform_name, shapes=True, fullPath=True) or []
    mesh_shape = None
    for s in shapes:
        if cmds.nodeType(s) == 'mesh':
            mesh_shape = s
            break
    if mesh_shape:
        verts = cmds.ls(f"{mesh_shape}.vtx[*]", fl=True) or []
        if verts:
            mid_idx = len(verts) // 2
            try:
                pos = cmds.pointPosition(verts[mid_idx], world=True)
                return pos
            except Exception:
                pass
    # fallback bbox center
    try:
        bbox = cmds.exactWorldBoundingBox(transform_name)
        center = [(bbox[0]+bbox[3])/2.0, (bbox[1]+bbox[4])/2.0, (bbox[2]+bbox[5])/2.0]
        return center
    except Exception:
        return [0,0,0]

def final_setup():
    poly_tail = 'PolyTail'
    joint_001 = 'joint_001'
    torus_name = 'pTorus1'
    plane_name = 'driverPlane_target_001'
    locator_name = 'dynamic_target_002'
    ctrl_curve_name = 'dynamic_ctrl_001'

    # === 1: Crear toroide y ubicarlo ===
    print("== PASO 1: Crear toroide ==")
    if not cmds.objExists(torus_name):
        torus = cmds.polyTorus(radius=1.0, name=torus_name)[0]
    else:
        torus = torus_name
    pos = get_mid_vertex_position_of_mesh(poly_tail)
    if pos:
        cmds.xform(torus, worldSpace=True, translation=pos)
        print(f"Toroide ubicado en posición de PolyTail: {pos}")
    else:
        if cmds.objExists(poly_tail):
            bbox = cmds.exactWorldBoundingBox(poly_tail)
            center = [(bbox[0]+bbox[3])/2.0, (bbox[1]+bbox[4])/2.0, (bbox[2]+bbox[5])/2.0]
            cmds.xform(torus, worldSpace=True, translation=center)
            print(f"Toroide ubicado en bbox center de PolyTail: {center}")
        else:
            cmds.xform(torus, worldSpace=True, translation=(0,0,0))
            print("PolyTail no existe — toroide en 0,0,0")

    # === 2: Crear plano driver ===
    print("== PASO 2: Crear plano driver ==")
    if not cmds.objExists(plane_name):
        plane = cmds.polyPlane(width=1, height=1, subdivisionsWidth=1, subdivisionsHeight=1, name=plane_name)[0]
    else:
        plane = plane_name

    # === 3: Match Transform ===
    print("== PASO 3: Match Transform entre plano y toroide ==")
    try:
        cmds.select([plane, torus], replace=True)
        mel.eval('matchTransform')
    except Exception as e:
        cmds.warning(f"matchTransform no ejecutado: {e}")

    # === 4: Ubicar plano en base del toroide ===
    print("== PASO 4: Ubicar plano en la base del toroide ==")
    try:
        bbox = cmds.exactWorldBoundingBox(torus)
        baseY = bbox[1]
        torus_pos = cmds.xform(torus, query=True, worldSpace=True, translation=True)
        plane_pos = [torus_pos[0], baseY - 0.0, torus_pos[2]]
        cmds.xform(plane, worldSpace=True, translation=plane_pos)
    except Exception as e:
        cmds.warning(f"No se pudo posicionar el plano: {e}")

    # === 5: Bind skin (plane <-> joint_001) ===
    print("== PASO 5: Bind skin (plane <-> joint_001) ==")
    if not cmds.objExists(joint_001):
        cmds.warning(f"El joint '{joint_001}' no existe. Saltando bind skin.")
    else:
        try:
            sc = cmds.skinCluster(joint_001, plane, toSelectedBones=True, bindMethod=0, name=f"{plane}_skinCluster")[0]
            print(f"skinCluster creado: {sc}")
        except Exception as e:
            cmds.warning(f"Error creando skinCluster: {e}")
            sc = None

    # === 6: Copy skin weights from PolyTail to plane ===
    print("== PASO 6: Copiar skin weights desde PolyTail al plano ==")
    if not cmds.objExists(poly_tail):
        cmds.warning(f"'{poly_tail}' no existe. Saltando copySkinWeights.")
    else:
        # buscar skinClusters fuente y destino
        sc_source = get_skinCluster_on(poly_tail)
        sc_dest = get_skinCluster_on(plane)
        if not sc_source:
            cmds.warning(f"No se encontró skinCluster en '{poly_tail}'. No se puede copiar pesos. (salteando)")
        elif not sc_dest:
            cmds.warning(f"No se encontró skinCluster en '{plane}'. No se puede copiar pesos.")
        else:
            try:
                # Ejecutar MEL copySkinWeights indicando explícitamente skinClusters
                mel_cmd = 'copySkinWeights -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint {src} {dst};'.format(src=sc_source, dst=sc_dest)
                mel.eval(mel_cmd)
                print("copySkinWeights ejecutado entre skinClusters.")
            except Exception as e:
                cmds.warning(f"Error en copySkinWeights: {e}")

    # === 7: Crear locator ===
    print("== PASO 7: Crear locator ==")
    if not cmds.objExists(locator_name):
        locator = cmds.spaceLocator(name=locator_name)[0]
    else:
        locator = locator_name

    # === 8: Point on Poly constraint sin offset ===
    print("== PASO 8: Aplicar pointOnPolyConstraint (offset apagado) ==")
    try:
        # El punto es: poly -> locator, maintainOffset False
        if hasattr(cmds, 'pointOnPolyConstraint'):
            cmds.pointOnPolyConstraint(plane, locator, maintainOffset=False)
        else:
            cmds.select([plane, locator], replace=True)
            mel.eval('pointOnPolyConstraint -offset 0 0 0;')
    except Exception as e:
        cmds.warning(f"No se pudo aplicar pointOnPolyConstraint: {e}")

    # === 9: Atributos Driver Plane Target ===
    print("== PASO 9: Crear atributos Driver Plane Target en locator ==")
    attrs = ['driverPlaneTargetU', 'driverPlaneTargetV', 'driverPlaneTargetW']
    for a in attrs:
        full_attr = f"{locator}.{a}"
        if not cmds.objExists(full_attr):
            try:
                cmds.addAttr(locator, longName=a, attributeType='double', min=0.0, max=1.0, defaultValue=0.5)
                cmds.setAttr(full_attr, e=True, keyable=True)
            except Exception as e:
                cmds.warning(f"No se pudo crear atributo {a}: {e}")
        try:
            cmds.setAttr(full_attr, 0.5)
        except Exception:
            pass

    # === 10: Crear curva control y emparentar al locator ===
    print("== PASO 10: Curva control y emparentar al locator ==")
    if not cmds.objExists(ctrl_curve_name):
        ctrl_curve = cmds.curve(name=ctrl_curve_name, degree=1, point=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,0)])
    else:
        ctrl_curve = ctrl_curve_name
    try:
        # asegurarse de que el parent preserve world transform
        # si la curva ya tiene otro padre, la reparentamos al locator
        cmds.parent(ctrl_curve, locator)
    except Exception as e:
        cmds.warning(f"No se pudo emparentar la curva al locator: {e}")

    # === 11: Crear root para la curva con la función robusta ===
    print("== PASO 11: Crear root para la curva ==")
    root = create_root_for_curve(ctrl_curve)
    if not root:
        cmds.warning("No se pudo crear root para la curva.")

    # === 12: parentConstraint y scaleConstraint entre control y toroide ===
    print("== PASO 12: Crear constraints finales ==")
    try:
        if cmds.objExists(ctrl_curve) and cmds.objExists(torus):
            cmds.parentConstraint(ctrl_curve, torus, maintainOffset=True, name=f"{torus}_parentConstraint")
            cmds.scaleConstraint(ctrl_curve, torus, maintainOffset=True, name=f"{torus}_scaleConstraint")
    except Exception as e:
        cmds.warning(f"Error creando constraints: {e}")

    print("=== PROCESO FINALIZADO ===")
    return True

if __name__ == "__main__":
    final_setup()
