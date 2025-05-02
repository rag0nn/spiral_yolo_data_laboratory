import cv2
import os
from tqdm import tqdm
from tools.dataset import SpiralDataset



def delete_not_conjugated_data():
    """
    Remove not conjugated data parts
    """
    path = "C:/Users/asus/Desktop/dataset/datasets/T22_O2_4"
    ds = SpiralDataset(path)
    problems = ds.check_data_balance()
    for prob in tqdm(problems):
        type, name = prob.split(" ")
        if type == "image_name":
            im_path = path + "/" + "detect/image_names/train" + "/" + name + ".jpg"
            os.remove(im_path)
            print("removed",im_path)
        elif type == 'txt':
            txt_path = path + "/" + "detect/labels/train"  + "/" + name + ".txt"
            os.remove(txt_path)
            print("removed",txt_path)
        else:
            raise Exception(f"Errrrrr {type}")
    
def add_prefix_to_data():
    image_folder = "./datasets/visdrone_1078_1916_3/detect/image_names/train"
    names = os.listdir(image_folder)

    for name in tqdm(names):
        image_path = image_folder + "/" + name
        image_name = cv2.imread(image_path)
        new_image = cv2.resize(image_name,(1200,600))
        cv2.imwrite(image_path,new_image)

            
def convert_voc2yolo():
    from pylabel import importer
    data_name = "T22_O2_4"
    # Klasör yolları
    xml_dir = f"C:/Users/asus/Desktop/TEKNOFEST_DATA/NESNE/{data_name}/voc_labels"  # PascalVOC XML dosyalarının bulunduğu klasör
    output_dir = f"C:/Users/asus/Desktop/TEKNOFEST_DATA/NESNE/{data_name}/labels"  # YOLO formatındaki etiketlerin kaydedileceği klasör

    dataset = importer.ImportVOC(path=xml_dir)
    dataset.export.ExportToYoloV5(output_dir)
    
    
def mark_dataset(path):
    import cv2
    ds = SpiralDataset(path)
    names = []
    for path in ds.image_paths:
        im = cv2.imread(path)
        im = cv2.resize(im,(1200,700))
        cv2.imshow("Q",im)
        q = cv2.waitKey(0)
        if q == ord("q"):
            break
        elif q == ord("d"):
            continue
        elif q == ord("t"):
            names.append(path.split("/")[-1].split(".")[-2])
            continue
    return names
#names = mark_dataset("C:/Users/asus/Desktop/dataset/datasets/SOAP")
#print(names)    

def move():
    import shutil
    names = ['1001_ppl_00751_crop', '1004_peoplepegia_2935', '1005_people_0050_416', '1009_peoplepegia_2800', '100_peoplepegia_1205', '1010_peoplepegia_1195', '1011_peoplepegia_2970', '1014_people_0042_140', '1033_ppl_3_00151_crop', '103_people_0008_440', '1041_ppl_2_01151_crop', '1043_people_0050_744', '1044_ppl_3_05901_crop', '104_people_0007_7830', '104_people_0007_7980', '1051_peoplepegia_2820', '1053_peoplepegia_2345', '1054_peoplepegia_2235', '1059_peoplepegia_1480', '105_people_0007_7755', '105_ppl_00401_crop', '105_ppl_2_01251_crop', '1068_peoplepegia_955', '1069_peoplepegia_2100', '106_ppl_3_01001_crop']
    for name in names:
        im_path = "C:/Users/asus/Desktop/dataset/datasets/SOAP/detect/image_names/train/" + name + ".jpg"
        txt_path = "C:/Users/asus/Desktop/dataset/datasets/SOAP/detect/labels/train/" + name + ".txt"
        new_im_path = "C:/Users/asus/Desktop/k/frames/" + name + ".jpg"
        new_txt_path = "C:/Users/asus/Desktop/k/labels/" + name + ".txt"
        shutil.move(im_path,new_im_path)
        shutil.move(txt_path,new_txt_path)
        print(im_path, " --> ", new_im_path)
        print(txt_path," --> ",new_txt_path)

