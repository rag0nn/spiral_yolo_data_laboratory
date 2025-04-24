import cv2
import os
from tqdm import tqdm
from tools.organization import create_dataset
from tools.dataset import SpiralDataset



def delete_not_conjugated_data():
    import os
    path = "C:/Users/asus/Desktop/tools/2024/spirai_yolo_data_lab/dataset/datasets/EVD4UAV"
    ds = SpiralDataset(path)
    problems = ds.check_data_balance()
    for prob in problems:
        type, name = prob.split(" ")
        if type == "image":
            im_path = path + "/" + "detect/images/train" + "/" + name + ".jpg"
            os.remove(im_path)
        elif type == 'txt':
            txt_path = path + "/" + "detect/labels/train"  + "/" + name + ".txt"
            os.remove(txt_path)
        else:
            raise Exception(f"Errrrrr {type}")
    print(problems[:5])
    print(problems[-5:])
delete_not_conjugated_data()


def add_prefix_to_data():
    image_folder = "./datasets/visdrone_1078_1916_3/detect/images/train"
    names = os.listdir(image_folder)

    for name in tqdm(names):
        image_path = image_folder + "/" + name
        image = cv2.imread(image_path)
        new_image = cv2.resize(image,(1200,600))
        cv2.imwrite(image_path,new_image)

def delete_zero_tag_data():
    from tools.dataset import SpiralDataset
    path =  "C:/Users/asus/Desktop/tools/2024/spirai_yolo_data_lab/dataset/datasets/T22_O2_2"
    ds = SpiralDataset(path)
    datas = ds.get_datas()
    print(datas[:3])

delete_zero_tag_data()
"""


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