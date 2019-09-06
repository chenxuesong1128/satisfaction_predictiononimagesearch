__author__ = 'Jerry'

from prepared_functions import *
import numpy as np

valid_users = get_valid_users()

# action[5] row
# action[6] col

# click 总的数量
# 一行中只出现一次click的数量





if __name__ == "__main__":
    dataset = './dataset/f_remove_jump_before_click/'
    user_sqs, total_num = load_sq(dataset)
    satisfaction_dic = load_query_satisfaction()


