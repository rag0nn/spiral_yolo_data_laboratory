from spiral_dataset import SpiralDataset
from spiral_data import SpiralData
from spiral_events.object_detection.object import SpiralObject
from utils import chose_dataset
import cv2
from spiral_events.monitor_helper import SpiralMonitorHelper
ds = SpiralDataset(chose_dataset())

datas = ds.get_datas()

data:SpiralData =datas[0]
results = data.slice(600,500)

for key,(image,objects) in results.items():
    for obj in objects:
        obj:SpiralObject
        obj.convert_coordinates_to_int()
    image = SpiralMonitorHelper.paint_objects(image,objects)
    cv2.imshow(key,image)
    cv2.waitKey(0)
