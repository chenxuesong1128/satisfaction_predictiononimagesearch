# -*- coding: utf-8 -*-
__author__ = 'franky'

import pandas as pd
import seaborn as sns
from collections import defaultdict
import math
import numpy as np
from scipy import stats
from scipy.stats import t as t_dist
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
# import sys
# from importlib import reload
# reload(sys)
# import importlib,sys
# importlib.reload(sys)
# sys.setdefaultencoding('utf-8')
from scipy.stats import chi2_contingency
from sklearn import metrics
from offline_metrics import *


def load_query_satisfaction(filename='./dataset/query_satisfaction1119.csv'):
    # query_satisfaction[task_id][user][query_id] = satisfaction
    satisfaction_dict = defaultdict(lambda: defaultdict(lambda: {}))
    fin = open(filename).readlines()[1:]
    # explore e.g.You want to know some information about Los Angelas (e.g. streets, landscapes, buildings).
    # Entertaining e.g. You want to browse some posters or photos of your favorite stars to kill time.
    # Locating e.g. You need to make a slide about Harry Potter film to introduce the protagonists.
    Exp, Ent, Loc = 0, 0, 0
    for line in fin:
        user, task_id, query_id, query, satisfaction = line.strip().split(',')
        satisfaction_dict[task_id][user][query_id] = int(satisfaction)  # satisfaction from 1
        if 1 <= int(task_id) <= 4:
            Exp += 1
        if 5 <= int(task_id) <= 8:
            Ent += 1
        if 9 <= int(task_id) <= 12:
            Loc += 1
    print("num of Explore:", Exp)
    print("num of Entertainment:",Ent)
    print("num of locating", Loc)
    return satisfaction_dict


def load_results(filename='./dataset/results_judgments.tsv'):
    satisfaction_dict = load_query_satisfaction()
    # results_dict[task_id][user][query_id][row] = results_list
    results_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))))
    fin = open(filename).readlines()[1:]
    i = 0
    for line in fin:
        user, task_id, query_id, query, list_id, rank, url, relevance, quality, combination, description, row, column, top, left, width, height, color = line.strip().split('\t')
        if int(row) < 10 and task_id in satisfaction_dict and user in satisfaction_dict[task_id] and query_id in satisfaction_dict[task_id][user]:
            result = {
                'rank': int(rank),
                'relevance': int(relevance),
                'quality': int(quality),
                'combination': int(combination),
                'row': int(row),
                'column': int(column),
                'top': float(top),
                'left': float(left),
                'width': float(width),
                'height': float(height)
            }
            results_dict[task_id][user][query_id][int(row)].append(result)
            i += 1
    print("load results: ", i)
    return satisfaction_dict, results_dict


def plt_marginal_distribution(relevance_distribution, quality_distribution, figname='./fig/marginal_distribution.pdf'):
    N = 2
    ind = np.arange(N)  # the x locations for the groups
    width = 0.20       # the width of the bars

    fig, ax = plt.subplots()
    font = FontProperties()
    font.set_family('Times New Roman')

    means0 = (relevance_distribution[0], quality_distribution[0])
    rects0 = ax.bar(ind, means0, width, color='#FFFF99')

    means1 = (relevance_distribution[1], quality_distribution[1])
    rects1 = ax.bar(ind + width, means1, width, color='#FFCCCC')

    means2 = (relevance_distribution[2], quality_distribution[2])
    rects2 = ax.bar(ind + 2*width, means2, width, color='#FFCC99')

    means3 = (relevance_distribution[3], quality_distribution[3])
    rects3 = ax.bar(ind + 3*width, means3, width, color='#CCCCFF')

    # add some text for labels, title and axes ticks
    ax.set_xticks(ind + width * 1.5)
    ax.set_xticklabels((r'$Topical\ Relevance$', r'$Image\ Quality$'))
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    ax.legend((rects0[0], rects1[0], rects2[0], rects3[0]), ('$0$', '$1$', '$2$', '$3$'), fontsize=16)
    plt.savefig(figname)


