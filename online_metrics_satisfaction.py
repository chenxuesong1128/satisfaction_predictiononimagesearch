# -*- coding: utf-8 -*-
__author__ = 'franky'


from collections import defaultdict
import math
import numpy as np
from scipy import stats
from scipy.stats import t as t_dist
import matplotlib.pyplot as plt
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

valid_users = ['20160113535', '2016011528', '2016011386', '2016011387', '2016011395', '2016010022', '2016011397',
               '2016011391', '2016011290', '2016011303', '2016011392', '2016010811', '2016011297', '2016011330',
               '2015012820', '2015011753', '2015012610', '2013011818', '2015012739', '2015012630', '2015011759',
               '2015012822', '2015012881', '2015011771', '2015011742', '2015013055', '2015011285', '2015012647',
               '2016211382', '2015012867', '2015011770', '2015011348', '2015011748', '2015012620', '2015011765',
               '2015011727']


def load_sq():
    # user_sqs[user][task_id][query_id] = [['PAGE_START', abs_time], ['JUMP_OUT', abs_time], ['JUMP_IN', abs_time], ['CLICK', url, dwell_time, abs_time, rank], ['HOVER', url, dwell_time, abs_time, rank], ['SCROLL', y1, y2, abs_time], ['PAGE_END', abs_time]]
    user_sqs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    for user in valid_users:
        fin = open('./dataset/sq_annot/' + user, 'r').readlines()
        for line in fin:
            items = line.strip().split('\t')
            task_id, query_id, query = items[0].split('-')
            for action in items[1:]:
                infos = action.split('|')
                name = infos[0]
                if name == 'CLICK' or name == 'HOVER':
                    url = infos[1]
                    time = int(infos[2])
                    abs_time = int(infos[3])
                    rank = int(infos[4])
                    # print(type(user_sqs[user][task_id][query_id]))
                    user_sqs[user][task_id][query_id].append([name, url, time, abs_time, rank])
                elif name == 'SCROLL':
                    y1 = float(infos[1])
                    y2 = float(infos[2])
                    abs_time = int(infos[3])
                    user_sqs[user][task_id][query_id].append([name, y1, y2, abs_time])
                else:
                    abs_time = int(infos[1])
                    user_sqs[user][task_id][query_id].append([name, abs_time])
    return user_sqs


def load_results(filename='./dataset/results_judgments.tsv'):
    results_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {})))
    fin = open(filename).readlines()[1:]
    i = 0
    for line in fin:
        user, task_id, query_id, query, list_id, rank, url, relevance, quality, combination, description, row, column, top, left, width, height, color = line.strip().split('\t')
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
        results_dict[user][task_id][query_id][int(rank)] = result
        i += 1
    print('load results: ', i)
    return results_dict


