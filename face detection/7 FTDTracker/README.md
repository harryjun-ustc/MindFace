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

    For this challenge, the MOT17 and MOT20 dataset is used.
    
    You can download the dataset from the official site of [MOT challenge](https://motchallenge.net/)

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

## References
- [Multi-Object Tracking: Decoupling Features to Solve the Contradictory Dilemma of Feature Requirements](https://ieeexplore.ieee.org/abstract/document/10053999)
```
@ARTICLE{10053999,
  author={Jin, Yan and Gao, Fang and Yu, Jun and Wang, Jiabao and Shuang, Feng},
  journal={IEEE Transactions on Circuits and Systems for Video Technology}, 
  title={Multi-Object Tracking: Decoupling Features to Solve the Contradictory Dilemma of Feature Requirements}, 
  year={2023},
  volume={33},
  number={9},
  pages={5117-5132},
  keywords={Feature extraction;Target tracking;Task analysis;Training;Data models;Video sequences;Trajectory;Multi-object tracking;decoupling by mutual inhibition;data association;one-shot model;ReID-based tracker},
  doi={10.1109/TCSVT.2023.3249162}}
