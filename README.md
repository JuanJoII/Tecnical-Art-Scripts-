# Scripts de automatización de rig en Autodesk Maya

Este repositorio contiene un conjunto de herramientas para **automatizar procesos de rigging** en Autodesk Maya, incluyendo sistemas **FK/IK**, **Spline Column** y **Dynamic Tail**.

---

## Guía de uso general

1. Ejecuta el archivo `main.py` desde **Visual Studio Code** o directamente en **Maya**.
   Esto abrirá una ventana llamada **“Rigging Tools Launcher”**, desde la cual podrás acceder a todas las herramientas.
2. Para conocer el proceso completo de conexión entre **VSCode** y **Maya**, consulta este repositorio:
   👉 [vscode-environment-for-maya](https://github.com/JuanJoII/vscode-environment-for-maya)

---

## 🦿 Herramienta FK/IK

### Requisitos previos

* Debes tener una **cadena de exactamente 3 joints**.
  Si la herramienta detecta más de 3 joints, mostrará un error y detendrá el proceso.

---

### Pasos para crear el rig FK/IK

1. **Selecciona el primer joint** de tu cadena.
   En el **Rigging Tools Launcher**, elige **“IK/FK Rig Tools”**.

2. Se abrirá una ventana con dos controles principales:

   * **Selector de herramienta**
   * **Botón de ejecución**

3. En el menú desplegable selecciona **“Renombrar cadena”** y pulsa **“Ejecutar”**.

4. En la ventana de renombrado, deja los valores por defecto de:

   * `Base name`
   * `Chain type`
     Luego haz clic en **“Rename Selection”**.
     Esto aplicará una **nomenclatura estándar** necesaria para los pasos siguientes.

5. Pulsa **“Create IK and MAIN chains”** para generar las cadenas adicionales necesarias.
   Una vez completado, puedes cerrar la ventana **Rename Chain Tool**.

6. En el menú principal selecciona **“Crear grupos Root y Auto”** y ejecuta.
   Se crearán los grupos de organización correspondientes en la jerarquía.

7. Selecciona **“Crear sistema IK”** y ejecuta.
   Esto generará un **ikHandle**, una **curva de control** y un **efector** para la cadena IK.

8. Selecciona **“Crear Orient Constrain”** y ejecuta.
   Se aplicará un *orient constrain* en la cadena **MAIN**, conectándola con las cadenas **FK** e **IK**.

9. Selecciona **“Asignar curvas de control”** y ejecuta.
   Esto añadirá curvas de control sobre los joints **FK**, facilitando su manipulación.

10. Selecciona **“Crear atributo FKIK”** y ejecuta.
    Se creará un **locator** (por defecto dentro de `upperLeg_Leg_practice_L_joint_001`).
    En sus atributos aparecerá un atributo nuevo llamado **`FKIK`**.

11. Finalmente, selecciona **“Conectar nodos FKIK”** y ejecuta.
    Esto realizará las conexiones nodales necesarias para que el atributo **FKIK** controle el peso de los constraints entre **FK** e **IK** en la cadena **MAIN**.

---

## Spine Rig (Spline Column)

### Requisitos previos y preparación

* Crea una **cadena de joints** con la cantidad de joints que necesites (la herramienta acepta cualquier número).

* Selecciona toda la cadena y ve a **Skeleton → Orient Joints** en Maya. Ajusta las opciones de orientación de la siguiente manera:

  * **Primary Axis:** `X`
  * **Secondary Axis:** `Y`
  * **Secondary Axis World Orientation:** `Z`
    Esto garantiza una orientación consistente y evita rotaciones indeseadas al generar el rig.

* Una vez orientados los joints, **selecciona el último joint** de la cadena, abre el **Attribute Editor** y en el campo **Joint Orient** establece todos los valores en **0** (`0, 0, 0`).
  Esto es importante para evitar que el último eslabón de la columna presente rotaciones erróneas en el rig final.

---

### 🔧 Pasos para crear el Spine Rig

1. **Selecciona el primer joint** de la cadena.
   En el **Rigging Tools Launcher**, elige **“Spine Auto Rig Tools”**.

2. Se abrirá una ventana con dos opciones principales:

   * **Crear desde 0** — si quieres que la herramienta genere la cadena y el rig paso a paso.
   * **Usar Joints seleccionados** — si ya has creado manualmente tu cadena de joints.

3. **Si eliges “Crear desde 0”**: la interfaz te guiará por todo el proceso (creación de joints, curvas, controles y constraints) paso a paso.

4. **Si eliges “Usar Joints seleccionados”**:

   * Verifica que la cadena esté correctamente orientada (ver sección de requisitos previos).
   * Selecciona el primer joint y pulsa **“Usar Joints seleccionados”**.
     La herramienta generará automáticamente el rig completo: curvas spline, controles, skinning básico y constraints necesarios.

---

## Notas importantes

* ⚠️ **No modifiques el archivo `send2maya.py`**.
  Este archivo gestiona la comunicación entre **VSCode** y **Maya**; cambiarlo puede romper la conexión.

* Mantén la nomenclatura y la estructura generadas por las herramientas para evitar errores en pasos posteriores.

* Si vas a integrar tus propias utilidades en el launcher, sigue la estructura modular del proyecto (nombres, rutas y convenciones de los módulos).

* Si algo falla, revisa la **shelf** de errores en Maya y el **output/Script Editor** para ver mensajes concretos que te indiquen qué paso falló.

---

## Tecnologías usadas

| Tecnología           | Descripción                                                                 |
| -------------------- | --------------------------------------------------------------------------- |
| 🐍 **Python**        | Lenguaje principal de desarrollo para los scripts y módulos.                |
| ⚡ **uv**             | Gestor de entornos y dependencias ultrarrápido para proyectos Python.       |
| 🎨 **Autodesk Maya** | Plataforma principal para la ejecución de los scripts y desarrollo de rigs. |