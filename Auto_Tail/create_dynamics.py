import maya.cmds as cmds
import maya.mel as mel


def make_hair_dynamic():
    """
    Script para hacer dinámicas las curvas de cabello en Maya.
    Busca la curva 'dynamic_cv_001' y ejecuta FX -> nHair -> Make selected Curves Dynamic
    """

    # Nombre de la curva a buscar
    curve_name = "dynamic_cv_001"

    # Verificar si la curva existe
    if not cmds.objExists(curve_name):
        cmds.warning(f"La curva '{curve_name}' no existe en la escena.")
        return False

    # Verificar que sea una curva NURBS
    if cmds.nodeType(curve_name) != "nurbsCurve":
        # Si es un transform, obtener la forma
        shapes = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
        if not shapes:
            cmds.warning(f"'{curve_name}' no es una curva NURBS válida.")
            return False
        curve_name = shapes[0]

    # Seleccionar la curva
    cmds.select(curve_name, replace=True)
    print(f"Curva seleccionada: {curve_name}")

    # Ejecutar el comando de FX para hacer dinámica la curva
    try:
        # Comando de MEL para hacer la curva dinámica
        mel.eval('makeCurvesDynamic(2, {"0"})')
        print("Curva convertida a dinámica correctamente.")
        return True
    except Exception as e:
        cmds.warning(f"Error al hacer la curva dinámica: {str(e)}")
        return False


# Ejecutar el script
if __name__ == "__main__":
    make_hair_dynamic()
