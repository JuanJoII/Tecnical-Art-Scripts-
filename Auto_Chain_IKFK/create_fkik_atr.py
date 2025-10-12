import maya.cmds as cmds


def create_fkik_attribute(base_name="Leg_practice_L", version="001"):
    """
    Crea un locator con el atributo FKIK (0–1) y lo combina con el joint raíz.
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
