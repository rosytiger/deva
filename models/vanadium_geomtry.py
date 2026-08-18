import numpy as np
from Bio.PDB import PDBParser
from core.interfaces import BaseModel
from core.registry import register_model
from evolve.individual import Individual


@register_model("vanadium_geometry")
class VanadiumGeometryObjective(BaseModel):
    def setup(self, config, device='cpu'):
        self.config = config
        # Vanadium-Oxygen/Nitrogen canonical bonds average 1.95A - 2.35A
        self.ideal_distance = 2.15
        self.tolerance = 0.20

    def score(self, individual: Individual):
        pdb_path = individual.get_name()
        parser = PDBParser(QUIET=True)
        try:
            structure = parser.get_structure("mutant", pdb_path)
        except Exception:
            individual.add_fitness({'vanadium_geometry': -100.0})
            return

        v_atom = None
        coordinating_atoms = []

        # 1. Parse coordinate space for the metal ion and donor atoms
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        if atom.element == 'V':
                            v_atom = atom
                        elif residue.get_resname() in ['ASP', 'GLU', 'HIS', 'TYR']:
                            # Extract functional shell carboxylate/imidazole/phenol donors
                            if atom.get_name() in ['OD1', 'OD2', 'OE1', 'OE2', 'ND1', 'NE2', 'OH']:
                                coordinating_atoms.append(atom)

        if v_atom is None:
            # Heavily penalize structural evaluations that purge the target metal coordinate
            individual.add_fitness({'vanadium_geometry': -100.0})
            return

        # 2. Evaluate spatial distance matrices to target coordinates
        v_coord = v_atom.get_coord()
        valid_bonds = []
        for atom in coordinating_atoms:
            dist = np.linalg.norm(atom.get_coord() - v_coord)
            if (self.ideal_distance - self.tolerance) <= dist <= (self.ideal_distance + self.tolerance):
                valid_bonds.append(atom)

        # 3. Formulate the geometric fitness scoring metric
        coordination_count = len(valid_bonds)
        # Perfect reward parameters tuned specifically for 6-coordinate octahedral architecture
        if coordination_count == 6:
            fitness_score = 100.0
        elif coordination_count == 5:
            fitness_score = 75.0
        elif coordination_count == 4:
            fitness_score = 40.0
        else:
            fitness_score = float(coordination_count * 5)

        # 4. Bind the calculated fitness vector back into dEVA population metrics
        individual.add_fitness({'vanadium_geometry': fitness_score})