def online_metrics(user_sqs, results):
    fout = open('./results/online_metrics_franky.csv', 'w')
    fout.write('user,task_id,query_id,UCTR,QCTR,MaxRR,MinRR,MeanRR,MaxRRow,MinRRow,MeanRRow,PLC,MaxScroll,QDT,SCD,ACD,TTFC,TTLC,DsatCC,DsatCR\n')
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                # user_sqs[user][task_id][query_id] = [['PAGE_START', abs_time], ['JUMP_OUT', abs_time], ['JUMP_IN', abs_time], ['CLICK', url, dwell_time, abs_time, rank], ['HOVER', url, dwell_time, abs_time, rank], ['SCROLL', y1, y2, abs_time], ['PAGE_END', abs_time]]
                sequence = user_sqs[user][task_id][query_id]
                results_dict = results[user][task_id][query_id]
                # print user, task_id, query_id

                click_Rranks = []
                lowest_click = 0.0
                click_Rrows = []
                row_click = 1
                hover_Rranks = []
                lowest_hover = 0.0
                hover_Rrows = []
                row_hover = 1
                clickandhover_Rranks = []
                lowest_clickandhover = 0.0
                clickandhover_Rrows = []
                row_clickandhover = 1
                MaxScroll = 0.0
                Scroll = 0.0

                Query_start_time = 0
                Query_end_time = 0
                last_jumpout_time = 0
                jumpouts_dwell_time = []
                clicks_dwell = []
                clicks_rel_time = []
                hovers_dwell = []
                hovers_rel_time = []
                clickandhovers_dwell = []
                clickandhovers_rel_time = []

                for action in sequence:
                    if action[0] == 'PAGE_START':
                        if Query_start_time == 0:
                            Query_start_time = action[1]
                    if action[0] == 'PAGE_END':
                        Query_end_time = action[1]
                    if action[0] == 'JUMP_OUT':
                        Query_end_time = action[1]
                        last_jumpout_time = action[1]
                    if action[0] == 'JUMP_IN':
                        Query_end_time = action[1]
                        jumpouts_dwell_time.append(action[1] - last_jumpout_time)
                    if action[0] == 'SCROLL':
                        Query_end_time = action[3]
                        y = action[2] - action[1]
                        Scroll += y
                        if Scroll > MaxScroll:
                            MaxScroll = Scroll
                    if action[0] == 'CLICK':
                        # if int(user) == 20160113535 and int(task_id) == 1 and int(query_id) == 1:
                            # print(user, task_id, query_id)
                        Query_end_time = action[3]
                        dwell_time = action[2]
                        abs_time = action[3]
                        clicks_dwell.append(dwell_time)
                        clicks_rel_time.append(abs_time-Query_start_time)
                        clickandhovers_dwell.append(dwell_time)
                        clickandhovers_rel_time.append(abs_time-Query_start_time)
                        rank = action[4]
                        click_Rranks.append(1.0 / (rank+1))
                        clickandhover_Rranks.append(1.0 / (rank+1))
                        result = results_dict[rank]
                        y = result['top']
                        if int(user) == 20160113535 and int(task_id) == 1 and int(query_id) == 0:
                            print('y' + str(y))
                        row = int(result['row'])
                        click_Rrows.append(1.0 / (row+1))
                        clickandhover_Rrows.append(1.0 / (row+1))
                        if y > lowest_click:
                            lowest_click = y
                        if row + 1 > row_click:
                            row_click = row + 1
                        if y > lowest_clickandhover:
                            lowest_clickandhover = y
                        if row + 1 > row_clickandhover:
                            row_clickandhover = row + 1
                    if action[0] == 'HOVER':
                        Query_end_time = action[3]
                        dwell_time = action[2]
                        abs_time = action[3]
                        hovers_dwell.append(dwell_time)
                        hovers_rel_time.append(abs_time-Query_start_time)
                        clickandhovers_dwell.append(dwell_time)
                        clickandhovers_rel_time.append(abs_time-Query_start_time)
                        rank = action[4]
                        hover_Rranks.append(1.0 / (rank+1))
                        clickandhover_Rranks.append(1.0 / (rank+1))
                        result = results_dict[rank]
                        y = result['top']
                        row = int(result['row'])
                        hover_Rrows.append(1.0 / (row+1))
                        clickandhover_Rrows.append(1.0 / (row+1))
                        if y > lowest_hover:
                            lowest_hover = y
                        if row + 1 > row_hover:
                            row_hover = row + 1
                        if y > lowest_clickandhover:
                            lowest_clickandhover = y
                        if row + 1 > row_clickandhover:
                            row_clickandhover = row + 1

                UCTR = 0
                QCTR = len(click_Rranks)
                # QCTR = len(clickandhover_Rranks)
                MaxRR = 0
                MinRR = 0
                MeanRR = 0
                PLC = 0
                MaxRRow = 0
                MinRRow = 0
                MeanRRow = 0
                RLC = 0
                UHTR = 0
                QHTR = len(hover_Rranks)
                MaxHRRank = 0
                MinHRRank = 0
                MeanHRRank = 0
                PLH = 0
                MaxHRRow = 0
                MinHRRow = 0
                MeanHRRow = 0
                RLH = 0
                if click_Rranks:
                    UCTR = 1
                    MaxRR = np.max(click_Rranks)
                    MinRR = np.min(click_Rranks)
                    MeanRR = np.mean(click_Rranks)
                    PLC = QCTR / lowest_click
                    MaxRRow = np.max(click_Rrows)
                    MinRRow = np.min(click_Rrows)
                    MeanRRow = np.mean(click_Rrows)
                    RLC = QCTR / row_click
                # if clickandhover_Rranks:
                #     UCTR = 1
                #     MaxRR = np.max(clickandhover_Rranks)
                #     MinRR = np.min(clickandhover_Rranks)
                #     MeanRR = np.mean(clickandhover_Rranks)
                #     PLC = QCTR / lowest_clickandhover
                #     MaxRRow = np.max(clickandhover_Rrows)
                #     MinRRow = np.min(clickandhover_Rrows)
                #     MeanRRow = np.mean(clickandhover_Rrows)
                #     RLC = QCTR / row_clickandhover
                if hover_Rranks:
                    UHTR = 1
                    MaxHRRank = np.max(hover_Rranks)
                    MinHRRank = np.min(hover_Rranks)
                    MeanHRRank = np.mean(hover_Rranks)
                    PLH = QHTR / lowest_hover
                    MaxHRRow = np.max(hover_Rrows)
                    MinHRRow = np.min(hover_Rrows)
                    MeanHRRow = np.mean(hover_Rrows)
                    RLH = QHTR / row_hover

                QDT = Query_end_time - Query_start_time
                SDT = QDT - np.sum(jumpouts_dwell_time)
                SCD = 0
                ACD = 0
                TTFC = 2000000
                TTLC = 2000000
                DsatCC = 0
                DsatCR = 0
                click_threshold = 15000
                SHD = 0
                AHD = 0
                TTFH = 2000000
                TTLH = 2000000
                DsatHC = 0
                DsatHR = 0
                hover_threshold = 5000
                if clicks_dwell:
                    SCD = np.sum(clicks_dwell)
                    ACD = np.mean(clicks_dwell)
                    TTFC = clicks_rel_time[0]
                    TTLC = clicks_rel_time[-1]
                    for dwell in clicks_dwell:
                        if dwell < click_threshold:
                            DsatCC += 1
                    DsatCR = DsatCC / len(clicks_dwell)
                # if clickandhovers_dwell:
                #     SCD = np.sum(clickandhovers_dwell)
                #     ACD = np.mean(clickandhovers_dwell)
                #     TTFC = clickandhovers_rel_time[0]
                #     TTLC = clickandhovers_rel_time[-1]
                #     for dwell in clickandhovers_dwell:
                #         if dwell < click_threshold:
                #             DsatCC += 1
                #     DsatCR = DsatCC / len(clickandhovers_dwell)
                if hovers_dwell:
                    SHD = np.sum(hovers_dwell)
                    AHD = np.mean(hovers_dwell)
                    TTFH = hovers_rel_time[0]
                    TTLH = hovers_rel_time[-1]
                    for dwell in hovers_dwell:
                        if dwell < hover_threshold:
                            DsatHC += 1
                    DsatHR = DsatHC / len(hovers_dwell)

                fout.write(','.join(str(item) for item in [user,task_id,query_id,UCTR,QCTR,MaxRR,MinRR,MeanRR,MaxRRow,MinRRow,MeanRRow,PLC,MaxScroll,QDT,SCD,ACD,TTFC,TTLC,DsatCC,DsatCR]))
                # fout.write(','.join(str(item) for item in [user,task_id,query_id,UHTR,QHTR,MaxHRRank,MinHRRank,MeanHRRank,MaxHRRow,MinHRRow,MeanHRRow,PLH,MaxScroll,QDT,SHD,AHD,TTFH,TTLH,DsatHC,DsatHR]))
                fout.write('\n')
    fout.close()


