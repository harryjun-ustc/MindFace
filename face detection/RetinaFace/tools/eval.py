"""Eval Retinaface_resnet50_or_mobilenet0.25."""
import argparse
import os
import time
import datetime
import numpy as np
import cv2
import sys

from mindspore import Tensor, context
from mindspore.train.serialization import load_checkpoint, load_param_into_net

base_path = os.getcwd()
sys.path.append(base_path)

from configs.RetinaFace_mobilenet import cfg_mobile025
from configs.RetinaFace_resnet50 import cfg_res50
from utils.utils import decode_bbox, prior_box

from model.retinaface import RetinaFace
from backbone.resnet import resnet50
from backbone.mobilenet import mobilenet025

class Timer():
    def __init__(self):
        self.start_time = 0.
        self.diff = 0.

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.diff = time.time() - self.start_time

class DetectionEngine:
    """DetectionEngine"""
    def __init__(self, cfg):
        self.results = {}
        self.nms_thresh = cfg['val_nms_threshold']
        self.conf_thresh = cfg['val_confidence_threshold']
        self.iou_thresh = cfg['val_iou_threshold']
        self.var = cfg['variance']
        self.save_prefix = cfg['val_predict_save_folder']
        self.gt_dir = cfg['val_gt_dir']

    def _iou(self, a, b):
        """_iou"""
        A = a.shape[0]
        B = b.shape[0]
        max_xy = np.minimum(
            np.broadcast_to(np.expand_dims(a[:, 2:4], 1), [A, B, 2]),
            np.broadcast_to(np.expand_dims(b[:, 2:4], 0), [A, B, 2]))
        min_xy = np.maximum(
            np.broadcast_to(np.expand_dims(a[:, 0:2], 1), [A, B, 2]),
            np.broadcast_to(np.expand_dims(b[:, 0:2], 0), [A, B, 2]))
        inter = np.maximum((max_xy - min_xy + 1), np.zeros_like(max_xy - min_xy))
        inter = inter[:, :, 0] * inter[:, :, 1]

        area_a = np.broadcast_to(
            np.expand_dims(
                (a[:, 2] - a[:, 0] + 1) * (a[:, 3] - a[:, 1] + 1), 1),
            np.shape(inter))
        area_b = np.broadcast_to(
            np.expand_dims(
                (b[:, 2] - b[:, 0] + 1) * (b[:, 3] - b[:, 1] + 1), 0),
            np.shape(inter))
        union = area_a + area_b - inter
        return inter / union

    def _nms(self, boxes, threshold=0.5):
        """_nms"""
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        scores = boxes[:, 4]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        reserved_boxes = []
        while order.size > 0:
            i = order[0]
            reserved_boxes.append(i)
            max_x1 = np.maximum(x1[i], x1[order[1:]])
            max_y1 = np.maximum(y1[i], y1[order[1:]])
            min_x2 = np.minimum(x2[i], x2[order[1:]])
            min_y2 = np.minimum(y2[i], y2[order[1:]])

            intersect_w = np.maximum(0.0, min_x2 - max_x1 + 1)
            intersect_h = np.maximum(0.0, min_y2 - max_y1 + 1)
            intersect_area = intersect_w * intersect_h
            ovr = intersect_area / (areas[i] + areas[order[1:]] - intersect_area)

            indices = np.where(ovr <= threshold)[0]
            order = order[indices + 1]

        return reserved_boxes

    def write_result(self):
        """write_result"""
        # save result to file.
        import json
        t = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S')
        try:
            if not os.path.isdir(self.save_prefix):
                os.makedirs(self.save_prefix)

            self.file_path = self.save_prefix + '/predict' + t + '.json'
            f = open(self.file_path, 'w')
            json.dump(self.results, f)
        except IOError as e:
            raise RuntimeError("Unable to open json file to dump. What(): {}".format(str(e)))
        else:
            f.close()
            return self.file_path

    def detect(self, boxes, confs, resize, scale, image_path, priors,phase='trainval'):
        """detect"""
        if boxes.shape[0] == 0:
            # add to result
            event_name, img_name = image_path.split('/')
            self.results[event_name][img_name[:-4]] = {'img_path': image_path,
                                                       'bboxes': []}
            return

        boxes = decode_bbox(np.squeeze(boxes.asnumpy(), 0), priors, self.var)
        boxes = boxes * scale / resize

        scores = np.squeeze(confs.asnumpy(), 0)[:, 1]
        # ignore low scores
        inds = np.where(scores > self.conf_thresh)[0]
        boxes = boxes[inds]
        scores = scores[inds]

        # keep top-K before NMS
        order = scores.argsort()[::-1]
        boxes = boxes[order]
        scores = scores[order]

        # do NMS
        dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
        keep = self._nms(dets, self.nms_thresh)
        dets = dets[keep, :]

        dets[:, 2:4] = (dets[:, 2:4].astype(np.int32) - dets[:, 0:2].astype(np.int32)).astype(np.float32) # int
        dets[:, 0:4] = dets[:, 0:4].astype(np.int32).astype(np.float32)                                 # int


        # add to result
        if phase == 'test':
            return dets[:, :5].astype(np.float32).tolist()

        event_name, img_name = image_path.split('/')
        if event_name not in self.results.keys():
            self.results[event_name] = {}
        self.results[event_name][img_name[:-4]] = {'img_path': image_path,
                                                   'bboxes': dets[:, :5].astype(np.float32).tolist()}

    def _get_gt_boxes(self):
        """_get_gt_boxes"""
        from scipy.io import loadmat
        gt = loadmat(os.path.join(self.gt_dir, 'wider_face_val.mat'))
        hard = loadmat(os.path.join(self.gt_dir, 'wider_hard_val.mat'))
        medium = loadmat(os.path.join(self.gt_dir, 'wider_medium_val.mat'))
        easy = loadmat(os.path.join(self.gt_dir, 'wider_easy_val.mat'))

        faceboxes = gt['face_bbx_list']
        events = gt['event_list']
        files = gt['file_list']

        hard_gt_list = hard['gt_list']
        medium_gt_list = medium['gt_list']
        easy_gt_list = easy['gt_list']

        return faceboxes, events, files, hard_gt_list, medium_gt_list, easy_gt_list

    def _norm_pre_score(self):
        """_norm_pre_score"""
        max_score = 0
        min_score = 1

        for event in self.results:
            for name in self.results[event].keys():
                bbox = np.array(self.results[event][name]['bboxes']).astype(np.float32)
                if bbox.shape[0] <= 0:
                    continue
                max_score = max(max_score, np.max(bbox[:, -1]))
                min_score = min(min_score, np.min(bbox[:, -1]))

        length = max_score - min_score
        for event in self.results:
            for name in self.results[event].keys():
                bbox = np.array(self.results[event][name]['bboxes']).astype(np.float32)
                if bbox.shape[0] <= 0:
                    continue
                bbox[:, -1] -= min_score
                bbox[:, -1] /= length
                self.results[event][name]['bboxes'] = bbox.tolist()

    def _image_eval(self, predict, gt, keep, iou_thresh, section_num):
        """_image_eval"""
        _predict = predict.copy()
        _gt = gt.copy()

        image_p_right = np.zeros(_predict.shape[0])
        image_gt_right = np.zeros(_gt.shape[0])
        proposal = np.ones(_predict.shape[0])

        # x1y1wh -> x1y1x2y2
        _predict[:, 2:4] = _predict[:, 0:2] + _predict[:, 2:4]
        _gt[:, 2:4] = _gt[:, 0:2] + _gt[:, 2:4]

        ious = self._iou(_predict[:, 0:4], _gt[:, 0:4])
        for i in range(_predict.shape[0]):
            gt_ious = ious[i, :]
            max_iou, max_index = gt_ious.max(), gt_ious.argmax()
            if max_iou >= iou_thresh:
                if keep[max_index] == 0:
                    image_gt_right[max_index] = -1
                    proposal[i] = -1
                elif image_gt_right[max_index] == 0:
                    image_gt_right[max_index] = 1

            right_index = np.where(image_gt_right == 1)[0]
            image_p_right[i] = len(right_index)



        image_pr = np.zeros((section_num, 2), dtype=np.float32)
        for section in range(section_num):
            _thresh = 1 - (section + 1)/section_num
            over_score_index = np.where(predict[:, 4] >= _thresh)[0]
            if over_score_index.shape[0] <= 0:
                image_pr[section, 0] = 0
                image_pr[section, 1] = 0
            else:
                index = over_score_index[-1]
                p_num = len(np.where(proposal[0:(index+1)] == 1)[0])
                image_pr[section, 0] = p_num
                image_pr[section, 1] = image_p_right[index]

        return image_pr


    def get_eval_result(self):
        """get_eval_result"""
        self._norm_pre_score()
        facebox_list, event_list, file_list, hard_gt_list, medium_gt_list, easy_gt_list = self._get_gt_boxes()
        section_num = 1000
        sets = ['easy', 'medium', 'hard']
        set_gts = [easy_gt_list, medium_gt_list, hard_gt_list]
        ap_key_dict = {0: "Easy   Val AP : ", 1: "Medium Val AP : ", 2: "Hard   Val AP : ",}
        ap_dict = {}
        for _set in range(len(sets)):
            gt_list = set_gts[_set]
            count_gt = 0
            pr_curve = np.zeros((section_num, 2), dtype=np.float32)
            for i, _ in enumerate(event_list):
                event = str(event_list[i][0][0])
                image_list = file_list[i][0]
                event_predict_dict = self.results[event]
                event_gt_index_list = gt_list[i][0]
                event_gt_box_list = facebox_list[i][0]

                for j, _ in enumerate(image_list):
                    predict = np.array(event_predict_dict[str(image_list[j][0][0])]['bboxes']).astype(np.float32)
                    gt_boxes = event_gt_box_list[j][0].astype('float')
                    keep_index = event_gt_index_list[j][0]
                    count_gt += len(keep_index)

                    if gt_boxes.shape[0] <= 0 or predict.shape[0] <= 0:
                        continue
                    keep = np.zeros(gt_boxes.shape[0])
                    if keep_index.shape[0] > 0:
                        keep[keep_index-1] = 1

                    image_pr = self._image_eval(predict, gt_boxes, keep,
                                                iou_thresh=self.iou_thresh,
                                                section_num=section_num)
                    pr_curve += image_pr

            precision = pr_curve[:, 1] / pr_curve[:, 0]
            recall = pr_curve[:, 1] / count_gt

            precision = np.concatenate((np.array([0.]), precision, np.array([0.])))
            recall = np.concatenate((np.array([0.]), recall, np.array([1.])))
            for i in range(precision.shape[0]-1, 0, -1):
                precision[i-1] = np.maximum(precision[i-1], precision[i])
            index = np.where(recall[1:] != recall[:-1])[0]
            ap = np.sum((recall[index + 1] - recall[index]) * precision[index + 1])


            print(ap_key_dict[_set] + '{:.4f}'.format(ap))

        return ap_dict


