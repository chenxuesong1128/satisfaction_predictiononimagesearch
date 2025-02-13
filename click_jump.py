__author__ = 'Jerry'

from collections import defaultdict
import math
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

ERR_PAGE_START = 0
ERR_PAGE_START_END_PAIR_NUM = 1
ERR_PAGE_START_END_PAIR = 2
ERR_JUMP = 3
ERR_CLICK_JUMP_PAIR = 4
ERR_NON_CLICK_JUMP_PAIR = 5
ERR_BEFORE_CLICK_JUMP = 6
ERR_JUMP_PAIR = 7
# 记录在点击之前存在jump in和jump out行为但是他们不是成对出现
ERR_BEFORE_CLICK_JUMP_OUT_UNMATCH_JUMP_IN = 8
aciton_abstime_index = {
    'PAGE_START_index': 1,
    'CLICK_index':3,
    'JUMP_IN_index':1,
    'JUMP_OUT_index':1,
    'SCROLL_index':3,
    'HOVER_index':3,
    'PAGE_END_index':1
}


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
        fin = open('./dataset/remove_err_un_match/' + user, 'r').readlines()
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
                    # row = int(infos[5])
                    # col = int(infos[6])
                    # user_sqs[user][task_id][query_id].append([name, url, time, abs_time, rank, row, col])
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


def click_jump(user_sqs):

    jump_out_num = 0
    jump_in_num = 0
    non_click_jump_out_num = 0
    non_click_jump_in_num = 0
    click_jump_out_num = 0
    click_jump_in_num = 0
    click_num = 0
    jump_after_click_num = 0
    err_num = 0
    page_start_num = 0
    page_end_num = 0
    sequence_num = 0
    non_click_jump_un_pair_num = 0
    before_click_jump_num = 0
    time_gap_list_after_click = []

    err_page = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    # user_sqs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                query_start_flag = False
                click_start_flag = False
                sequence_num += 1
                sequence_pagestart_num = 0
                sequence_pageend_num = 0
                pair_check = 0
                jump_pair_check = 0
                click_jump_pair_check = 0
                non_click_jump_pair_check = 0
                jump_out_start = False
                for action in sequence:


                    #
                    if jump_out_start is True:
                        if action[0] == 'JUMP_IN':
                            pass
                        elif action[0] == 'PAGE_END':
                            pass
                        # elif action[0] == 'HOVER':
                        #     pass
                        else:
                            print(action[1])
                            err_page[user][task_id][query_id].append(ERR_JUMP_PAIR)
                    # if jump_out_start is True and action[0] != 'PAGE_END':
                    #     err_page[user][task_id][query_id] = ERR_JUMP_PAIR
                    if action[0] == 'PAGE_START':
                        sequence_pagestart_num += 1
                        query_start_flag = True
                        page_start_num += 1
                        pair_check += 1
                    if action[0] == 'PAGE_END':
                        sequence_pageend_num += 1
                        query_start_flag = False
                        click_start_flag = False
                        page_end_num += 1
                        pair_check -= 1
                    if action[0] == 'JUMP_OUT':
                        jump_out_num += 1
                        jump_pair_check += 1
                        jump_out_start = True
                    if action[0] == 'JUMP_IN':
                        jump_in_num += 1
                        jump_pair_check -= 1
                        jump_out_start = False
                    if action[0] == 'JUMP_OUT' and click_start_flag is False:
                        non_click_jump_out_num += 1
                        non_click_jump_pair_check += 1

                        # 记录用户在点击之前存在jump in 和 jump out行为的分析
                        # err_page[user][task_id][query_id].append(ERR_BEFORE_CLICK_JUMP)

                        # err_num += 1
                        before_click_jump_num += 1
                    if action[0] == 'JUMP_IN' and click_start_flag is False:
                        non_click_jump_in_num += 1
                        non_click_jump_pair_check -= 1

                    if action[0] == 'CLICK':
                        click_start_flag = True
                        click_num += 1
                    if action[0] == 'JUMP_OUT' and click_start_flag is True:
                        jump_after_click_num += 1
                        click_jump_out_num += 1
                        click_jump_pair_check += 1
                        start_time = action[1]
                    if action[0] == 'JUMP_IN' and click_start_flag is True:
                        # click_start_flag = False
                        click_jump_in_num += 1
                        click_jump_pair_check -= 1
                        end_time = action[1]
                        time_gap_list_after_click.append(end_time - start_time)

                # 所有query中的开始标签数量均为1个

                if sequence_pagestart_num >= 2:
                    err_page[user][task_id][query_id].append(ERR_PAGE_START)

                # 所有的结束标签的数量均为1个

                if sequence_pageend_num >= 2:
                    err_page[user][task_id][query_id].append(ERR_PAGE_START_END_PAIR_NUM)

                # query中page start和page end 配对检查

                if pair_check != 0:
                    err_page[user][task_id][query_id].append(ERR_PAGE_START_END_PAIR)

                # 点击之前的jump in和jump out是否配对检查，将jump out后面连接page end的情况标注出来

                if non_click_jump_pair_check != 0:
                    # print(type(err_page[user][task_id][query_id]))
                    err_page[user][task_id][query_id].append(ERR_NON_CLICK_JUMP_PAIR)
                    err_num += 1
                    # pass
                # click后出现jump out和jump in情况检查

                if click_jump_pair_check != 0:
                    page_end_pos = len(user_sqs[user][task_id][query_id]) - 1
                    if user_sqs[user][task_id][query_id][page_end_pos][0] != 'PAGE_END':
                        err_page[user][task_id][query_id].append(ERR_CLICK_JUMP_PAIR)
                if non_click_jump_pair_check != 0:
                    page_end_pos = len(user_sqs[user][task_id][query_id]) - 1
                    if user_sqs[user][task_id][query_id][page_end_pos][0] != 'PAGE_END':
                        err_page[user][task_id][query_id].append(ERR_BEFORE_CLICK_JUMP_OUT_UNMATCH_JUMP_IN)
                # if query_start_flag == True:
                #     err_num += 1
    print("sequence num:", sequence_num)
    print("non_click_un_pair_num:", non_click_jump_un_pair_num)
    print(page_start_num)
    print(page_end_num)
    print("page start and end ok.")
    print("before click exist jump num:", before_click_jump_num)
    print("err_num:", err_num)
    print('debug')

    return user_sqs, err_page


