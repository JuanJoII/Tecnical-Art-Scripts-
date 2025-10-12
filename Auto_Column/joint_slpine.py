import maya.cmds as cmds


def create_spine_chain_s_shape(
    num_joints=5, base_name="joint", curve_name="splineCurve_001"
):
    """
    Crea una cadena de joints en forma de S y una curva spline perfectamente alineada.
    Cada joint corresponde a un CV de la curva.
    """
    if num_joints < 2:
        cmds.warning("⚠️ Se necesitan al menos 2 joints para formar una columna.")
        return

    # Generar posiciones en forma de S (curva suave)
    positions = []
    height_step = 2.0
    x_amp = 0.5
    for i in range(num_joints):
        # alterna izquierda/derecha
        x = -x_amp if i % 2 else x_amp
        y = i * height_step
        positions.append((x, y, 0))

    # Crear joints
    joints = []
    for i, pos in enumerate(positions, 1):
        jnt = cmds.joint(name=f"{base_name}_{i:03d}", position=pos)
        joints.append(jnt)

    cmds.select(clear=True)

    # Crear curva con los mismos puntos (1 CV por joint)
    curve = cmds.curve(name=curve_name, degree=1, ep=positions)
    print(f"✅ Curva creada con {num_joints} CVs.")

    # No rebuild para mantener correspondencia exacta
    print("✅ Joints creados:", joints)
    print(f"✅ Curva alineada: {curve}")

    # Volver al root joint
    cmds.select(clear=True)

    # Crear curva EP a partir de las posiciones
    curve = cmds.curve(name=curve_name, degree=1, ep=positions)

    # Rebuild curva (Parameter range 0-1, spans=2)
    cmds.rebuildCurve(
        curve,
        rebuildType=0,
        spans=num_joints - 1,  # número de segmentos = joints - 1
        keepRange=0,
        keepControlPoints=False,
        replaceOriginal=True,
    )

    print("✅ Joints creados:", joints)
    print(f"✅ Curva creada con forma de columna: {curve}")
    return joints, curve


# Uso:
# create_spine_chain_s_shape()
if __name__ == "__main__":
    create_spine_chain_s_shape()
