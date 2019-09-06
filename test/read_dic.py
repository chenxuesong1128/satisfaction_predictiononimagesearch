import json
import codecs

from prepared_functions import *

err_case = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: int)))
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
                    if action[0] == 'JUMP_IN' and click_start_flag is False:
                        err_case[user][task_id][query_id] = MARK_BEFORE_CLICK_JUMP
                        num += 1
                        break
    return err_case, num


if __name__ == "__main__":

    dataset = './dataset/remove_inside_action/'
    user_sqs, total_num = load_sq(dataset)
    print("case num: ", total_num)

    err_case_jump_before_click, jump_before_case_num = get_before_click_exist_jump_case(user_sqs)
    print(jump_before_case_num)

    data = []
    with codecs.open("../filter_log/20160113535", "r", "utf-8") as f:
        for line in f:
            dic = json.loads(line)
            data.append(dic)
            json.dumps(dic)

