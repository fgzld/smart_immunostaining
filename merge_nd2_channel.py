import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
from skimage import exposure
from skimage.io import imsave
import glob

# Function to normalize intensity across channels
def normalize_intensity(channel, min_intensity, max_intensity):
    normalized = exposure.rescale_intensity(channel, in_range=(min_intensity, max_intensity), out_range=(0, 1))
    return normalized

# Function to merge three channels into an RGB image
def merge_channels(dapi, nestin, tuj1, dapi_range, nestin_range, tuj1_range):
    # Normalize each channel using global min/max
    dapi_norm = normalize_intensity(dapi, *dapi_range)
    nestin_norm = normalize_intensity(nestin, *nestin_range)
    tuj1_norm = normalize_intensity(tuj1, *tuj1_range)
    
    # Merge into RGB
    rgb_image = np.stack([tuj1_norm, nestin_norm, dapi_norm], axis=-1)
    return rgb_image

# Function to determine global min/max for all channels across files
def calculate_global_min_max(file_paths):
    dapi_min, dapi_max = float('inf'), float('-inf')
    nestin_min, nestin_max = float('inf'), float('-inf')
    tuj1_min, tuj1_max = float('inf'), float('-inf')

    for file_path in file_paths:
        with ND2Reader(file_path) as nd2:
            dapi = nd2.get_frame(0)  # Channel 0: DAPI
            nestin = nd2.get_frame(1)  # Channel 1: NESTIN
            tuj1 = nd2.get_frame(2)  # Channel 2: TUJ1
            
            dapi_min = min(dapi_min, np.min(dapi))
            dapi_max = max(dapi_max, np.max(dapi))
            nestin_min = min(nestin_min, np.min(nestin))
            nestin_max = max(nestin_max, np.max(nestin))
            tuj1_min = min(tuj1_min, np.min(tuj1))
            tuj1_max = max(tuj1_max, np.max(tuj1))

    return (dapi_min, dapi_max), (nestin_min, nestin_max), (tuj1_min, tuj1_max)

# Process .nd2 files using global min/max. 
# depending on the order of channel (RGB) and the markers, adjust this function accordingly.
def process_nd2(file_path, output_path, dapi_range, nestin_range, tuj1_range):
    with ND2Reader(file_path) as nd2:
        # Access channel data by specifying the index
        dapi = nd2.get_frame(0)  # Channel 0: DAPI
        nestin = nd2.get_frame(1)  # Channel 1: NESTIN
        tuj1 = nd2.get_frame(2)  # Channel 2: TUJ1
        
        # Merge channels
        rgb_image = merge_channels(dapi, nestin, tuj1, dapi_range, nestin_range, tuj1_range)
        
        # Save as image
        imsave(output_path, (rgb_image * 255).astype(np.uint8))
        print(f"Saved merged image to {output_path}")

# for example, i know that my file 1920-3-1 has a different channel order so i have this alternative process nd2 function
def alternative_process_nd2(file_path, output_path, dapi_range, nestin_range, tuj1_range):
    # this is 
    with ND2Reader(file_path) as nd2:
        # Access channel data by specifying the index
        dapi = nd2.get_frame(0)  # Channel 0: DAPI
        tuj1 = nd2.get_frame(1)  
        nestin = nd2.get_frame(2) 
        
        # Merge channels
        rgb_image = merge_channels(dapi, nestin, tuj1, dapi_range, nestin_range, tuj1_range)
        
        # Save as image
        imsave(output_path, (rgb_image * 255).astype(np.uint8))
        print(f"Saved merged image to {output_path}")

# accessing all the files that end with .nd2 in the same folder
file_paths = glob.glob("*.nd2")
dapi_range, nestin_range, tuj1_range = calculate_global_min_max(file_paths)

for file_path in file_paths:
    output_path = file_path.replace(".nd2", "_merged.png")
    process_nd2(file_path, output_path, dapi_range, nestin_range, tuj1_range)
    if file_path == '12.06.24 TUJ1 Rb NES ck no1920 pos3-1.nd2':
        alternative_process_nd2(file_path, output_path, dapi_range, nestin_range, tuj1_range)
# print(dapi_range, nestin_range, tuj1_range)