#move()
    
    
def list_image_shapes():
    #ds_names = os.listdir("C:/Users/asus/Desktop/dataset/datasets")
    #paths = list(f"C:/Users/asus/Desktop/dataset/datasets/{ds_name}/detect/images/train"  for ds_name in ds_names)
    paths = ["C:/Users/asus/Desktop/dataset/datasets/afo/detect/images/train"]
    s = set()
    for path in tqdm(paths):
        image_names = os.listdir(path)
        for image_name in image_names:
            im_path = path + "/" +image_name
            im = cv2.imread(im_path)
            s.add(im.shape)
            
        print(path,s)

#list_image_shapes()



def sub_slice(img_path, lbl_path, out_img_path, out_lbl_path,
                  target_w=1920, target_h=1080):
    # Görseli ve etiketleri yükle
    img = cv2.imread(img_path)
    if img is None:
        print(f"[HATA] Görsel okunamadı: {img_path}")
        return
    h_src, w_src = img.shape[:2]
    # Kaynak boyutlar hedef boyuttan küçükse atla
    if w_src < target_w or h_src < target_h:
        print(f"[UYARI] Görsel hedef boyuttan küçük: {img_path}")
        return

    # Etiketleri yükle (class cx cy w h formatında, 0-1 aralığında)
    boxes = []
    with open(lbl_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls, cx, cy, bw, bh = parts
            cx, cy, bw, bh = map(float, (cx, cy, bw, bh))
            x = cx * w_src
            y = cy * h_src
            bw_px = bw * w_src
            bh_px = bh * h_src
            boxes.append({'cls': cls, 'x': x, 'y': y, 'w': bw_px, 'h': bh_px})

    # En yoğun etiket içeren crop'u bul
    max_count = -1
    best_crop = None
    for b in boxes:
        cx, cy = b['x'], b['y']
        x1 = int(round(cx - target_w/2))
        y1 = int(round(cy - target_h/2))
        x1 = max(0, min(x1, w_src - target_w))
        y1 = max(0, min(y1, h_src - target_h))
        cnt = sum(
            1 for bb in boxes
            if x1 <= bb['x'] <= x1 + target_w and y1 <= bb['y'] <= y1 + target_h
        )
        if cnt > max_count:
            max_count = cnt
            best_crop = (x1, y1)

    if best_crop is None:
        print(f"[UYARI] Merkez bulunamadı: {img_path}")
        return

    x1, y1 = best_crop
    crop = img[y1:y1 + target_h, x1:x1 + target_w]
    cv2.imwrite(out_img_path, crop)

    # Kırpılmış alandaki etiketleri yeniden yaz
    with open(out_lbl_path, 'w') as fw:
        for b in boxes:
            if not (x1 <= b['x'] <= x1 + target_w and y1 <= b['y'] <= y1 + target_h):
                continue
            x_rel = (b['x'] - x1) / target_w
            y_rel = (b['y'] - y1) / target_h
            w_rel = b['w'] / target_w
            h_rel = b['h'] / target_h
            fw.write(f"{b['cls']} {x_rel:.6f} {y_rel:.6f} {w_rel:.6f} {h_rel:.6f}\n")

def apply_sub_slice():
    """
    Obje yoğunluğu baz alınarak görüntüden istenen bir dilim alınır
    
    """
    import os
    import cv2
    import glob
    from tqdm import tqdm
    
    img_dir = 'C:/Users/asus/Desktop/dataset/datasets/semantic_drone/detect/images/train'
    lbl_dir = 'C:/Users/asus/Desktop/dataset/datasets/semantic_drone/detect/labels/train'
    out_img_dir = 'C:/Users/asus/Desktop/output/images'
    out_lbl_dir = 'C:/Users/asus/Desktop/output/labels'
    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_lbl_dir, exist_ok=True)

    img_files = glob.glob(os.path.join(img_dir, '*.jpg')) + glob.glob(os.path.join(img_dir, '*.png'))
    for img_path in tqdm(img_files):
        base = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(lbl_dir, base + '.txt')
        if not os.path.isfile(lbl_path):
            continue
        out_img_path = os.path.join(out_img_dir, base + os.path.splitext(img_path)[1])
        out_lbl_path = os.path.join(out_lbl_dir, base + '.txt')
        sub_slice(img_path, lbl_path, out_img_path, out_lbl_path)

#apply_sub_slice()


