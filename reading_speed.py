__author__ = 'Jerry'

from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt


valid_users = ['20160113535', '2016011528', '2016011386', '2016011387', '2016011395', '2016010022', '2016011397',
               '2016011391', '2016011290', '2016011303', '2016011392', '2016010811', '2016011297', '2016011330',
               '2015012820', '2015011753', '2015012610', '2013011818', '2015012739', '2015012630', '2015011759',
               '2015012822', '2015012881', '2015011771', '2015011742', '2015013055', '2015011285', '2015012647',
               '2016211382', '2015012867', '2015011770', '2015011348', '2015011748', '2015012620', '2015011765',
               '2015011727']


def load_sq():
    # user_sqs[user][task_id][query_id] = [['PAGE_START', abs_time], ['JUMP_OUT', abs_time], ['JUMP_IN', abs_time], ['CLICK', url, dwell_time, abs_time, rank], ['HOVER', url, dwell_time, abs_time, rank], ['SCROLL', y1, y2, abs_time], ['PAGE_END', abs_time]]
    user_sqs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    total_num = 0
    for user in valid_users:
        fin = open('./dataset/sq_annot4/' + user, 'r').readlines()
        for line in fin:
            total_num += 1
            items = line.strip().split('\t')
            task_id, query_id, query = items[0].split('-')
            user_sqs[user][task_id][query_id].append([query])
            for action in items[1:]:
                infos = action.split('|')
                name = infos[0]
                if name == 'CLICK' or name == 'HOVER':
                    url = infos[1]
                    time = int(infos[2])
                    abs_time = int(infos[3])
                    rank = int(infos[4])
                    user_sqs[user][task_id][query_id].append([name, url, time, abs_time, rank])
                elif name == 'SCROLL':
                    y1 = float(infos[1])
                    y2 = float(infos[2])
                    abs_time = int(infos[3])
                    user_sqs[user][task_id][query_id].append([name, y1, y2, abs_time])
                else:
                    abs_time = int(infos[1])
                    user_sqs[user][task_id][query_id].append([name, abs_time])

    print(total_num)
    return user_sqs


def count_two_clicks_in_a_row(user_sqs):
    total = 0
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                sequence_click = 0
                for action in sequence:
                    if action[0] == 'CLICK':
                        sequence_click += 1
                if sequence_click >= 2:
                    total += 1
    return total


if __name__ == '__main__':
    user_sqs = load_sq()
    two_clicks_in_a_row_num = count_two_clicks_in_a_row(user_sqs)
    print(two_clicks_in_a_row_num)