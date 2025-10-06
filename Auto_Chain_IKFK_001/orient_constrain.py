import maya.cmds as cmds


def create_leg_orient_constraints(base_name="Leg_practice_L", version="001"):
    suffixes = ["upperLeg", "middleLeg"]
    chain_types = ["joint", "IK", "MAIN"]

    for segment in suffixes:
        # Nombres completos según la nomenclatura
        objects = [f"{segment}_{base_name}_{c}_{version}" for c in chain_types]

        # Verificar que existan
        missing = [obj for obj in objects if not cmds.objExists(obj)]
        if missing:
            cmds.warning(f"⚠️ Faltan estos objetos para {segment}: {missing}")
            continue

        # Target order: joint, IK -> MAIN (el MAIN es el constrained)
        targets = objects[0:2]
        constrained = objects[2]

        # Crear el orientConstraint con Maintain Offset = False
        constraint_name = cmds.orientConstraint(
            targets, constrained, maintainOffset=False
        )[0]

        print(f"✅ OrientConstraint creado: {constraint_name} → {constrained}")
