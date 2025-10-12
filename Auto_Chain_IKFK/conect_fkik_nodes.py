import maya.cmds as cmds


def connect_fkik_nodes(base_name="Leg_practice_L", version="001"):
    """
    Conecta el atributo FKIK del locator con los orientConstraints de la cadena MAIN.
    FKIK = 0 → controla la cadena FK
    FKIK = 1 → controla la cadena IK
    Crea automáticamente el nodo 'reverse' para invertir los pesos.
    """
    attr_shape = f"{base_name}_attributes_{version}Shape"
    if not cmds.objExists(attr_shape):
        cmds.warning(f"⚠️ No existe el shape del atributo: {attr_shape}")
        return

    reverse_node = f"{base_name}_reverse_{version}"
    if not cmds.objExists(reverse_node):
        reverse_node = cmds.createNode("reverse", name=reverse_node)

    # Conectar FKIK → reverse.inputX
    cmds.connectAttr(f"{attr_shape}.FKIK", f"{reverse_node}.inputX", force=True)

    # Procesar todos los segmentos principales
    segments = ["upperLeg", "middleLeg", "endLeg"]
    for seg in segments:
        constraint = f"{seg}_{base_name}_MAIN_{version}_orientConstraint1"
        if not cmds.objExists(constraint):
            cmds.warning(f"⚠️ No se encontró constraint: {constraint}")
            continue

        # Obtener pesos del constraint (por orden de creación)
        weights = cmds.listAttr(constraint, string="*W*", multi=True) or []
        if len(weights) < 2:
            cmds.warning(f"⚠️ No se detectaron pesos válidos en {constraint}")
            continue

        w_fk = f"{constraint}.{weights[0]}"  # FK target
        w_ik = f"{constraint}.{weights[1]}"  # IK target

        # 🔁 Conexión corregida:
        # FKIK = 0 → FK activo → reverse.outputX (1 cuando FKIK=0)
        # FKIK = 1 → IK activo → FKIK directo (1 cuando FKIK=1)
        cmds.connectAttr(f"{reverse_node}.outputX", w_fk, force=True)
        cmds.connectAttr(f"{attr_shape}.FKIK", w_ik, force=True)

        print(f"✅ Conectado reverse.outputX → {w_fk}, FKIK → {w_ik}")

    print("\n🎚️ Sistema FK/IK conectado correctamente (0=FK, 1=IK).")


if __name__ == "__main__":
    connect_fkik_nodes()
