import cv2
import os
from tqdm import tqdm
from core_organization import create_dataset


image_folder = "./datasets/visdrone_1078_1916_3/detect/images/train"
names = os.listdir(image_folder)

for name in tqdm(names):
    image_path = image_folder + "/" + name
    image = cv2.imread(image_path)
    new_image = cv2.resize(image,(1200,600))
    cv2.imwrite(image_path,new_image)


    
    
""" 

prefix = "AFO_"
image_folder = "./datasets/Visdrone_distil/detect/images/train"
lbl_foler = "./datasets/Visdrone_distil/detect/labels/train"
names = os.listdir(image_folder)


classes = {}
for name in tqdm(names):
    image_path = image_folder + "/" + name
    image = cv2.imread(image_path)
    shape_text = f"{image.shape[0]}_{image.shape[1]}_{image.shape[2]}"
    if shape_text not in list(classes.keys()):
        classes[shape_text] = []
    
    classes[shape_text].append(name)
print(classes)

for key, names in tqdm(classes.items()):
    create_dataset(f"{prefix}{key}","./datasets")
    new_fder_image = f"./datasets/{prefix}{key}/detect/images/train"
    new_fder_lbl = f"./datasets/{prefix}{key}/detect/labels/train"
    for name in tqdm(names):
        image = cv2.imread(image_folder + "/" + name)
        cv2.imwrite(new_fder_image + "/" + name,image)
        
        f = open(lbl_foler + "/" + name[:-4] + ".txt","r")
        lines = f.readlines()
        f.close()
        
        f = open(new_fder_lbl + "/" + name[:-4] + ".txt","w")
        f.writelines(lines)
        f.close()
"""


"""
ds_names = os.listdir("./datasets")

k = set()
for ds_name in tqdm(ds_names):
    p = f"./datasets/{ds_name}/detect/images/train"
    im_names = os.listdir(p)
    
    for im_name in tqdm(im_names):
        im_path = p + "/" + im_name
        
        image = cv2.imread(im_path)
        if image.shape != (600,1200,3):
            k.add(ds_name)
            break
            
print(k)

"""