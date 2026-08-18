import os
import torch
import logging
from typing import Dict
from collections import OrderedDict

from common.utils import ensure_dir
from core.interfaces import BaseModel
from core.registry import register_model
from evolve.individual import Individual

from .metal3d.metal3d import run
from .metal3d.utils.helpers import *
from .metal3d.utils.model import Model as Metal3D

logger = logging.getLogger("evolution")
logger.setLevel(logging.DEBUG)

@register_model("metal3d_model")
class Metal3DModel(BaseModel):

    def __init__(self):
        pass

    def setup(self, config: Dict, device: str='cpu') -> None:
        self.config = config
        self.device = device

        self.pdb = self.config.input.pdb
        self.pdb_name = os.path.split(self.pdb)[-1].split('.')[0]
        
        self.model_config = self.config.models.metal3d
        self.max_metal_p = self.model_config.max_metal_p

        # Build var_idx for Metal3D scoring: pull the chain-prefixed
        # var_residues string from the ligandmpnn config (e.g. "B15 B25 A85 A89"),
        # strip the chain letters, and join the plain residue numbers into a
        # single selection string (e.g. "15 25 85 89") for Metal3D's run().
        # This restricts Metal3D's scan to just the target site instead of
        # the whole structure (its default behavior when var_idx is empty).
        var_residues_str = self.config.models.ligandmpnn.var_residues
        var_residues_list = var_residues_str.split()
        resnums = [item[1:] for item in var_residues_list]  # strip leading chain letter
        self.var_idx = " ".join(resnums)
        logger.info(f"Metal3D scoring restricted to var_idx: {self.var_idx} "
                    f"(from var_residues: {var_residues_str})")

        outputs = self.config.general.outputs

        self.output_packed = os.path.join(outputs, "packed")
        self.output_metals = os.path.join(outputs, 'metals')
        self.output_gen = os.path.join(outputs, "gen")

        ensure_dir(self.output_packed)
        ensure_dir(self.output_metals)
        ensure_dir(self.output_gen)

        logger.info('Setting up metal-site prediction with Metal3D...')
        self.model = Metal3D()

        checkpoint_metal3d = torch.load(self.model_config.model_path, map_location=self.device)
        new_checkpoint_metal3d = OrderedDict()
        for k, v in checkpoint_metal3d.items():
            name = k.replace("module.", "")  # remove 'module.' prefix
            new_checkpoint_metal3d[name] = v
        
        self.model.load_state_dict(new_checkpoint_metal3d)
        self.model.eval()
        self.model.to(self.device)

    def score(self, individual: Individual):
        
        index = individual.get_index()
        gen = individual.get_gen()
        curr_pdb = individual.get_name()
        
        out_root = os.path.join(self.output_metals, f'{self.pdb_name}_metals_gen{gen}_ind{index}')

        pmetal, outfile, found = run(self.model,
                                    output_metals = self.output_metals,
                                    output_gen = self.output_gen,
                                    out_root = out_root,
                                    pdb = curr_pdb,
                                    pdb_name = self.pdb_name, 
                                    var_idx = self.var_idx,
                                    max_metal_p = self.max_metal_p,
                                    device=self.device)
        
        individual.add_fitness({'pmetal': pmetal})
        individual.update_name(outfile)