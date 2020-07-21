from flask import Flask
from flask import request
from flask.json import jsonify
from werkzeug.utils import secure_filename
import os
import base64
from ctypes import *


app = Flask(__name__)
lib = CDLL("libdarknet.so", RTLD_GLOBAL)

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int),
                ("uc", POINTER(c_float)),
                ("points", c_int),
                ("embeddings", POINTER(c_float)),
                ("embedding_size", c_int),
                ("sim", c_float),
                ("track_id", c_int)]

class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45, debug= False):
    """
    Performs the meat of the detection
    """
    #pylint: disable= C0321
    im = load_image(image, 0, 0)
    ret = detect_image(net, meta, im, thresh, hier_thresh, nms, debug)
    free_image(im)
    return ret

def detect_image(net, meta, im, thresh=.5, hier_thresh=.5, nms=.45, debug= False):
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    letter_box = 0
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum, letter_box)
    num = pnum[0]
    if nms:
        do_nms_sort(dets, num, meta.classes, nms)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append({'name': i,
                            'score': dets[j].prob[i],
                            'left': b.x,
                            'top': b.y,
                            'width': b.w,
                            'height': b.h})
    res = sorted(res, key=lambda x: -x['score'])
    free_detections(dets, num)
    return res

def performDetect(imagePath="raw.jpg", thresh= 0.25, configPath = "./data/obj.cfg", weightPath = "weights", metaPath= "./data/obj.data", showImage= True, makeImageOnly = False, initOnly= False):
    global metaMain, netMain, altNames #pylint: disable=W0603
    assert 0 < thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `"+os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `"+os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `"+os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = load_net_custom(configPath.encode("ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = load_meta(metaPath.encode("ascii"))
    if initOnly:
        print("Initialized detector")
        return None
    if not os.path.exists(imagePath):
        raise ValueError("Invalid image path `"+os.path.abspath(imagePath)+"`")
    detections = detect(netMain, metaMain, imagePath.encode("ascii"), thresh)
    return detections


netMain = None
metaMain = None
altNames = None

performDetect(initOnly = True)

def convert_and_save(b64_string):
    with open("raw.jpg", "wb") as fh:
        fh.write(base64.decodebytes(b64_string.encode()))

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        print('Saving to raw.jpg')
        convert_and_save(request.form['image'])
        
        print('Returning new prediction')
        return jsonify(performDetect(thresh=float(request.form['threshold'])))
    if request.method == 'GET':
        print('Returning old prediction')
        return jsonify(performDetect())
