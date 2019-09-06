__author__ = 'Jerry'

###############################
# 不同满意度下的没有点击的case的时间
###############################

from prepared_functions import *
import numpy as np
import matplotlib.pyplot as plt


valid_users = get_valid_users()
satisfaction_dict = load_query_satisfaction()
satisfaction_lever_gap_time = defaultdict(lambda: defaultdict(lambda: []))


def get_non_click_case(user_sqs, valid_users):

    case_num = 0
    extra_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                non_click_flag = True

                for action in sequence:
                    if action[0] == 'CLICK':
                        non_click_flag = False
                        break

                if non_click_flag == True:
                    extra_case[user][task_id][query_id] = sequence
                    case_num += 1

    return extra_case, case_num


def get_non_click_case_empty_between(user_sqs, valid_users):

    case_num = 0
    extra_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                # print(sequence[len(sequence)-1][0])
                if len(sequence) == 3:
                    extra_case[user][task_id][query_id] = sequence
                    case_num += 1

    return extra_case, case_num


def get_non_click_case_something_between(user_sqs, valid_users):

    case_num = 0
    extra_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                non_click_flag = True

                for action in sequence:
                    if action[0] == 'CLICK':
                        non_click_flag = False
                        break

                if non_click_flag == True:
                    if len(sequence) > 3:
                        extra_case[user][task_id][query_id] = sequence
                        case_num += 1

    return extra_case, case_num


def page_start_to_page_end_time(non_click_case):

    for user in valid_users:
        for task_id in non_click_case[user]:
            for query_id in non_click_case[user][task_id]:
                sequence = non_click_case[user][task_id][query_id]
                if 1 <= int(task_id) <= 4:
                    type = 'Exp'
                elif 5 <= int(task_id) <= 8:
                    type = 'Ent'
                elif 9 <= int(task_id) <= 12:
                    type = 'Loc'
                satisfaction_lever = satisfaction_dict[task_id][user][query_id]
                page_start_time = sequence[1][1]
                page_end_time = sequence[len(sequence) - 1][1]
                # print(user, task_id, query_id, sequence)
                gap_time = page_end_time - page_start_time
                satisfaction_lever_gap_time[satisfaction_lever][type].append(gap_time)
                satisfaction_lever_gap_time[satisfaction_lever]['All'].append(gap_time)
    return satisfaction_lever_gap_time


def visual_result(satisfaction_lever_gap_time):
    diff_lever_avg_time = np.zeros(6)
    # for satisfaction_lever in range(1, 6, 1):
    #     diff_lever_avg_time[satisfaction_lever] = np.array(satisfaction_lever_gap_time[satisfaction_lever]['All']).mean()
    n_groups = 5

    # 盒装图展示不同满意度下的time gap情况
    labels = [1, 2, 3, 4, 5]
    fig, ax = plt.subplots()
    data = []
    for i in range(1, 6):
        data.append(np.array(satisfaction_lever_gap_time[i]['All']))
    bplot1 = ax.boxplot(data,
                        vert=True,  # vertical box alignment
                        patch_artist=True,  # fill with color
                        labels=labels)  # will be used to label x-ticks
    ax.set_title('Rectangular box plot')
    plt.show()

    # 柱状图展示平均分数
    diff_lever_avg_time = np.zeros(6)
    for satisfaction_lever in range(1, 6, 1):
        diff_lever_avg_time[satisfaction_lever] = np.array(
            satisfaction_lever_gap_time[satisfaction_lever]['All']).mean()
    n_groups = 5
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4
    lable_name = 'average gap time'
    rects1 = plt.bar(index, diff_lever_avg_time[1:6], bar_width, alpha=opacity, color='b', label=lable_name)

    plt.xlabel('satisfaction lever')
    plt.ylabel('gap time')
    plt.title('different satisfaction average gap time')
    plt.xticks(index, ('1', '2', '3', '4', '5'))
    plt.legend()

    plt.tight_layout()
    plt.show()



    # 柱状图展示不同满意度的数量分布
    n_groups = 5
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    n_data = []
    for i in range(0, 5):
        n_data.append(len(data[i]))
    opacity = 0.4
    lable_name = 'diff lever num'
    rects1 = plt.bar(index, n_data, bar_width, alpha=opacity, color='b', label=lable_name)

    plt.xlabel('satisfaction lever')
    plt.ylabel('num')
    plt.title('different satisfaction\'s num')
    plt.xticks(index, ('1', '2', '3', '4', '5'))
    plt.legend()

    plt.tight_layout()
    plt.show()



if __name__ == "__main__":

    dataset = './dataset/f_remove_jump_before_click/'
    user_sqs, total_num = load_sq(dataset)
    print("case num: ", total_num)

    # 笼统不区分page start和page end内部的动作

    # non_click_case, non_click_case_num = get_non_click_case(user_sqs, valid_users)
    # satisfaction_lever_gap_time = page_start_to_page_end_time(non_click_case)
    # visual_result(satisfaction_lever_gap_time)

    # page start和page end之间不存在动作
    non_click_case_empty_between_case, non_click_case_empty_between_num = get_non_click_case_empty_between(user_sqs, valid_users)
    satisfaction_lever_gap_time_empty_between = page_start_to_page_end_time(non_click_case_empty_between_case)
    visual_result(satisfaction_lever_gap_time_empty_between)

    # page start和page end之间存在动作的情况
    # non_click_case_something_between_case, non_click_case_something_between_num = get_non_click_case_something_between(user_sqs, valid_users)
    # satisfaction_lever_gap_time_something_between = page_start_to_page_end_time(non_click_case_something_between_case)
    # visual_result(satisfaction_lever_gap_time_something_between)



















#
# def visual_result(satisfaction_lever_gap_time):
#     diff_lever_avg_time = np.zeros(6)
#     for satisfaction_lever in range(1, 6, 1):
#         diff_lever_avg_time[satisfaction_lever] = np.array(satisfaction_lever_gap_time[satisfaction_lever]['All']).mean()
#     n_groups = 5
#     fig, ax = plt.subplots()
#     index = np.arange(n_groups)
#     bar_width = 0.35
#
#     opacity = 0.4
#     lable_name = 'average gap time'
#     rects1 = plt.bar(index, diff_lever_avg_time[1:6], bar_width, alpha=opacity, color='b', label=lable_name)
#
#     plt.xlabel('satisfaction lever')
#     plt.ylabel('gap time')
#     plt.title('different satisfaction average gap time')
#     plt.xticks(index, ('1', '2', '3', '4', '5'))
#     plt.legend()
#
#     plt.tight_layout()
#     plt.show()
#