def store_user_sqs(user_sqs, err_page):

    time_gap_list_before_click = []
    num_of_6 = 0
    false_num = 0
    for user in valid_users:
        filename = './dataset/sq_annot4/' + user
        fout = open(filename, 'w')
        write_flag = True
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:

                fout2_txt = ''
                row = task_id + '-' + query_id + '-'
                # print(type(user_sqs[user][task_id][query_id]))
                query = user_sqs[user][task_id][query_id][0][0]
                row += query
                # print(len(user_sqs[user][task_id][query_id]))
                before_click = True
                time_gap = 0
                start_time = 0
                # if err_page[user][task_id][query_id] != 7:
                for sequence in user_sqs[user][task_id][query_id][1:]:

                # 对sequence中时间序列进行操作
                    if 6 != err_page[user][task_id][query_id]:
                    # if 6 in err_page[user][task_id][query_id] and 5 not in err_page[user][task_id][query_id]:
                        tmp = '|'.join(str(s) for s in sequence)
                        row += '\t' + tmp
                    else:
                        write_flag = False
                # print(row)
                if write_flag is False:
                    false_num += 1
                else:
                    fout.write(row)
                    fout.write('\n')
    print("false num", false_num)

def get_time_gap_list(user_sqs):

    time_gap_list_before_click = []
    time_gap_list_after_click = []

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                click_start_flag = False
                start_time = 0
                for action in sequence:
                    if action[0] == 'JUMP_OUT' and click_start_flag is False:
                        start_time = action[1]
                    if action[0] == 'JUMP_IN' and click_start_flag is False:
                        end_time = action[1]
                        time_gap = end_time - start_time
                        time_gap_list_before_click.append(time_gap)
                    if action[0] == 'CLICK':
                        click_start_flag = True

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                click_start_flag = False
                start_time = 0
                for action in sequence:
                    if action[0] == 'JUMP_OUT' and click_start_flag is True:
                        start_time = action[1]
                    if action[0] == 'JUMP_IN' and click_start_flag is True:
                        end_time = action[1]
                        time_gap = end_time - start_time
                        time_gap_list_after_click.append(time_gap)
                    if action[0] == 'CLICK':
                        click_start_flag = True

    return time_gap_list_before_click, time_gap_list_after_click


