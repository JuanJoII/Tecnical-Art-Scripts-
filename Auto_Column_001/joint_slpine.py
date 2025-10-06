import maya.cmds as cmds

def create_spine_chain_s_shape(num_joints=5, base_name="joint", curve_name="splineCurve_001"):
    """
    Crea una columna de joints con forma en 'S' y la curva spline correspondiente.
    """
    # Posiciones aproximadas en forma de S
    positions = [
        (0, 0, 0),
        (0.5, 2, 0),
        (-0.5, 4, 0),
        (0.5, 6, 0),
        (0, 8, 0),
    ]

    # Ajustar si num_joints distinto de 5
    if num_joints != 5:
        # Repartir los puntos en Y y alternar X para simular curvatura
        positions = []
        for i in range(num_joints):
            x = (0.5 if i % 2 == 0 else -0.5)  # alterna izquierda/derecha
            y = i * 2
            positions.append((x, y, 0))

    # Crear joints
    joints = []
    for i, pos in enumerate(positions, 1):
        jnt = cmds.joint(name=f"{base_name}_{i:03d}", position=pos)
        joints.append(jnt)

    # Volver al root joint
    cmds.select(clear=True)

    # Crear curva EP a partir de las posiciones
    curve = cmds.curve(name=curve_name, degree=1, ep=positions)

    # Rebuild curva (Parameter range 0-1, spans=2)
    cmds.rebuildCurve(curve,
                      rebuildType=0,
                      spans=2,
                      keepRange=0,
                      keepControlPoints=False,
                      replaceOriginal=True)

    print("✅ Joints creados:", joints)
    print(f"✅ Curva creada con forma de columna: {curve}")
    return joints, curve

# Uso:
# create_spine_chain_s_shape()
if __name__ == "__main__":
    create_spine_chain_s_shape()