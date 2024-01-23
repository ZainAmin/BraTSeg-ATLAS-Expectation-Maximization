import shutil
import subprocess
import numpy as np
import pandas as pd
import seaborn as sns
import SimpleITK as sitk
import matplotlib.pyplot as plt
from tqdm import tqdm
from typing import List
from pathlib import Path



def elastix(
    fix_img_path: Path,
    mov_img_path: Path,
    res_path: Path,
    parameters_path: Path,
    keep_just_useful_files: bool = True
):

    # Fix filenames and create folders
    mov_img_name = mov_img_path.name.split(".")[0]
    if res_path.name.endswith('.img') or ('.nii' in res_path.name):
        res_filename = f'{res_path.name.split(".")[0]}.nii.gz'
        res_path = res_path.parent / 'res_tmp'
    else:
        res_filename = f'{mov_img_name}.nii.gz'
        res_path = res_path / 'res_tmp'
    res_path.mkdir(exist_ok=True, parents=True)

    # Run elastix
    subprocess.call([
        'elastix', '-out', str(res_path), '-f', str(fix_img_path), '-m',
        str(mov_img_path), '-p', str(parameters_path)
    ])

    # Fix resulting filenames
    (res_path/'result.0.nii.gz').rename(res_path.parent/res_filename)
    transformation_file_name = f'TransformParameters_{mov_img_name}.txt'
    (res_path/'TransformParameters.0.txt').rename(res_path.parent/transformation_file_name)

    if keep_just_useful_files:
        shutil.rmtree(res_path)

    return res_path.parent/transformation_file_name




def transformix(
    mov_img_path: Path,
    res_path: Path,
    transformation_path: Path,
    keep_just_useful_files: bool = True
):

    # Fix filenames and create folders
    if res_path.name.endswith('.img') or ('.nii' in res_path.name):
        res_filename = f'{res_path.name.split(".")[0]}.nii.gz'
        res_path = res_path.parent / 'res_tmp'
    else:
        mov_img_name = mov_img_path.name.split(".")[0]
        res_filename = f'{mov_img_name}.nii.gz'
        res_path = res_path / 'res_tmp'
    res_path.mkdir(exist_ok=True, parents=True)

    # Run transformix
    subprocess.call([
        'transformix', '-out', str(res_path), '-in', str(mov_img_path),
        '-tp', str(transformation_path)
    ])

    # Fix resulting filenames
    (res_path/'result.nii.gz').rename(res_path.parent/res_filename)
    if keep_just_useful_files:
        shutil.rmtree(res_path)
        
        
        
        

def modify_parameter(
    field_value_list: List[tuple], in_par_map_path: Path, out_par_map_path: Path = None
):

    pm = sitk.ReadParameterFile(str(in_par_map_path))
    for [field, value] in field_value_list:
        pm[field] = (value, )
    out_par_map_path = in_par_map_path if out_par_map_path is None else out_par_map_path
    sitk.WriteParameterFile(pm, str(out_par_map_path))
    
    
    
  
def min_max_norm(img: np.ndarray, max_val: int = None, dtype: str = None):

    if max_val is None:
        max_val = np.iinfo(img.dtype).max
    img = (img - img.min()) / (img.max() - img.min()) * max_val
    if dtype is not None:
        return img.astype(dtype)
    else:
        return img

    
