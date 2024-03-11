# FDTracker in MindSpore

## Introduction
MindSpore is a new generation of full-scenario AI computing framework launched by Huawei in August 2019 and released On March 28, 2020.

FDTrack surpasses the previous state-of-the-art (SOTA) methods and has good anti-interference and real-time performance. FDTrack is extensively tested on the MOT17 and MOT20 benchmarks.Our proposed modules have good portability and can be applied in other one-shot trackers to achieve performance improvement.

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

    For this challenge, the  MOT17 and MOT20.
    
    You can download the dataset from the official site of [MOT challenge](https://motchallenge.net/method/MOT=862&chl=10)

4. Train

    ```
    python tools/train.py 
    ```

5. Evaluation

    ```
    python tools/eval.py
    ```

## Updates
Comming soon!