def plt_joint_distribution(joint_distributions, figname='./fig/joint_distribution.pdf'):
    fig = plt.figure()
    ax = fig.gca()
    im = ax.imshow(joint_distributions, cmap='Blues')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    ax.set_xticks((0, 1, 2, 3))
    ax.set_xticklabels((0, 1, 2, 3))
    ax.set_xlabel(r'$Topical\ Relevance$', fontsize=16)
    ax.set_yticks((0, 1, 2, 3))
    ax.set_yticklabels((3, 2, 1, 0))
    ax.set_ylabel(r'$Image\ Quality$', fontsize=16)
    fig.colorbar(im, ax=ax)
    plt.savefig(figname)


def relevance_quality():
    satisfaction_dict, results_dict = load_results()
    relevance_number = np.zeros(4)
    quality_number = np.zeros(4)
    joint_numbers = {
        'All': np.zeros((4, 4)),
        'Exp': np.zeros((4, 4)),
        'Ent': np.zeros((4, 4)),
        'Loc': np.zeros((4, 4)),
    }
    relevance_list = []
    quality_list = []
    for task_id in results_dict:
        for user in results_dict[task_id]:
            for query_id in results_dict[task_id][user]:
                for row in results_dict[task_id][user][query_id]:
                    for result in results_dict[task_id][user][query_id][row]:
                        relevance = result['relevance']
                        quality = result['quality']
                        combination = result['combination']
                        relevance_list.append(relevance)
                        quality_list.append(quality)
                        relevance_number[int(relevance)] += 1
                        quality_number[int(quality)] += 1
                        joint_numbers['All'][3-int(quality)][int(relevance)] += 1
                        if 1 <= int(task_id) <= 4:
                            joint_numbers['Exp'][3-int(quality)][int(relevance)] += 1
                        if 5 <= int(task_id) <= 8:
                            joint_numbers['Ent'][3-int(quality)][int(relevance)] += 1
                        if 9 <= int(task_id) <= 12:
                            joint_numbers['Loc'][3-int(quality)][int(relevance)] += 1
    relevance_distribution = relevance_number / relevance_number.sum()
    quality_distribution = quality_number / quality_number.sum()
    print(chi2_contingency(np.array([relevance_number, quality_number])), relevance_number.sum())
    # print(chi2_contingency(np.array([relevance_number, quality_number])))

    plt_marginal_distribution(relevance_distribution, quality_distribution)
    print(metrics.cohen_kappa_score(relevance_list, quality_list, weights='linear'))
    print(metrics.cohen_kappa_score(relevance_list, quality_list, weights='quadratic'))
    print(stats.pearsonr(relevance_list, quality_list))

    for type in joint_numbers:
        print(type, joint_numbers[type].sum())
        joint_distributions = joint_numbers[type] / joint_numbers[type].sum()
        plt_joint_distribution(joint_distributions, figname='./fig/joint_distribution_' + type + '.pdf')


    # 不同的query的topical relevance
    plt.figure()
    different_query_quality_num = {
        'All': np.zeros(4),
        'Exp': np.zeros(4),
        'Ent': np.zeros(4),
        'Loc': np.zeros(4),
    }
    different_query_relevance_num = {
        'All': np.zeros(4),
        'Exp': np.zeros(4),
        'Ent': np.zeros(4),
        'Loc': np.zeros(4),
    }
    for type in joint_numbers:
        different_query_quality_num[type] = np.sum(joint_numbers[type], 1)
        different_query_relevance_num[type] = np.sum(joint_numbers[type], 0)

    tmp_diff_query_quality_num = different_query_quality_num
    for i in range(3):
        different_query_quality_num[type][i] = tmp_diff_query_quality_num[type][3 - i]
    prct_different_query_relevance_num = {

    }
    for type in joint_numbers:
        prct_different_query_relevance_num[type] = different_query_relevance_num[type] / np.sum(different_query_relevance_num[type])
    size = 4
    x = np.arange(size)

    total_width, n = 0.8, 3  # 有多少个类型，只需更改n即可
    width = total_width / n
    x = x - (total_width - width) / 2

    # plt.bar(x, different_query_quality_num['All'], width=width, label='quality=0')
    plt.bar(x, prct_different_query_relevance_num['Exp'], width=width, label='explore')
    plt.bar(x + width, prct_different_query_relevance_num['Ent'], width=width, label='entertainment')
    plt.bar(x + 2 * width, prct_different_query_relevance_num['Loc'], width=width, label='locate')
    plt.xticks([0, 1, 2, 3], ['0', '1', '2', '3'])
    plt.xlabel('relevant score')
    plt.ylabel('percent')
    plt.legend()
    plt.show()
    # plt.pause(5)
    plt.close()


    # 展示不同查询类型分数的占比
    # relevence
    pie_lable = ['0', '1', '2', '3']
    plt.figure(figsize=(8, 8), num=8)
    plt.axes()
    pos_of_fig = 221
    for type in joint_numbers:
        # plt.figure()
        ax = plt.subplot(pos_of_fig)
        plt.title(type)
        # plt.subplot(pos_of_fig)
        pos_of_fig += 1
        ax.pie(x=different_query_relevance_num[type], labels=pie_lable, autopct='%3.1f %%',
                shadow=False, labeldistance=1.1, startangle=90, pctdistance=0.6
                )
    plt.show()



    # 展示不同查询类型分数的占比
    # quantity
    pie_lable = ['0', '1', '2', '3']
    plt.figure(figsize=(8, 8), num=8)
    plt.axes()
    pos_of_fig = 221
    for type in joint_numbers:
        # plt.figure()
        ax = plt.subplot(pos_of_fig)
        plt.title(type)
        # plt.subplot(pos_of_fig)
        pos_of_fig += 1
        ax.pie(x=different_query_quality_num[type], labels=pie_lable, autopct='%3.1f %%',
                shadow=False, labeldistance=1.1, startangle=90, pctdistance=0.6
                )
    plt.show()


