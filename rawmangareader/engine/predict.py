import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

import os
import cv2

class Predictor():
    MODEL_FILE = "rawmangareader\\model\\faster_rcnn_R_50_FPN_3x.yaml"
    OUTPUT_DIR = "rawmangareader\\model"

    def __init__(self, useCuda=True):
        self.cfg = get_cfg()
        self.cfg.merge_from_file(Predictor.MODEL_FILE)
        self.cfg.DATALOADER.NUM_WORKERS = 2
        self.cfg.SOLVER.IMS_PER_BATCH = 2
        self.cfg.SOLVER.BASE_LR = 0.001
        self.cfg.SOLVER.MAX_ITER = 1000
        self.cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # faster, and good enough for this toy dataset (default: 512)
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (text)
        self.cfg.OUTPUT_DIR = Predictor.OUTPUT_DIR
        self.cfg.MODEL.WEIGHTS = os.path.join(self.cfg.OUTPUT_DIR, "model_final.pth")
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7   # set the testing threshold for this model
        self.cfg.MODEL.DEVICE = 'cuda' if useCuda else 'cpu'

        self.predictor = DefaultPredictor(self.cfg)

    def predict(self, image_path):
        """Predict where the speech bubble locate in the image

        Arguments:
            image_path {string} -- Path to image file

        Returns:
            [list[list]] -- List of boxes. Each box is a list with coordinate (x0,y0,x1,y1)
        """
        image = cv2.imread(image_path)
        outputs = self.predictor(image)
        predictions = outputs["instances"].to("cpu")
        boxes = predictions.pred_boxes if predictions.has("pred_boxes") else None
        if boxes is not None:
            boxes = boxes.tensor.numpy()
            return boxes.tolist()
        else:
            return None
