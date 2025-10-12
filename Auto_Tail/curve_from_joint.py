import maya.cmds as cmds


def create_dynamic_curve_from_joint(base_name="dynamic_cv_001", num_spans=8):
    sel = cmds.ls(selection=True, type="joint")
    if not sel:
        cmds.warning("Por favor selecciona el PRIMER joint de la cadena.")
        return None

    root = sel[0]

    # Recorrer hacia abajo siguiendo el primer hijo para formar la cadena (más robusto para chains típicas)
    joint_chain = [root]
    current = root
    while True:
        children = cmds.listRelatives(current, children=True, type="joint") or []
        # filtrar solo joints entre children (ya lo hace type arg), tomar el primero si hay
        if not children:
            break
        # tomar el primer hijo (asume cadena simple). Si hay ramificaciones, se quedará con la rama 'primaria'.
        current = children[0]
        joint_chain.append(current)

    if len(joint_chain) < 2:
        cmds.warning("La cadena debe tener al menos 2 joints.")
        return None

    # Obtener posiciones en world space
    positions = [cmds.xform(j, q=True, ws=True, t=True) for j in joint_chain]

    # Elegir grado inicial: si hay menos de 4 puntos, degree debe ser 1 para evitar errores con degree 3
    initial_degree = 3 if len(positions) >= 4 else 1

    # Crear curva que pase por los joints (interpolada)
    try:
        curve = cmds.curve(d=initial_degree, p=positions, name=base_name)
    except Exception as e:
        cmds.warning("Error creando la curva: {}".format(e))
        return None

    # Reconstruir la curva con el número de spans deseado y grado 3 (suave).
    # rpo=True intenta preservar la forma general; ch=False evita historial innecesario.
    try:
        # solo reconstruir si num_spans es mayor que 0
        if num_spans and num_spans > 0:
            cmds.rebuildCurve(curve, ch=False, rpo=True, s=num_spans, d=3)
    except Exception as e:
        cmds.warning("Error en rebuildCurve: {}".format(e))
        # aun si falla el rebuild, devolver la curva original
        return curve

    cmds.select(curve)
    print("✅ Curva '{}' creada y reconstruida con {} spans.".format(curve, num_spans))
    return curve


if __name__ == "__main__":
    create_dynamic_curve_from_joint()
