from tag_tracker import TagTracker
import os

src_pat = r"C:\Users\asus\Desktop\dataset\scripts\tag_tracker\src" 
dst_pat = r"C:\Users\asus\Desktop\dataset\scripts\tag_tracker\outputs" 
track_backbone_pat = os.path.join(os.path.dirname(__file__), "nanotrack_backbone_sim.onnx")
track_neckhead_pat = os.path.join(os.path.dirname(__file__), "nanotrack_head_sim.onnx")

TagTracker(src_pat,dst_pat,track_backbone_pat,track_neckhead_pat)

