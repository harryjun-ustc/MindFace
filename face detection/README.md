# Retinaface in MindSpore


## Introduction
MindSpore is a new generation of full-scenario AI computing framework launched by Huawei in August 2019 and released On March 28, 2020.

RetinaFace is a practical single-stage SOTA face detector which is accepted by [CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/html/Deng_RetinaFace_Single-Shot_Multi-Level_Face_Localisation_in_the_Wild_CVPR_2020_paper.html). 


This repository is the mindspore implementation of RetinaFace, and has achieved great performance. We implemented two versions based on ResNet50 and MobileNet0.25 to meet different needs.
![retinaface_picture](https://camo.githubusercontent.com/a3fa0edd910b60f94085b14fa1a171bfa30bfea7b9591ca7a380565e4e581b80/68747470733a2f2f696e7369676874666163652e61692f6173736574732f696d672f6769746875622f31313531334430352e6a7067)

## Updates
Comming soon!


  
## WiderFace Val Performance

WiderFace Val Performance When using Resnet50 or MobileNet0.25 as backbone, comparing with MxNet implement.
| Model | Easy-set | Mesium-set | Hard-set |
| :-- | :-: | :-: | :-: |
| RetinaFace_mobile025 (MindSpore) | 88.62% | 86.96% | 79.93% |
| RetinaFace_mobile025 (MxNet) | 88.72% | 86.97% | 79.19% |
| RetinaFace_resnet50 (MindSpore) | 94.42% | 93.37% | 89.25% |
| RetinaFace_resnet50 (MxNet) | 94.86% | 93.87% | 88.33% |



## Quick Start
1. Installation

    1.1 Git clone this repo

    ```
    git clone https://github.com/harryjun-ustc/MindFace.git
    ```

    1.2 Install dependencies

    ```
    pip install -r requirements.txt
    ```
    
2. Prepare Data

    2.1. Download annotations from [baidu cloud](link) or [gdrive](link)

    2.2. Download the [WIDERFACE dataset](http://shuoyang1213.me/WIDERFACE/)

    2.3. Organise the dataset directory under MindFace/RetinaFace/ as follows:
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
3. Set Config File

    You can Modify the parameters of the config file in ./configs.
    We provide two versions of config for MobileNet0.25 and ResNet50 as backbone.

4. Train
```
    python tools/train.py --backbone ResNet50
```

5. Eval
```
    python tools/eval.py --backbone ResNet50
```

6. Predict
```
    python tools/test.py --backbone ResNet50 --image_path ./imgs/0000.jpg
```



## RetinaFace Pretrained Models
You can download the pretrained model from RetinaFace-ResNet50 ([baidu cloud](link) or [googledrive](link)) and  RetinaFace-MobileNet025 ([baidu cloud](link) or [googledrive](link)). 

You can verify the results in the table with the downloaded pretrained model.


## Deployment

## 

## Third-party resources

