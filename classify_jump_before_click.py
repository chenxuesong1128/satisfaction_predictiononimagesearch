import json
import codecs

from prepared_functions import *
import pickle

err_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: int)))
err_case_return = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: int)))
valid_users = get_valid_users()

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
                    if action[0] == 'JUMP_OUT' and click_start_flag is False:
                        # err_case[user][task_id][query_id] = MARK_BEFORE_CLICK_JUMP
                        jump_out_time = action[1]
                    if action[0] == 'JUMP_IN' and click_start_flag is False:
                        err_case[user][task_id][query_id] = jump_out_time
                        num += 1
    return err_case, num

# 用于返回正常的jump out和jump in的值


def used_to_return():

    dataset = './dataset/remove_inside_action/'
    user_sqs, total_num = load_sq(dataset)
    print("case num: ", total_num)

    err_case_jump_before_click, jump_before_case_num = get_before_click_exist_jump_case(user_sqs)
    print(jump_before_case_num)

    jump_in_next_to_jump_out_num = 0
    page_start_next_to_jump_out_num = 0
    serp_jump_in_next_to_jump_out_num = 0
    landing_page_jump_in_next_to_jump_out_num = 0
    for user in err_case:
        for task_id in err_case[user]:
            for query_id in user_sqs[user][task_id]:
                line_start_flag = False
                line_num = 5
                filename = './log/' + user
                fin = open(filename)
                for line in fin:
                    # line = fin.readline()
                    if str(err_case[user][task_id][query_id]) in line:
                        line_start_flag = True
                    if line_start_flag is True:
                        line_num -= 1
                    if line_num == 4:
                        current_line = line
                        # print(line)
                    if line_num == 3:
                        if 'JUMP_IN' in line and 'http://10.129.248.85:8000' in line:
                            jump_in_next_to_jump_out_num += 1
                            err_case_return[user][task_id][query_id] = MARK_BEFORE_CLICK_JUMP

                        elif 'JUMP_IN' in line and 'http://10.129.248.85:8000' not in line:
                            if 'asf=pic.sogou.com' in line:
                                # print(line)
                                serp_jump_in_next_to_jump_out_num += 1
                            elif 'mode' in line:
                                landing_page_jump_in_next_to_jump_out_num += 1
                            else:
                                print('line', line)
                            # print('CRRNT', current_line)
                            # print('LINE', line)
                        elif 'PAGE_START' in line:
                            page_start_next_to_jump_out_num += 1
                            # print(user, ' ', task_id, ' ', query_id, ' ')
                            # print('line', line)
                        else:
                            # print(line)
                            pass
                    if line_num <= 0:
                        break

    print('jump_in_next_to_jump_out_num', jump_in_next_to_jump_out_num)
    print('page_start_next_to_jump_out_num', page_start_next_to_jump_out_num)
    print('hover_next_to_jump_out_num', '1')
    print('serp_jump_in_next_to_jump_out_num', serp_jump_in_next_to_jump_out_num)
    print('landing_page_jump_in_next_to_jump_out_num', landing_page_jump_in_next_to_jump_out_num)

    return err_case_return

