import maya.cmds as cmds
from Auto_Tail import (
    curve_from_joint,
    create_dynamics,
    rig_setup,
    mesh_setup,
    skinning_contrain,
    dyna_torus,
)


def auto_tail_ui():
    """
    Interfaz para ejecutar paso a paso el rig dinámico de cola.
    """
    window_name = "autoTailWindow"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="🐍 Auto Tail Rig Tool", widthHeight=(340, 420))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center")

    cmds.text(label="Herramienta de Cola Dinámica", height=30, align="center")
    cmds.separator(height=10, style="in")

    # === PASO 1 ===
    cmds.button(
        label="1️⃣ Crear Curva desde Joints",
        bgc=(0.3, 0.5, 0.8),
        command=lambda *_: curve_from_joint.create_dynamic_curve_from_joint(),
    )

    # === PASO 2 ===
    cmds.button(
        label="2️⃣ Hacer Curva Dinámica",
        bgc=(0.4, 0.6, 0.8),
        command=lambda *_: create_dynamics.make_hair_dynamic(),
    )

    # === PASO 3 ===
    cmds.button(
        label="3️⃣ Crear Rig Dinámico",
        bgc=(0.4, 0.7, 0.6),
        command=lambda *_: rig_setup.hair_rigging_setup(),
    )

    # === PASO 4 ===
    cmds.button(
        label="4️⃣ Configurar Mesh",
        bgc=(0.6, 0.7, 0.4),
        command=lambda *_: mesh_setup.tail_mesh_setup(),
    )

    # === PASO 5 ===
    cmds.button(
        label="5️⃣ Bind Skin + Constraints",
        bgc=(0.7, 0.6, 0.4),
        command=lambda *_: skinning_contrain.skin_and_constraint_setup(),
    )

    # === PASO 6 ===
    cmds.separator(height=15, style="in")
    cmds.text(
        label="⚠️ Antes de ejecutar este paso:\n"
        "1. Crea un toroide manualmente en la escena.\n"
        "2. Ubícalo visualmente sobre el PolyTail.\n"
        "3. Luego selecciona el toroide y presiona el botón.",
        align="center",
        wordWrap=True,
        height=70,
    )

    cmds.button(
        label="6️⃣ Crear Dyna Torus (Requiere selección del toroide)",
        bgc=(0.85, 0.55, 0.35),
        command=lambda *_: dyna_torus.create_dynamic_object(),
    )

    cmds.separator(height=15, style="in")
    cmds.button(
        label="❌ Cerrar",
        bgc=(0.5, 0.2, 0.2),
        command=lambda *_: cmds.deleteUI(window_name),
    )

    cmds.showWindow(window_name)


# Permitir ejecución directa
if __name__ == "__main__":
    auto_tail_ui()
