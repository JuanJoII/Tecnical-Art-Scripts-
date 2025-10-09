import maya.cmds as cmds
import re

def create_leg_orient_constraints():
    """
    Crea orient constraints FK + IK -> MAIN para cada cadena MAIN encontrada en la escena.
    - Agrupa por root de cadena para procesar cada cadena en orden root->end.
    - Para cada joint MAIN busca su FK y su IK.
    - IMPORTANTE: El orden es FK, IK -> MAIN (los drivers primero, luego el constrained).
    - maintainOffset = False (desactivado) para que MAIN se oriente en valores intermedios.
    """
    # 1) Buscar todos los joints cuyo nombre corto termine en _MAIN_###.
    all_joints = cmds.ls(type="joint", long=True) or []
    mains = [j for j in all_joints if re.search(r"_MAIN_\d{3}$", j.split("|")[-1])]

    if not mains:
        cmds.warning("⚠️ No se encontraron joints MAIN con sufijo '_MAIN_###'.")
        return []

    # 2) Determinar los roots de cada cadena MAIN (roots son los MAIN cuya parent no sea MAIN)
    main_roots = []
    for m in mains:
        parent = cmds.listRelatives(m, parent=True, type="joint", fullPath=True) or []
        if not parent:
            # no tiene padre joint -> es root
            main_roots.append(m)
        else:
            parent_short = parent[0].split("|")[-1]
            if not re.search(r"_MAIN_\d{3}$", parent_short):
                # el padre no es de la cadena MAIN -> este es root
                main_roots.append(m)

    # si por alguna razón no detectamos roots (topología inusual), tomamos el conjunto único de mains como una sola cadena
    if not main_roots:
        main_roots = [mains[0]]

    created_constraints = []

    # 3) Procesar cada cadena MAIN por separado (root -> end)
    for root in main_roots:
        # obtener todos los descendants (devuelve hijo->descendientes), agregamos root y revertimos para root->end
        descendants = cmds.listRelatives(root, ad=True, type="joint", fullPath=True) or []
        chain = descendants + [root]
        chain.reverse()  # ahora chain = [root, ..., end]

        print("\n" + "="*50)
        print(f"Procesando cadena MAIN cuyo root es: {root}  (joints: {len(chain)})")
        print("="*50)

        for idx, main_full in enumerate(chain):
            main_short = main_full.split("|")[-1]

            # construir nombres esperados FK e IK (solo en el nombre corto)
            fk_short = re.sub(r"_MAIN_", "_joint_", main_short, count=1)
            ik_short = re.sub(r"_MAIN_", "_IK_", main_short, count=1)

            # resolver a nombres completos en la escena (si existen)
            fk_long = cmds.ls(fk_short, long=True) or []
            ik_long = cmds.ls(ik_short, long=True) or []

            if not fk_long or not ik_long:
                missing = []
                if not fk_long:
                    missing.append(f"FK expected: {fk_short}")
                if not ik_long:
                    missing.append(f"IK expected: {ik_short}")
                cmds.warning(f"⚠️ Mapeo faltante para MAIN '{main_short}': {missing}. Se omite este joint.")
                continue

            fk = fk_long[0]
            ik = ik_long[0]

            # IMPORTANTE: Orden correcto = [FK, IK] -> MAIN
            # maintainOffset = False (desactivado) para que MAIN se oriente en valores intermedios
            try:
                cons = cmds.orientConstraint(fk, ik, main_full, maintainOffset=False)[0]
                created_constraints.append(cons)
                print(f"✅ OrientConstraint creado: {cons}")
                print(f"   Drivers: {fk_short}, {ik_short}")
                print(f"   Constrained: {main_short}")
                print(f"   maintainOffset: False")
            except Exception as e:
                cmds.warning(f"⚠️ Error creando orientConstraint para {main_short}: {e}")

    print(f"\n📦 Total orient constraints creados: {len(created_constraints)}\n")
    return created_constraints


def list_main_chains():
    """Helper rápido para debug - lista qué joints MAIN existen"""
    mains = [j for j in cmds.ls(type="joint", long=True) if re.search(r"_MAIN_\d{3}$", j.split("|")[-1])]
    roots = []
    for m in mains:
        parent = cmds.listRelatives(m, parent=True, type="joint", fullPath=True) or []
        if not parent or not re.search(r"_MAIN_\d{3}$", parent[0].split("|")[-1]):
            roots.append(m)
    print("MAIN roots detectados:")
    for r in roots:
        print(" -", r)
    return roots


def verify_constraints():
    """Verifica los constraints creados y su estado"""
    constraints = cmds.ls(type="orientConstraint") or []
    if not constraints:
        print("⚠️ No hay orient constraints en la escena")
        return
    
    print(f"\n{'='*50}")
    print(f"Verificando {len(constraints)} constraints...")
    print(f"{'='*50}")
    
    for cons in constraints:
        targets = cmds.orientConstraint(cons, query=True, targetList=True) or []
        constrained = cmds.orientConstraint(cons, query=True, constrainedObject=True) or []
        weights = cmds.orientConstraint(cons, query=True, weight=True) or []
        maintain_offset = cmds.orientConstraint(cons, query=True, maintainOffset=True)
        
        print(f"\n✓ {cons}")
        print(f"  Constrained: {constrained}")
        print(f"  Targets (Drivers): {targets}")
        print(f"  Weights: {weights}")
        print(f"  MaintainOffset: {maintain_offset}")


if __name__ == "__main__":
    create_leg_orient_constraints()