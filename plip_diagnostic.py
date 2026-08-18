from plip.structure.preparation import PDBComplex

mol = PDBComplex()
mol.load_pdb('outputs/2wcb_default/packed/2WCB_s0_gen0_ind0.pdb')
mol.analyze()

keys = list(mol.interaction_sets.keys())
print("ALL INTERACTION SET KEYS:", keys)
print()

for k in keys:
    it = mol.interaction_sets[k]
    print(f"--- {k} ---")
    print("  attrs on interaction set object:", [a for a in dir(it) if not a.startswith('_')])
    for attr_name in ['hbonds_lig', 'hbonds_pdon', 'saltbridge_lneg', 'saltbridge_pneg',
                      'pistacking', 'pication', 'halogen_bonds', 'halogen',
                      'hydrophobic_contacts', 'waterbridge', 'metal_complexes']:
        val = getattr(it, attr_name, 'MISSING_ATTR')
        length = len(val) if isinstance(val, list) else 'n/a'
        print(f"  {attr_name}: type={type(val).__name__} len={length}")
    print()
