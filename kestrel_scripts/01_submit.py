import os, sys 
#sys.path.insert(0,'/ocean/projects/chm240001p/ssonti/kultools')
print(os.getcwd())
from ase import io
from src.kul_tools import KulTools as KT

kt = KT(gamma_only=False,structure_type='zeo')
kt.set_calculation_type('opt')
atoms = io.read('init.traj')
atoms.pbc=True
kt.set_structure(atoms)
kt.set_overall_vasp_params({'gga':'RP','encut':400,'lreal':'Auto', 'algo':'fast', 'isif':3, 'kpts':(1,1,1)})
kt.run()
