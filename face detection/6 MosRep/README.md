# MosRep in MindSpore

## Introduction
MindSpore is a new generation of full-scenario AI computing framework launched by Huawei in August 2019 and released On March 28, 2020.


### Mosaic Representation Learning for Self-supervised Visual Pre-training 
We propose a mosaic representation learning framework (MosRep), consisting of a new data augmentation strategy that enriches the backgrounds of each small crop and improves the quality of visual representations.
Extensive experimental results demonstrate that our method improves the performance far greater than the multi-crop strategy on a series of downstream tasks, e.g., +7.4% and +4.9% than the multi-crop strategy on ImageNet-1K with 1% label and 10% label, respectively.

This is a PyTorch implementation of [our paper.](https://openreview.net/pdf?id=JAezPMehaUu)

## Updates
Comming soon!

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
2. Prepare dataset

   We use webdataset to speed up our training process.
   To convert the ImageNet dataset into webdataset format, please run:
   ```
   python imagenet2wds.py -i $IMAGENET_DIR -o $OUTPUT_FOLDER
   ```


3. Train

    ```
    python tools/train.py 
    ```

4. Evaluation

    ```
    python tools/eval.py
    ```
    
## References
- [Mosaic Representation Learning for Self-supervised Visual Pre-training](https://openreview.net/forum?id=JAezPMehaUu)
```
@inproceedings{
wang2023mosaic,
title={Mosaic Representation Learning for Self-supervised Visual Pre-training},
author={Zhaoqing Wang and Ziyu Chen and Yaqian Li and Yandong Guo and Jun Yu and Mingming Gong and Tongliang Liu},
booktitle={The Eleventh International Conference on Learning Representations },
year={2023},
url={https://openreview.net/forum?id=JAezPMehaUu}
}