def different_judgments():
    satisfaction_dict, results_dict = load_results()
    satisfaction_list = []
    # metrics_list[judgment][metric] = []
    metrics_list = defaultdict(lambda: defaultdict(lambda: []))
    metric_map = {
        'CG': CG_cost,
        'DCG': DCG_cost,
        'RBP': RBP_cost,
        'ERR': ERR_cost
    }
    for task_id in satisfaction_dict:
        for user in satisfaction_dict[task_id]:
            for query_id in satisfaction_dict[task_id][user]:
                satisfaction_list.append(satisfaction_dict[task_id][user][query_id])

                results_rows = results_dict[task_id][user][query_id]
                judgments_list = {
                    'relevance': [],
                    'quality': [],
                    'combination': []
                }
                for row in range(10):
                    if row in results_rows:
                        results = results_rows[row]
                        for judgment in judgments_list:
                            judgments_list[judgment] += [item[judgment] for item in results]
                for judgment in judgments_list:
                    for metric in metric_map:
                        score = metric_map[metric](judgments_list[judgment])
                        metrics_list[judgment][metric].append(score)
    fout = open('./results/different_judgments.csv', 'w')
    fout.write('Metrics,TR,IQ,CR\n')
    for metric in ['CG', 'DCG', 'RBP', 'ERR']:
        fout.write(metric)
        for judgment in ['relevance', 'quality', 'combination']:
            fout.write(',')
            r, p = stats.pearsonr(satisfaction_list, metrics_list[judgment][metric])
            fout.write(str(round(r, 3)))
            # if p < 0.01:
            #     fout.write('*')
            if p < 0.001:
                fout.write('*')
        fout.write('\n')


