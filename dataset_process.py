__author__ = 'Jerry'

from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import json
import codecs
from classify_jump_before_click import *
from prepared_functions import *

err_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: int)))
valid_users = get_valid_users()


# 对于同一查询词查询多次，即出现多次page start page end

MARK_MULTIPLE_PAGE_START = 1


def solve_multiple_times_page_start_and_page_end(user_sqs, valid_users):

    case_num = 0

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                page_start_num = 0
                for action in sequence:
                    if action[0] == 'PAGE_START':
                        page_start_num += 1
                if page_start_num >= 2:
                    case_num += 1
                    err_case[user][task_id][query_id] = MARK_MULTIPLE_PAGE_START

    return err_case, case_num


# 上面默认了page_start和page_end是成对出现的
# 检查出现多次page end，手动修改2次/1067

MARK_MULTIPLE_PAGE_END = 2


def solve_multiple_page_end(user_sqs):

    multiple_page_end_case_num = 0

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                page_end_num = 0
                for action in sequence:
                    if action[0] == 'PAGE_END':
                        page_end_num += 1
                if page_end_num >= 2:
                    multiple_page_end_case_num += 1
                    err_case[user][task_id][query_id] = MARK_MULTIPLE_PAGE_END

    return err_case, multiple_page_end_case_num


# 解决page start和page end不配对问题

MARK_PAGE_START_UN_MATCH_PAGE_END = 3


def solve_page_start_un_match_page_end(user_sqs):

    page_start_un_match_page_end_num = 0

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                page_start_flag = 0
                for action in sequence:
                    if action[0] == 'PAGE_START':
                        page_start_flag += 1
                    if action[0] == 'PAGE_END':
                        page_start_flag -= 1
                if page_start_flag != 0:
                    err_case[user][task_id][query_id] = MARK_PAGE_START_UN_MATCH_PAGE_END
                    page_start_un_match_page_end_num += 1

    return err_case, page_start_un_match_page_end_num


# 检查jump out和jump in之间存在动作的情况

MARK_ACTION_BETWEEN_OUT_AND_IN = 4


def solve_action_between_out_and_in(user_sqs):
    num = 0

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                jump_out_start_flag = False
                for action in sequence:
                    if action[0] == 'JUMP_OUT':
                        jump_out_start_flag = True
                    if jump_out_start_flag is True and action[0] != 'JUMP_OUT':
                        if action[0] == 'JUMP_IN':
                            jump_out_start_flag = False
                        elif action[0] == 'PAGE_END':
                            pass
                        else:
                            print(action[0])
                            err_case[user][task_id][query_id] = MARK_ACTION_BETWEEN_OUT_AND_IN
                            num += 1
                            break

    return err_case, num


# 获取在click之前存在jump out和jump in的情况

MARK_BEFORE_CLICK_JUMP = 5


def get_before_click_exist_jump_case(user_sqs):
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
                        err_case[user][task_id][query_id] = MARK_BEFORE_CLICK_JUMP
                        num += 1
                        break
    return err_case, num


# click 后出现无点击的jump out和jump in行为的情况

MARK_AFTER_CLICK_ABNORMAL_JUMP = 6


def get_after_click_abnormal_jump_case(user_sqs):
    num = 0
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]
                for action in sequence:
                    click_start_flag = False
                    click_flag = False
                    if action[0] == 'CLICK':
                        click_start_flag = True
                        click_flag = True
                    if click_start_flag is True and action[0] == 'JUMP_IN' and click_flag is True:
                        click_flag = False
                    if action[0] == 'JUMP_IN' and click_flag is True and click_flag is False:
                        num += 1
                        err_case[user][task_id][query_id] = MARK_AFTER_CLICK_ABNORMAL_JUMP
                        # break
    return err_case, num


if __name__ == "__main__":

    dataset = './dataset/remove_inside_action/'
    # dataset = './dataset/f_remove_jump_before_click/'

    user_sqs, total_num = load_sq(dataset)
    print("case num: ", total_num)

# 处理page start
# -----start-----

#     err_case_page_start, multiple_page_start_case_num = solve_multiple_times_page_start_and_page_end(user_sqs, valid_users)
#     print(multiple_page_start_case_num)
#     store_info(user_sqs, err_case, './dataset/remove_err_page_start_edit_page_end/', MARK_MULTIPLE_PAGE_START)


# ------end-----

# 处理page end
# ------start----

    # err_case_page_end, multiple_page_end_case_num = solve_multiple_page_end(user_sqs)
    # print(multiple_page_end_case_num)

# -----end------


# 处理page start和page_end配对问题
# ------start---------

    # err_case_un_match, un_match_case_num = solve_page_start_un_match_page_end(user_sqs)
    # print(un_match_case_num)
    # store_info(user_sqs, err_case_un_match, './dataset/remove_err_un_match/', MARK_PAGE_START_UN_MATCH_PAGE_END)

# ------end---------


# 处理jump start和jump in之间存在动作
# -------start-------

    # err_case_un_exist_action, exist_action_case_num = solve_action_between_out_and_in(user_sqs)
    # print(exist_action_case_num)
    # store_info(user_sqs, err_case_un_exist_action, './dataset/remove_inside_action/', MARK_ACTION_BETWEEN_OUT_AND_IN)


# -------end-------


# 处理在click前存在jump行为的情况
# -------start------

    # err_case_jump_before_click, jump_before_case_num = get_before_click_exist_jump_case(user_sqs)
    # print(jump_before_case_num)
    # with codecs.open('./mark_case/jump_before_case_num.json', 'w', 'utf-8') as outf:
    #     json.dump(err_case, outf, ensure_ascii=False)
    #     outf.write('\n')

# -------end--------


# 处理在click前存在jump行为的情况
# -------start------

    # err_case_after_click_abnormal_jump, after_click_abnormal_jump_num = get_after_click_abnormal_jump_case(user_sqs)
    # print(after_click_abnormal_jump_num)
    # pass
# -------end--------


# 删除click前存在jump信息的case
# -------start-------------

    err_case_jump_before_click, jump_before_click_num = get_before_click_exist_jump_case(user_sqs)
    print(jump_before_click_num)
    err_case_return = used_to_return()
    remain_num = store_info_2_variable(user_sqs, err_case_jump_before_click, './dataset/f_remove_jump_before_click/', MARK_BEFORE_CLICK_JUMP, err_case_return)
    print(remain_num)

# -------end---------------
