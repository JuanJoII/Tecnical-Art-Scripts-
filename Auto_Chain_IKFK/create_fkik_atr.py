"""
Auto Chain IK/FK System - Attribute Creation
==========================================

Este módulo maneja la creación del atributo de blend IK/FK para el sistema,
combinando un locator con el joint raíz para controlar la interpolación entre sistemas.

Pipeline Steps:
    1. Orient Joint Chain
    2. Rename Hierarchy
    3. Create IK/MAIN Chains
    4. Create IK System
    5. Create Orient Constraints
    6. Create FKIK Attribute (este módulo)

Estructura:
    - Locator (temporal)
    - Shape con atributo FKIK
    - Conexión al joint raíz

Convención de Nombres:
    {basename}_attributes_{version}
    Ejemplo:
        - Leg_practice_L_attributes_001
        - Leg_practice_L_attributesShape_001
"""

import maya.cmds as cmds


def create_fkik_attribute(base_name="Leg_practice_L", version="001"):
    """
    PASO 6 PARA AUTO CHAIN IK/FK:
    Crea y configura el atributo de blend entre sistemas FK e IK.

    Args:
        base_name (str): Nombre base para la nomenclatura (default: "Leg_practice_L")
        version (str): Número de versión para el sistema (default: "001")

    Returns:
        str: Nombre del shape creado con el atributo FKIK, None si hay error

    Proceso Técnico:
        1. Validación del joint raíz
        2. Creación del locator temporal
           - Nombrado según convención
           - Shape renombrado
        3. Setup del atributo FKIK
           - Rango: 0.0 (FK) a 1.0 (IK)
           - Default: 0.0 (FK)
           - Keyable: True
        4. Transferencia al joint
           - Shape parented al joint raíz
           - Cleanup del locator temporal

    Requisitos:
        - Joint raíz ya creado y renombrado
        - Nomenclatura: upperLeg_{base_name}_joint_{version}

    Ejemplo:
        >>> result = create_fkik_attribute("Leg_practice_L", "001")
        >>> print(result)
        "Leg_practice_L_attributesShape_001"

    Notas:
        - El atributo FKIK se usa para blend entre sistemas
        - 0 = FK control total
        - 1 = IK control total
        - Valores intermedios = blend proporcional
    """
    root_joint = f"upperLeg_{base_name}_joint_{version}"
    if not cmds.objExists(root_joint):
        cmds.warning(f"⚠️ No existe el joint raíz: {root_joint}")
        return None

    loc_name = f"{base_name}_attributes_{version}"
    if cmds.objExists(loc_name):
        cmds.delete(loc_name)

    # Crear locator y shape
    loc = cmds.spaceLocator(name=loc_name)[0]
    shape = cmds.listRelatives(loc, shapes=True)[0]
    shape_new = f"{loc_name}Shape"
    cmds.rename(shape, shape_new)

    # Crear atributo FKIK
    if not cmds.attributeQuery("FKIK", node=shape_new, exists=True):
        cmds.addAttr(
            shape_new,
            longName="FKIK",
            attributeType="float",
            min=0,
            max=1,
            defaultValue=0,
        )
        cmds.setAttr(f"{shape_new}.FKIK", e=True, keyable=True)

    # Mover shape al joint raíz
    cmds.parent(shape_new, root_joint, add=True, shape=True, relative=True)
    cmds.delete(loc)

    print(f"✅ Atributo FKIK creado y combinado con {root_joint}")
    return shape_new


if __name__ == "__main__":
    create_fkik_attribute()