def different_sequence():
    satisfaction_dict, results_dict = load_results()
    satisfaction_list = []
    # metrics_list[sequence][metric] = []
    metrics_list = defaultdict(lambda: defaultdict(lambda: []))
    metric_map = {
        'CG': CG_cost,
        'DCG': DCG_cost,
        'RBP': RBP_cost,
        'ERR': ERR_cost,
        'MAX': np.max,
        'AVG': np.mean
    }
    for task_id in satisfaction_dict:
        for user in satisfaction_dict[task_id]:
            for query_id in satisfaction_dict[task_id][user]:
                satisfaction_list.append(satisfaction_dict[task_id][user][query_id])

                results_rows = results_dict[task_id][user][query_id]
                sequences_list = {
                    'Z': [],
                    'T': [],
                    'S': []
                }
                for row in range(10):
                    if row in results_rows:
                        results = results_rows[row]
                        relevances = [item['combination'] for item in results]
                        sequences_list['Z'] += relevances
                        sequences_list['T'] += middle_sort(relevances)
                        relevances.reverse()
                        sequences_list['S'] += relevances
                for sequence in sequences_list:
                    for metric in metric_map:
                        score = metric_map[metric](sequences_list[sequence])
                        metrics_list[sequence][metric].append(score)
    fout = open('./results/different_sequences.csv', 'w')
    fout.write('Metrics,Z,T,S\n')
    for metric in ['CG', 'DCG', 'RBP', 'ERR', 'MAX', 'AVG']:
        fout.write(metric)
        for sequence in ['Z', 'T', 'S']:
            fout.write(',')
            r, p = stats.pearsonr(satisfaction_list, metrics_list[sequence][metric])
            fout.write(str(round(r, 3)))
            # if p < 0.01:
            #     fout.write('*')
            if p < 0.001:
                fout.write('*')
        fout.write('\n')


def two_dim_metrics():
    satisfaction_dict, results_dict = load_results()
    satisfaction_list = []
    # metrics_list[row_base][metric] = []
    metrics_list = defaultdict(lambda: defaultdict(lambda: []))
    metric_map = {
        'CG': np.sum,
        'DCG': DCS,
        'RBP': RBP,
        'ERR': ERR,
        'MAX': np.max,
        'AVG': np.mean
    }
    row_base_map = {
        'SUM': np.sum,
        'MAX': np.max,
        'AVG': np.mean
    }
    for task_id in satisfaction_dict:
        for user in satisfaction_dict[task_id]:
            for query_id in satisfaction_dict[task_id][user]:
                satisfaction_list.append(satisfaction_dict[task_id][user][query_id])

                results_rows = results_dict[task_id][user][query_id]
                relevances_list_2d = []
                for row in range(10):
                    if row in results_rows:
                        results = results_rows[row]
                        relevances = [item['combination'] for item in results]
                        relevances_list_2d.append(relevances)
                for row_base in row_base_map:
                    for metric in metric_map:
                        score = metric_2d(relevances_list_2d, row_base_map[row_base], metric_map[metric])
                        metrics_list[row_base][metric].append(score)
    fout = open('./results/2d_metrics.csv', 'w')
    fout.write('Metrics,SUM,MAX,AVG\n')
    for metric in ['CG', 'DCG', 'RBP', 'ERR', 'MAX', 'AVG']:
        fout.write(metric)
        for sequence in ['SUM', 'MAX', 'AVG']:
            fout.write(',')
            r, p = stats.pearsonr(satisfaction_list, metrics_list[sequence][metric])
            fout.write(str(round(r, 3)))
            # if p < 0.01:
            #     fout.write('*')
            if p < 0.001:
                fout.write('*')
        fout.write('\n')


# 比较前10行，在用户标注的情况下是否存在差异
# 设计参数产生衰减

