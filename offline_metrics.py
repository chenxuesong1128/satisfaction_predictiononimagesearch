# -*- coding: utf-8 -*-
__author__ = 'franky'


from collections import defaultdict
import math
import numpy as np
from scipy import stats
from scipy.stats import t as t_dist
import matplotlib.pyplot as plt


def graded_gain(relevance):
    return math.pow(2, relevance) - 1


def CG(relevance_list):
    metric = 0
    for i in range(len(relevance_list)):
        metric += graded_gain(relevance_list[i])
    return metric


def DCG(relevance_list):
    metric = 0
    for i in range(len(relevance_list)):
        metric += graded_gain(relevance_list[i]) / math.log(i + 2, 2)
    return metric


def DCG_cost(relevance_list):
    return DCG(relevance_list) / len(relevance_list)


def CG_cost(relevance_list):
    return CG(relevance_list) / len(relevance_list)


def nDCG(relevance_list):
    ideal_list = sorted(relevance_list, reverse=True)
    if DCG(ideal_list) == 0:
        return 0
    else:
        return DCG(relevance_list) / DCG(ideal_list)


def ERR(relevance_list):
    metric = 0
    p_sats = []
    for relevance in relevance_list:
        p_sats.append((math.pow(2, relevance) - 1) / float(math.pow(2, 3)))
    for r in range(len(relevance_list)):
        rank = r + 1
        p_dsat = 1
        for j in range(r):
            p_dsat *= (1 - p_sats[j])
        metric += p_dsat * p_sats[r] / float(rank)
        # print r, metric
    return metric


def ERR_cost(relevance_list):
    return ERR(relevance_list) / len(relevance_list)


def DCS(score_list):
    metric = 0
    for i in range(len(score_list)):
        metric += score_list[i] / math.log(i + 2, 2)
    return metric


def nDCS(score_list):
    ideal_list = sorted(score_list, reverse=True)
    if DCS(ideal_list) == 0:
        return 0
    else:
        return DCS(score_list) / DCS(ideal_list)


def RBP(relevance_list, p=0.95):
    metric = 0
    # print type(relevance_list[0])
    for i in range(len(relevance_list)):
        rank = i + 1
        metric += (1 - p) * math.pow(p, rank-1) * (relevance_list[i])
    return metric


def RBP_cost(relevance_list):
    return RBP(relevance_list) / len(relevance_list)


def middle_sort(relevance_list):
    middle_list = []
    middle = int(len(relevance_list) / 2)
    res = len(relevance_list) % 2
    if res == 1:
        middle_list.append(relevance_list[middle])
        for i in range(1, middle+1):
            middle_list.append(relevance_list[middle-i])
            middle_list.append(relevance_list[middle+i])
    else:
        for i in range(middle, len(relevance_list)):
            middle_list.append(relevance_list[len(relevance_list)-i-1])
            middle_list.append(relevance_list[i])
    return middle_list


def metric_2d(list_2d, row_h, column_h):
    row_list = []
    for row in list_2d:
        row_list.append(row_h(row))
    return column_h(row_list)


def compute_r_dep(Y, X, V, func=stats.pearsonr):
    assert(len(X) == len(Y) == len(V))
    rxy = func(X, Y)[0]
    rvy = func(V, Y)[0]
    rxv = func(X, V)[0]
    n = len(Y)
    assert(n > 3)
    diff = rxy - rvy
    t = diff * math.sqrt((n - 3.0) * (1.0 + rxv)) / \
        math.sqrt(2.0 * (1.0 - rxy**2 - rvy**2 - rxv**2 + 2.0 * rxy * rvy * rxv))
    d = 2.0 * t / math.sqrt(n - 3.0)

    p = 2.0 * (1.0 - t_dist.cdf(abs(t), n-3))
    return rxy, rvy, diff, t, p, d