def val(cfg):

    context.set_context(mode=context.GRAPH_MODE, device_target='GPU', save_graphs=False)
    # context.set_context(mode=context.PYNATIVE_MODE, device_target='GPU', save_graphs=False)
    

    if cfg['name'] == 'ResNet50':
        backbone = resnet50(1001)
    elif cfg['name'] == 'MobileNet025':
        backbone = mobilenet025(1000)
    network = RetinaFace(phase='predict', backbone=backbone, cfg=cfg)
    backbone.set_train(False)
    network.set_train(False)

    # load checkpoint
    assert cfg['val_model'] is not None, 'val_model is None.'
    param_dict = load_checkpoint(cfg['val_model'])
    print('Load trained model done. {}'.format(cfg['val_model']))
    network.init_parameters_data()
    load_param_into_net(network, param_dict)

    # testing dataset
    testset_folder = cfg['val_dataset_folder']
    testset_label_path = cfg['val_dataset_folder'] + "label.txt"
    with open(testset_label_path, 'r') as f:
        _test_dataset = f.readlines()
        test_dataset = []
        for im_path in _test_dataset:
            if im_path.startswith('# '):
                test_dataset.append(im_path[2:-1])  # delete '# ...\n'

    num_images = len(test_dataset)

    timers = {'forward_time': Timer(), 'misc': Timer()}

    if cfg['val_origin_size']:
        h_max, w_max = 0, 0
        for img_name in test_dataset:
            image_path = os.path.join(testset_folder, 'images', img_name)
            _img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if _img.shape[0] > h_max:
                h_max = _img.shape[0]
            if _img.shape[1] > w_max:
                w_max = _img.shape[1]

        h_max = (int(h_max / 32) + 1) * 32
        w_max = (int(w_max / 32) + 1) * 32

        priors = prior_box(image_sizes=(h_max, w_max),
                           min_sizes=[[16, 32], [64, 128], [256, 512]],
                           steps=[8, 16, 32],
                           clip=False)
    else:
        target_size = 1600
        max_size = 2160
        priors = prior_box(image_sizes=(max_size, max_size),
                           min_sizes=[[16, 32], [64, 128], [256, 512]],
                           steps=[8, 16, 32],
                           clip=False)

    # init detection engine
    detection = DetectionEngine(cfg)
    
    
    # testing begin
    print('Predict box starting')
    ave_time = 0
    ave_forward_pass_time = 0
    ave_misc = 0
    for i, img_name in enumerate(test_dataset):
        image_path = os.path.join(testset_folder, 'images', img_name)

        img_raw = cv2.imread(image_path, cv2.IMREAD_COLOR)
        img = np.float32(img_raw)

        # testing scale
        if cfg['val_origin_size']:
            resize = 1
            assert img.shape[0] <= h_max and img.shape[1] <= w_max
            image_t = np.empty((h_max, w_max, 3), dtype=img.dtype)
            image_t[:, :] = (104.0, 117.0, 123.0)
            image_t[0:img.shape[0], 0:img.shape[1]] = img
            img = image_t
        else:
            im_size_min = np.min(img.shape[0:2])
            im_size_max = np.max(img.shape[0:2])
            resize = float(target_size) / float(im_size_min)
            # prevent bigger axis from being more than max_size:
            if np.round(resize * im_size_max) > max_size:
                resize = float(max_size) / float(im_size_max)

            img = cv2.resize(img, None, None, fx=resize, fy=resize, interpolation=cv2.INTER_LINEAR)

            assert img.shape[0] <= max_size and img.shape[1] <= max_size
            image_t = np.empty((max_size, max_size, 3), dtype=img.dtype)
            image_t[:, :] = (104.0, 117.0, 123.0)
            image_t[0:img.shape[0], 0:img.shape[1]] = img
            img = image_t

        scale = np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]], dtype=img.dtype)
        img -= (104, 117, 123)
        img = img.transpose(2, 0, 1)
        img = np.expand_dims(img, 0)
        img = Tensor(img)

        timers['forward_time'].start()
        boxes, confs, _ = network(img)
        timers['forward_time'].end()
        timers['misc'].start()
        detection.detect(boxes, confs, resize, scale, img_name, priors)
        timers['misc'].end()

        ave_time = ave_time + timers['forward_time'].diff + timers['misc'].diff
        ave_forward_pass_time = ave_forward_pass_time + timers['forward_time'].diff
        ave_misc = ave_misc + timers['misc'].diff
        print('im_detect: {:d}/{:d} forward_pass_time: {:.4f}s misc: {:.4f}s sum_time: {:.4f}s'.format(i + 1, num_images,
                                                                                     timers['forward_time'].diff,
                                                                                     timers['misc'].diff,
                                                                                     timers['forward_time'].diff + timers['misc'].diff))
    print("ave_time: {:.4f}s".format(ave_time/(i+1)))
    print("ave_forward_pass_time: {:.4f}s".format(ave_forward_pass_time/(i+1)))
    print("ave_misc: {:.4f}s".format(ave_misc/(i+1)))
    print('Predict box done.')
    print('Eval starting')

    if cfg['val_save_result']:
        # Save the predict result if you want.
        predict_result_path = detection.write_result()
        print('predict result path is {}'.format(predict_result_path))

    detection.get_eval_result()
    print('Eval done.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='val')
    parser.add_argument('--backbone_name', type=str, default='ResNet50',
                        help='backbone name')
    parser.add_argument('--checkpoint', type=str, default='pretrained/RetinaFace_ResNet50.ckpt',
                        help='checpoint path')    
    args = parser.parse_args()
    if args.backbone_name == 'ResNet50':
        config = cfg_res50
    elif args.backbone_name == 'MobileNet025':
        config = cfg_mobile025
    config['val_model'] = args.checkpoint
    val(cfg=config)