def query_satisfaction():
    f_metrics = open('./results/online_metrics_all_hover.csv', 'r').readlines()
    f_satisfaction = open('./dataset/query_satisfaction.csv', 'r').readlines()
    satisfaction_dict = defaultdict(lambda: defaultdict(lambda: {}))
    for line in f_satisfaction[1:]:
        user,task_id,query_id,query,satisfaction = line.strip().split(',')
        satisfaction_dict[user][task_id][query_id] = int(satisfaction)
    i = 0
    for user in satisfaction_dict:
        for task_id in satisfaction_dict[user]:
            i += 1
    print(i)

    satisfaction_list = []
    online_metric_list = defaultdict(lambda: [])
    metrics = f_metrics[0].strip().split(',')[2:]
    for line in f_metrics[1:]:
        items = line.strip().split(',')
        user = items[0]
        task_id = items[1]
        query_id = items[2]
        metric_scores = items[2:]
        # print(user, task_id, query_id)
        satisfaction_list.append(satisfaction_dict[user][task_id][query_id])
        for i in range(len(metrics)):
            online_metric_list[metrics[i]].append(float(metric_scores[i]))
    fout = open('./results/cxs_online_metrics_satisfaction.csv', 'w')
    for i in range(len(metrics)):
        print(metrics[i], stats.pearsonr(online_metric_list[metrics[i]], satisfaction_list))
        if stats.pearsonr(online_metric_list[metrics[i]], satisfaction_list)[1] < 0.001:
            fout.write(metrics[i] + ',' + str(round(stats.pearsonr(online_metric_list[metrics[i]], satisfaction_list)[0], 3))+'*')
        else:
            fout.write(metrics[i] + ',' + str(round(stats.pearsonr(online_metric_list[metrics[i]], satisfaction_list)[0], 3)))
        fout.write('\n')

    # self define
    print(metrics[14], metrics[18], stats.pearsonr(online_metric_list[metrics[14]], online_metric_list[metrics[18]]))
    print(metrics[11], metrics[18], stats.pearsonr(online_metric_list[metrics[11]], online_metric_list[metrics[18]]))
    print(metrics[11], metrics[14], stats.pearsonr(online_metric_list[metrics[11]], online_metric_list[metrics[14]]))
    fout.close()


if __name__ == "__main__":
    # user_sqs = load_sq()
    # results = load_results()
    # online_metrics(user_sqs, results)
    query_satisfaction()