def get_num_of_jump_in_and_jump_out_pair(user_sqs):
    num = 0
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                jump_pair_start = False
                for action in sequence:
                    if action[0] == 'JUMP_OUT':
                        jump_pair_start = True
                    if action[0] == 'JUMP_IN' and jump_pair_start is True:
                        num += 1
                        jump_pair_start = False
    return num


def compare_click_before_and_click_after(user_sqs, type):
    time_gap_list_before_click, time_gap_list_after_click = get_time_gap_list(user_sqs)
    jump_out_and_jump_in_match_num = get_num_of_jump_in_and_jump_out_pair(user_sqs)
    time_gap_list_before_click_np = np.array(time_gap_list_before_click)
    time_gap_list_after_click_np = np.array(time_gap_list_after_click)
    if type == 'var':
    # 方差计算比较


        print("click之前的jump out和jump in的方差：", time_gap_list_before_click_np.var())
        print("click之后的jump out和jump in的方差：", time_gap_list_after_click_np.var())

    if type == 'scatter':
        print("jump out和jump in总对数：", jump_out_and_jump_in_match_num)
        print("在click之前的jump out和jump in的时间间隔：", len(time_gap_list_before_click))
        print("在click之后的jump out和jump in的时间间隔：", len(time_gap_list_after_click))
        # time_gap_list_before_click = store_user_sqs(to_store_user_sqs, err_page)
        avg_before = sum(time_gap_list_before_click) / len(time_gap_list_before_click)
        avg_after = sum(time_gap_list_after_click) / len(time_gap_list_after_click)
        print("avg_before", avg_before)
        print("avg_after", avg_after)
        #####   plt start    ######
        x1 = np.arange(0, len(time_gap_list_before_click))
        x2 = np.arange(0, len(time_gap_list_after_click))
        y1 = time_gap_list_before_click
        y2 = time_gap_list_after_click
        plt.scatter(x1, y1, s=20, c='g', alpha=0.5, marker='*', label='before')
        plt.scatter(x2, y2, s=20, c='b', alpha=0.5, marker='o', label='after')
        plt.legend()
        plt.show()

    # 折线图
    if type == 'zhexian':
        x1 = np.arange(0, len(time_gap_list_before_click))
        x2 = np.arange(0, len(time_gap_list_after_click))
        # y1 = time_gap_list_before_click.sort()
        # y2 = time_gap_list_after_click.sort()
        y1 = np.sort(time_gap_list_before_click_np)
        y2 = np.sort(time_gap_list_after_click_np)
        plt.figure(12)
        plt.subplot(121)
        plt.plot(x1, y1)
        y1_mean = np.mean(time_gap_list_before_click_np)

        plt.plot(x1, np.linspace(y1_mean, y1_mean, len(x1)))

        plt.subplot(122)
        plt.plot(x2, y2)
        y2_mean = np.mean(time_gap_list_after_click_np)
        plt.plot(x2, np.linspace(y2_mean, y2_mean, len(x2)))


def get_before_click_exist_jump_case(user_sqs):
    err_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: int)))
    num = 0
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                click_start_flag = False
                for action in sequence:
                    if action[0] == 'CLICK':
                        click_start_flag = True
                    if action[0] == 'JUMP_IN' and click_start_flag is False:
                        err_case[user][task_id][query_id] = ERR_BEFORE_CLICK_JUMP
                        num += 1
                        break
    print('jump case num', num)
    return err_case, num

def store_all_right_info(user_sqs, err_case):
    row_num = 0
    for user in valid_users:
        filename = './dataset/sq_annot4/' + user
        fout = open(filename, 'w')
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                if err_case[user][task_id][query_id] == 6:
                    continue
                else:
                    query = user_sqs[user][task_id][query_id][0][0]
                    row = task_id + '-' + query_id + '-' + query
                    for sequence in user_sqs[user][task_id][query_id][1:]:
                        tmp = '|'.join(str(s) for s in sequence)
                        # print(tmp)
                        row += '\t' + tmp
                    fout.write(row)
                    fout.write('\n')
                    row_num += 1
    print(row_num)




if __name__ == "__main__":
    user_sqs = load_sq()
    err_case, num = get_before_click_exist_jump_case(user_sqs)
    # click_jump(user_sqs)
    # compare_click_before_and_click_after(user_sqs, 'zhexian')
    # store_user_sqs(user_sqs, err_case)
    store_all_right_info(user_sqs, err_case)



