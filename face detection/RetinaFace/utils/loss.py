"""Loss."""
import mindspore.common.dtype as mstype
import mindspore.nn as nn
from mindspore.ops import operations as P
from mindspore.ops import functional as F
from mindspore import Tensor

class SoftmaxCrossEntropyWithLogits(nn.Cell):
    """SoftmaxCrossEntropyWithLogits"""
    def __init__(self):
        super(SoftmaxCrossEntropyWithLogits, self).__init__()
        self.log_softmax = P.LogSoftmax()
        self.neg = P.Neg()
        self.one_hot = P.OneHot()
        self.on_value = Tensor(1.0, mstype.float32)
        self.off_value = Tensor(0.0, mstype.float32)
        self.reduce_sum = P.ReduceSum()

    def construct(self, logits, labels):
        """construct"""
        prob = self.log_softmax(logits)
        labels = self.one_hot(labels, F.shape(logits)[-1], self.on_value, self.off_value)

        return self.neg(self.reduce_sum(prob * labels, 1))


class MultiBoxLoss(nn.Cell):
    """MultiBoxLoss"""
    def __init__(self, num_classes, num_boxes, neg_pre_positive, batch_size):
        super(MultiBoxLoss, self).__init__()
        self.num_classes = num_classes
        self.num_boxes = num_boxes
        self.neg_pre_positive = neg_pre_positive
        self.notequal = P.NotEqual()
        self.less = P.Less()
        self.tile = P.Tile()
        self.reduce_sum = P.ReduceSum()
        self.reduce_mean = P.ReduceMean()
        self.expand_dims = P.ExpandDims()
        self.smooth_l1_loss = P.SmoothL1Loss()
        self.cross_entropy = SoftmaxCrossEntropyWithLogits()
        self.maximum = P.Maximum()
        self.minimum = P.Minimum()
        self.sort_descend = P.TopK(True)
        self.sort = P.TopK(True)
        self.max = P.ReduceMax()
        self.log = P.Log()
        self.exp = P.Exp()
        self.concat = P.Concat(axis=1)
        self.reduce_sum2 = P.ReduceSum(keep_dims=True)
        self.mul = P.Mul()
        self.reduce_sum_new = P.ReduceSum(keep_dims=True)

    def construct(self, loc_data, loc_t, conf_data, conf_t, landm_data, landm_t):
        """construct"""
        # landm loss
        mask_pos1 = F.cast(self.less(0.0, F.cast(conf_t, mstype.float32)), mstype.float32)

        N1 = self.maximum(self.reduce_sum(mask_pos1), 1)
        mask_pos_idx1 = self.tile(self.expand_dims(mask_pos1, -1), (1, 1, 10))
        loss_landm = self.reduce_sum(self.smooth_l1_loss(landm_data, landm_t) * mask_pos_idx1)
        loss_landm = loss_landm / N1

        # Localization Loss
        mask_pos = F.cast(self.notequal(0, conf_t), mstype.float32)
        conf_t = F.cast(mask_pos, mstype.int32)

        N = self.maximum(self.reduce_sum(mask_pos), 1)
        mask_pos_idx = self.tile(self.expand_dims(mask_pos, -1), (1, 1, 4))
        loss_l = self.reduce_sum(self.smooth_l1_loss(loc_data, loc_t) * mask_pos_idx)
        loss_l = loss_l / N

        # Conf Loss
        conf_t_shape = F.shape(conf_t)
        conf_t = F.reshape(conf_t, (-1,))
        indices = self.concat((1 - F.reshape(conf_t, (-1, 1)), F.reshape(conf_t, (-1, 1))))

        batch_conf = F.reshape(conf_data, (-1, self.num_classes))
        x_max = self.max(batch_conf)
        loss_c = self.log(self.reduce_sum2(self.exp(batch_conf - x_max), 1)) + x_max
        mul_tensor = self.mul(indices, batch_conf)
        loss_c = loss_c - self.reduce_sum_new(mul_tensor, 1)
        loss_c = F.reshape(loss_c, conf_t_shape)

        # hard example mining
        num_matched_boxes = F.reshape(self.reduce_sum(mask_pos, 1), (-1,))
        neg_masked_cross_entropy = F.cast(loss_c * (1 - mask_pos), mstype.float32)

        _, loss_idx = self.sort_descend(neg_masked_cross_entropy, self.num_boxes)
        _, relative_position = self.sort(F.cast(loss_idx, mstype.float32), self.num_boxes)
        relative_position = F.cast(relative_position, mstype.float32)
        relative_position = relative_position[:, ::-1]
        relative_position = F.cast(relative_position, mstype.int32)

        num_neg_boxes = self.minimum(num_matched_boxes * self.neg_pre_positive, self.num_boxes - 1)
        tile_num_neg_boxes = self.tile(self.expand_dims(num_neg_boxes, -1), (1, self.num_boxes))
        top_k_neg_mask = F.cast(self.less(relative_position, tile_num_neg_boxes), mstype.float32)

        cross_entropy = self.cross_entropy(batch_conf, conf_t)
        cross_entropy = F.reshape(cross_entropy, conf_t_shape)

        loss_c = self.reduce_sum(cross_entropy * self.minimum(mask_pos + top_k_neg_mask, 1))

        loss_c = loss_c / N

        return loss_l, loss_c, loss_landm
