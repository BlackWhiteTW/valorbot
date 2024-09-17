import torch
import torchvision

boxes = torch.tensor([[0, 0, 10, 10], [5, 5, 15, 15]], dtype=torch.float32).cuda()
scores = torch.tensor([0.9, 0.8], dtype=torch.float32).cuda()
iou_thres = 0.5

try:
    keep = torchvision.ops.nms(boxes, scores, iou_thres)
    print("NMS output:", keep)
except Exception as e:
    print("Error during NMS:", e)
