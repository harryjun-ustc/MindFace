# Retinaface_resnet50 in MindSpore


## Introduction
RetinaFace is a practical single-stage SOTA face detector which is initially introduced in [arXiv technical report](https://arxiv.org/abs/1905.00641v2) and then accepted by [CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/html/Deng_RetinaFace_Single-Shot_Multi-Level_Face_Localisation_in_the_Wild_CVPR_2020_paper.html). Retinaface was put forward in 2019, and it has the best performance when applied to WIDER FACE dataset. Compared with S3FD and MTCNN, RetinaFace significantly improves the recall rate of small faces, but it is not suitable for multi-scale face detection. In order to solve these problems, RetinaFace uses the RetinaFace feature pyramid structure for feature fusion between different scales, and adds SSH modules.
![retinaface_picture](https://camo.githubusercontent.com/a3fa0edd910b60f94085b14fa1a171bfa30bfea7b9591ca7a380565e4e581b80/68747470733a2f2f696e7369676874666163652e61692f6173736574732f696d672f6769746875622f31313531334430352e6a7067)


## Updates
Comming soon!


## WiderFace Val Performance
Standard Models.
| Model | Easy-set | Mesium-set | Hard-set |
| :-- | :-: | :-: | :-: |
| RetinaFace_mobile025(mindspore) | 88.62% | 86.96% | 79.93% |
| RetinaFace_mobile025(mxnet) | 88.72% | 86.97% | 79.19% |
| RetinaFace_resnet50(MindSpore) | 94.42% | 93.37% | 89.25% |
| RetinaFace_resnet50(mxnet) | 94.86% | 93.87% | 88.33% |


## Data
1.Download annotations (face bounding boxes & five facial landmarks) from [baidu cloud](https://pan.baidu.com/s/1Laby0EctfuJGgGMgRRgykA) or [gdrive](https://drive.google.com/file/d/1BbXxIiY-F74SumCNG6iwmJJ5K3heoemT/view)

2.Download the [WIDERFACE dataset](http://shuoyang1213.me/WIDERFACE/)

3.Organise the dataset directory under insightface/RetinaFace/ as follows:
```

  data/retinaface/
    train/
      images/
      label.txt
    val/
      images/
      label.txt
    test/
      images/
      label.txt

```


## Quick Start
<details>
    <summary>Installation</summary>
    [Install MindSpore](https://www.mindspore.cn/install)
</details>

<details>
    <summary>Datasets</summary>
    You can download datasets from [here](http://shuoyang1213.me/WIDERFACE/)
</details>

<details>
    <summary>Train on GPU</summary>
    ```
    export CUDA_VISIBLE_DEVICES=0
    python train.py > train.log 2>&1 &
    ```
</details>

<details>
    <summary>Evaluate on GPU</summary>
    ```
    export CUDA_VISIBLE_DEVICES=0
    python eval.py > eval.log 2>&1 &  
    ```
</details>


## RetinaFace Pretrained Models
You can download the pretrained model from RetinaFace-ResNet50 ([baidu cloud](link) or [googledrive](link)) and  RetinaFace-MobileNet025 ([baidu cloud](link) or [googledrive](link)). 

You can verify the results in the table with the downloaded pretrained model.


## Deployment


## Third-party resources

