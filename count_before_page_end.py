# coding:utf-8
# __author__ = 'Jerry'


##########################
# 在用户page end之前的动作是什么，两个动作之间的时间差距，对于用户满意度的预测的关系的探究
##########################

from prepared_functions import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.font_manager import FontProperties


valid_users = get_valid_users()
satisfaction_dict = load_query_satisfaction()
satisfaction_lever_gap_time = defaultdict(lambda: defaultdict(lambda: []))

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def get_before_page_end_action_and_gap_time(user_sqs, valid_users):

    case_num = 0
    extra_case = defaultdict(lambda: [])

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                page_end_time = sequence[len(sequence) - 1][1]
                last_action = sequence[len(sequence) - 2][0]
                satisfaction_lever = satisfaction_dict[task_id][user][query_id]
                extra_case[satisfaction_lever].append(last_action)

    return extra_case


if __name__ == "__main__":

    dataset = './dataset/f_remove_jump_before_click/'
    user_sqs, total_num = load_sq(dataset)
    print("case num: ", total_num)
    satisfaction_lever_percent_action = np.zeros((6, 6))
    satisfaction_lever_percent_satisfaction = np.zeros((6, 6), float)
    statics = get_before_page_end_action_and_gap_time(user_sqs, valid_users)
    action_list = ['PAGE_START', 'SCROLL',
                   'CLICK', 'HOVER', 'JUMP_IN', 'JUMP_OUT']
    for satisfaction_lever in [1, 2, 3, 4, 5]:
        for action in action_list:
            index = action_list.index(action)
            satisfaction_lever_percent_action[satisfaction_lever][index] = statics[satisfaction_lever].count(
                action)/len(statics[satisfaction_lever])

    sum_action = np.zeros(6)
    for action in action_list:
        for satisfaction_lever in [1, 2, 3, 4, 5]:
            index = action_list.index(action)
            sum_action[index] += statics[satisfaction_lever].count(action)

    for action in action_list:
        for satisfaction_lever in [1, 2, 3, 4, 5]:
            index = action_list.index(action)
            if sum_action[index] != 0:
                satisfaction_lever_percent_satisfaction[index][satisfaction_lever] = statics[satisfaction_lever].count(
                    action) / sum_action[index]

    satisfaction_list = [1, 2, 3, 4, 5]
    pd_action_list = ['PAGE_START', 'SCROLL', 'HOVER', 'JUMP_IN', 'JUMP_OUT']
    heat_map_pd = pd.DataFrame(index=satisfaction_list, columns=pd_action_list)
    used_data = np.zeros((5, 5))
    transform_i = 1
    # for sat_i in satisfaction_list:
    #     for act_i in pd_action_list:
    #         heat_map_pd.loc[sat_i][act_i] = satisfaction_lever_percent_action[sat_i][transform_i]
    #         transform_i += 1
    #         if transform_i == 2:
    #             transform_i += 1
    #     transform_i = 0
    for sat_i in range(5):
        tmp_i = 0
        for act_i in range(5):
            used_data[sat_i][act_i] = satisfaction_lever_percent_action[sat_i+1][tmp_i]
            tmp_i += 1
            if tmp_i == 2:
                tmp_i += 1

    font = FontProperties()
    font.set_family('Times New Roman')
    plt.figure(figsize=(10, 9), dpi=100)
    cmap = sns.color_palette("Blues")
    ax = sns.heatmap(used_data, annot=True, cmap=cmap)
    # fig_title = 'distribution of last action before page end in different SAT'
    # ax.set_title(fig_title)
    original_x = [0.5, 1.5, 2.5, 3.5, 4.5]
    plt.xticks(original_x, pd_action_list)
    # plt.xlabel(u'查询会话结束前最后一个动作')
    plt.xlabel('Last Action Before Query Session', FontSize=14)
    original_y = [0, 1, 2, 3, 4]
    new_y = [1, 2, 3, 4, 5]
    plt.yticks(original_x, new_y)
    # plt.ylabel(u'用户满意度')
    plt.ylabel('User Satisfaction', FontSize=14)

    # png_position = '../'
    # plt.show()
    plt.savefig('a.pdf')
    pass
