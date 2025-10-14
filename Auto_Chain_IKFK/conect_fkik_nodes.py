"""
Auto Chain IK/FK System - Node Connection
=======================================

Este módulo maneja la conexión del sistema de blend entre FK e IK,
estableciendo las conexiones nodales necesarias para la interpolación.

Pipeline Steps:
    1. Orient Joint Chain
    2. Create FK Groups
    3. Create IK/MAIN Chains
    4. Create IK System
    5. Create Orient Constraints
    6. Create FKIK Attribute
    7. Connect FKIK Nodes (este módulo)

Estructura del Sistema:
    attributes_shape
    └── FKIK attribute (0-1)
        ├── Direct → IK weights
        └── Reverse → FK weights

Node Network:
    FKIK Attribute ────┬───> Orient Constraint (IK weight)
                       └───> Reverse Node ───> Orient Constraint (FK weight)
"""

import maya.cmds as cmds


def connect_fkik_nodes(base_name="Leg_practice_L", version="001"):
    """
    PASO 7 PARA AUTO CHAIN IK/FK:
    Conecta el sistema de blend entre FK e IK mediante nodos.

    Args:
        base_name (str): Nombre base para la nomenclatura (default: "Leg_practice_L")
        version (str): Número de versión del sistema (default: "001")

    Proceso Técnico:
        1. Validación del atributo FKIK
        2. Creación del nodo reverse
        3. Conexión por cada segmento:
           - Detección de constraint
           - Identificación de targets FK/IK
           - Conexión de pesos invertidos

    Sistema de Blend:
        - FKIK = 0: Sistema FK activo (reverse.outputX = 1)
        - FKIK = 1: Sistema IK activo (direct connection)
        - Valores intermedios: Blend proporcional

    Convención de Nombres:
        - Atributo: {base_name}_attributes_{version}Shape
        - Reverse: {base_name}_reverse_{version}
        - Constraints: {segment}_{base_name}_MAIN_{version}_orientConstraint1

    Requisitos:
        - Atributo FKIK ya creado
        - Orient constraints configurados
        - Nomenclatura correcta en joints FK/IK

    Ejemplo:
        >>> connect_fkik_nodes("Leg_practice_L", "001")
        🎚️ Sistema FK/IK conectado correctamente (0=FK, 1=IK)
    """
    attr_shape = f"{base_name}_attributes_{version}Shape"
    if not cmds.objExists(attr_shape):
        cmds.warning(f"⚠️ No existe el shape del atributo: {attr_shape}")
        return

    # Crear nodo reverse si no existe
    reverse_node = f"{base_name}_reverse_{version}"
    if not cmds.objExists(reverse_node):
        reverse_node = cmds.createNode("reverse", name=reverse_node)

    # Conectar FKIK → reverse.inputX
    cmds.connectAttr(f"{attr_shape}.FKIK", f"{reverse_node}.inputX", force=True)

    # Segmentos principales de la pierna
    segments = ["upperLeg", "middleLeg", "endLeg"]

    for seg in segments:
        constraint = f"{seg}_{base_name}_MAIN_{version}_orientConstraint1"
        if not cmds.objExists(constraint):
            cmds.warning(f"⚠️ No se encontró constraint: {constraint}")
            continue

        # Obtener lista de targets del constraint
        targets = cmds.orientConstraint(constraint, query=True, targetList=True)
        if not targets or len(targets) < 2:
            cmds.warning(f"⚠️ {constraint} no tiene suficientes targets.")
            continue

        # Detectar cuál target es FK y cuál IK
        fk_target = next((t for t in targets if "_joint_" in t), None)
        ik_target = next((t for t in targets if "_IK_" in t), None)

        if not fk_target or not ik_target:
            cmds.warning(f"⚠️ No se pudo identificar FK/IK en {constraint}")
            continue

        # Determinar índices para los pesos
        fk_index = targets.index(fk_target)
        ik_index = targets.index(ik_target)

        # Construir nombres de atributos de peso
        w_fk = f"{constraint}.{fk_target}W{fk_index}"
        w_ik = f"{constraint}.{ik_target}W{ik_index}"

        # Conectar:
        # reverse.outputX (1 cuando FKIK=0) → FK
        # FKIK (1 cuando FKIK=1) → IK
        cmds.connectAttr(f"{reverse_node}.outputX", w_fk, force=True)
        cmds.connectAttr(f"{attr_shape}.FKIK", w_ik, force=True)

        print(f"✅ {constraint}: conectado FK ({fk_target}) ↔ IK ({ik_target})")

    print("\n🎚️ Sistema FK/IK conectado correctamente (0=FK, 1=IK).")


if __name__ == "__main__":
    connect_fkik_nodes()