def cmp_top10():
    satisfaction_dict, results_dict = load_results()

    #########################
    #   计算满意度修改内容
    #########################
    distribution_2d = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: np.zeros((10, 13), dtype=float))))
    num_of_distribution = defaultdict(lambda: defaultdict(lambda: 0))
    # distribution_2d = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
    query_type_list = ['All', 'Exp', 'Ent', 'Loc']
    judgement_list = ['relevance', 'quality', 'combination']
    # map_num2name = {
    #     '11':0,
    #     '12':1,
    #     '13':2,
    #     '14':3,
    #     '15':4,
    # }
    # heat_map = np.zeros(10, 12)
    for task_id in results_dict:
        for user in results_dict[task_id]:
            for query_id in results_dict[task_id][user]:

                ######################
                #   计算满意度添加内容
                ######################
                if 1 <= int(task_id) <= 4:
                    query_type_id = 1
                if 5 <= int(task_id) <= 8:
                    query_type_id = 2
                if 9 <= int(task_id) <= 12:
                    query_type_id = 3
                satisfaction_score = satisfaction_dict[task_id][user][query_id]

                for row in results_dict[task_id][user][query_id]:
                    for result in results_dict[task_id][user][query_id][row]:
                        column_index = result['column']
                        if column_index > 8:
                            continue
                        for judgement in judgement_list:
                            # distribution_2d['all']['combine'][int(row)][0] = 3
                            # print(type(judgement), judgement)


                            #######################
                            #    计算满意度修改内容
                            #######################
                            distribution_2d['All'][judgement][satisfaction_score][int(row)][int(column_index)] += result[judgement]
                            distribution_2d[query_type_list[query_type_id]][judgement][satisfaction_score][int(row)][int(column_index)] += int(result[judgement])
                            distribution_2d['All'][judgement][satisfaction_score+5][int(row)][int(column_index)] += 1
                            distribution_2d[query_type_list[query_type_id]][judgement][satisfaction_score+5][int(row)][int(column_index)] += 1

                            # distribution_2d['All'][judgement][satisfaction_score][int(row)][int(column_index)] += result[judgement]
                            # distribution_2d[query_type_list[query_type_id]][judgement][satisfaction_score][int(row)][int(column_index)] += int(result[judgement])

                # num_of_distribution['All'][satisfaction_score] += 1
                # num_of_distribution[query_type_list[query_type_id]][satisfaction_score] += 1

    # print(distribution_2d['Exp']['relevance'])

    # normalization
    for query_type in ['All']:
        for judgement in judgement_list:
            for satisfaction_score in [1, 2, 3, 4, 5]:
                distribution_2d[query_type][judgement][satisfaction_score + 5] = np.where(distribution_2d[query_type][judgement][satisfaction_score+5] > 5, distribution_2d[query_type][judgement][satisfaction_score+5], 0)
                distribution_2d[query_type][judgement][satisfaction_score] = np.divide(distribution_2d[query_type][judgement][satisfaction_score], distribution_2d[query_type][judgement][satisfaction_score+5])
                plt.figure(figsize=(10, 9), dpi=100)
                # distribution_2d[query_type][judgement][satisfaction_score] = np.delete(distribution_2d[query_type][judgement][satisfaction_score], [1, 2, 3],
                #                                                    axis=1)
                df = pd.DataFrame(distribution_2d[query_type][judgement][satisfaction_score])
                sns.set(font_scale=1.8)
                ax = sns.heatmap(df, annot=False, vmin=0.5, vmax=3)
                if judgement == 'relevance':
                    title_item = 'Topical Relevance'
                if judgement == 'quality':
                    title_item = 'Image Quality'
                fig_title = str(title_item) + '=' + str(satisfaction_score)
                ax.set_title(fig_title)
                plt.savefig(fig_title + '.pdf')


            # *****************
            # 不计算满意度的情况下
            # *****************
            # plt.figure()
            # distribution_2d[query_type][judgement] = np.delete(distribution_2d[query_type][judgement], [1, 2, 3], axis=1)
            # df = pd.DataFrame(distribution_2d[query_type][judgement])
            # ax = sns.heatmap(df, annot=False, fmt='d', vmin=10)
            # ax.set_title(query_type+'_'+judgement)
            # plt.savefig(query_type+'_' + judgement+'.png')
            ## plt.savefig("../fig/"+query_type+"_" + judgement+".png")
            ## plt.show()





if __name__ == "__main__":
    # relevance_quality()
    # different_judgments()
    # different_sequence()
    # two_dim_metrics()
    cmp_top10()

# if 1 <= int(task_id) <= 4:
#     query_type = 'relevance'
# if 5 <= int(task_id) <= 8:
#     query_type = 'quality'
# if 9 <= int(task_id) <= 12:
#     query_type = 'combine'
# for judgement in judgement_list:
#     distribution_2d[query_type][judgement][row][result['column']] = result[judgement]
