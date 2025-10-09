import maya.cmds as cmds


def connect_locators_to_curve(
    curve_name="splineCurve_001", base_name="spineLoc_ctrl", num_locs=None
):
    """
    Conecta locators a los CVs de una curva spline usando nodos decomposeMatrix.
    Esta versión es robusta:
     - reutiliza decomposeMatrix si existe
     - no fuerza conexiones si ya hay otras diferentes (avisa y omite)
     - filtra y parenta solo los locators válidos (evita errores de "parent" y ciclos)
    """
    # Validar existencia curva (transform)
    if not cmds.objExists(curve_name):
        cmds.warning(f"⚠️ La curva {curve_name} no existe.")
        return []

    # Resolver nombre completo del transform de la curva
    curve_full = cmds.ls(curve_name, long=True)
    if not curve_full:
        cmds.warning(f"⚠️ No pude resolver la curva {curve_name} (ls falló).")
        return []
    curve_full = curve_full[0]

    # Obtener shape fullPath
    shapes = cmds.listRelatives(curve_full, shapes=True, fullPath=True) or []
    if not shapes:
        cmds.warning(f"⚠️ La curva {curve_full} no tiene shape.")
        return []
    curve_shape = shapes[0]

    # Número de CVs disponibles en la curva
    try:
        num_cvs = cmds.getAttr(f"{curve_shape}.controlPoints", size=True)
    except Exception:
        cmds.warning(f"⚠️ No pude leer controlPoints de {curve_shape}.")
        return []

    # Listar locators existentes (fullPath)
    existing_locs = cmds.ls(f"{base_name}_*", type="transform", long=True) or []
    if not existing_locs:
        cmds.warning(f"⚠️ No se encontraron locators con el prefijo {base_name}_")
        return []

    # Determinar cuántos ítems procesar
    num_locs = num_locs or len(existing_locs)
    # No procesar más de los locators existentes ni más CVs que existan
    num_locs = min(num_locs, len(existing_locs), num_cvs)

    processed = []
    for i in range(num_locs):
        loc_short = f"{base_name}_{i + 1:03d}"
        # resolver fullPath del locator específico
        loc_full = cmds.ls(loc_short, long=True) or []
        if not loc_full:
            cmds.warning(f"⚠️ Locator esperado {loc_short} no existe (se omite).")
            continue
        loc = loc_full[0]

        # crear o reutilizar decomposeMatrix con nombre consistente
        decomp_name = f"{loc_short}_decompMatrix"
        decomp_full = cmds.ls(decomp_name, long=True) or []
        if decomp_full:
            decomp = decomp_full[0]
        else:
            decomp = cmds.createNode("decomposeMatrix", name=decomp_name)

        # Conectar worldMatrix -> decompose.inputMatrix si no está conectado
        in_conns = (
            cmds.listConnections(f"{decomp}.inputMatrix", s=True, d=False, plugs=True)
            or []
        )
        if not in_conns:
            try:
                cmds.connectAttr(
                    f"{loc}.worldMatrix[0]", f"{decomp}.inputMatrix", force=True
                )
            except Exception as e:
                cmds.warning(
                    f"⚠️ Falló conectar {loc}.worldMatrix → {decomp}.inputMatrix: {e}"
                )
        else:
            # ya conectado, no hacemos nada
            pass

        # Conectar decompose.outputTranslate -> curve_shape.controlPoints[i] si es seguro hacerlo
        dst_attr = f"{curve_shape}.controlPoints[{i}]"
        existing_src = cmds.listConnections(dst_attr, s=True, d=False, plugs=True) or []

        if existing_src:
            # si ya está conectado desde este mismo decomp, ok; de lo contrario, no sobreescribir
            already_from_this = any(
                src.startswith(f"{decomp}.outputTranslate") for src in existing_src
            )
            if already_from_this:
                print(f"♻️ {dst_attr} ya conectado desde {decomp}. Se omite.")
            else:
                cmds.warning(
                    f"⚠️ {dst_attr} ya tiene conexión previa ({existing_src[0]}), se omite conectar desde {decomp}."
                )
        else:
            try:
                cmds.connectAttr(f"{decomp}.outputTranslate", dst_attr, force=True)
                print(f"✅ {loc} conectado vía {decomp} → {dst_attr}")
                processed.append(loc)
            except Exception as e:
                cmds.warning(
                    f"⚠️ Error conectando {decomp}.outputTranslate → {dst_attr}: {e}"
                )

    # --- Emparejar (parent) los locators bajo la curva de forma segura ---
    # Filtrar y evitar ciclos/auto-parent
    safe_to_parent = []
    # obtener la lista de todos los padres de la curva (para detectar ciclos)
    curve_parents = cmds.listRelatives(curve_full, allParents=True, fullPath=True) or []

    for loc in existing_locs:
        if not cmds.objExists(loc):
            continue
        # evitar agregar la curva misma
        if loc == curve_full:
            continue
        parent = cmds.listRelatives(loc, parent=True, fullPath=True) or []
        if parent and parent[0] == curve_full:
            # ya está parentado correctamente
            continue
        # evitar crear ciclo: si la curva es hija del locator (la curva tiene al locator como ancestro), no parentar
        if loc in curve_parents:
            cmds.warning(
                f"⚠️ No se puede parentar {loc} bajo {curve_full} (crearía ciclo)."
            )
            continue
        safe_to_parent.append(loc)

    if safe_to_parent:
        try:
            cmds.parent(safe_to_parent, curve_full)
            print(f"📌 {len(safe_to_parent)} locators emparentados bajo {curve_full}")
        except Exception as e:
            cmds.warning(f"⚠️ Error al emparentar locators: {e}")
    else:
        print(
            "♻️ No hay locators nuevos para emparentar (todos ya estaban o se detectaron riesgos)."
        )

    return processed
