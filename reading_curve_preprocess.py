__author__ = 'Jerry'

from prepared_functions import *
import numpy as np

valid_users = get_valid_users()

# action[5] row
# action[6] col

# click 总的数量
# 一行中只出现一次click的数量


row_click_record = defaultdict(lambda: int)


def count_two_clicks_in_a_row(user_sqs):

    total_click_num = 0
    click_in_row = np.zeros(20)
    row_num = 0
    click_row_num = 0
    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                sequence = user_sqs[user][task_id][query_id]

                row_list = {
                    0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0,
                    16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0,
                    30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0,
                    44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: 0, 56: 0, 57: 0,
                    58: 0, 59: 0, 60: 0, 61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: 0, 67: 0, 68: 0, 69: 0, 70: 0, 71: 0,
                    72: 0, 73: 0, 74: 0, 75: 0, 76: 0, 77: 0, 78: 0, 79: 0, 80: 0, 81: 0, 82: 0, 83: 0, 84: 0, 85: 0,
                    86: 0, 87: 0, 88: 0, 89: 0, 90: 0, 91: 0, 92: 0, 93: 0, 94: 0, 95: 0, 96: 0, 97: 0, 98: 0, 99: 0,
                    100: 0, 101: 0, 102: 0, 103: 0, 104: 0, 105: 0, 106: 0, 107: 0, 108: 0, 109: 0, 110: 0, 111: 0,
                    112: 0, 113: 0, 114: 0, 115: 0, 116: 0, 117: 0, 118: 0, 119: 0, 120: 0, 121: 0, 122: 0, 123: 0,
                    124: 0, 125: 0, 126: 0, 127: 0, 128: 0, 129: 0, 130: 0, 131: 0, 132: 0, 133: 0, 134: 0, 135: 0,
                    136: 0, 137: 0, 138: 0, 139: 0, 140: 0, 141: 0, 142: 0, 143: 0, 144: 0, 145: 0, 146: 0, 147: 0,
                    148: 0, 149: 0, 150: 0, 151: 0, 152: 0, 153: 0, 154: 0, 155: 0, 156: 0, 157: 0, 158: 0, 159: 0,
                    160: 0, 161: 0, 162: 0, 163: 0, 164: 0, 165: 0, 166: 0, 167: 0, 168: 0, 169: 0, 170: 0, 171: 0,
                    172: 0, 173: 0, 174: 0, 175: 0, 176: 0, 177: 0, 178: 0, 179: 0, 180: 0, 181: 0, 182: 0, 183: 0,
                    184: 0, 185: 0, 186: 0, 187: 0, 188: 0, 189: 0, 190: 0, 191: 0, 192: 0, 193: 0, 194: 0, 195: 0,
                    196: 0, 197: 0, 198: 0, 199: 0
                }
                row_num += 1
                # if 'click' in sequence:
                #     click_row_num += 1
                for action in sequence:
                    if action[0] == 'CLICK' or action[0] == 'HOVER':
                    # if action[0] == 'HOVER':

                        row_list[action[5]] += 1
                        total_click_num += 1

                        # click_row_num += 1
                        # break

                for key in row_list.keys():
                    for i in range(1, 10):
                        if row_list[key] == i:
                            click_in_row[i] += 1
                    # if row_list[key] == 1:
                    #     one_click_in_row_num += 1
                    # if row_list[key] == 2:
                    #     two_click_in_row_num += 1
                    # if row_list[key] == 3:
                    #     three_click_in_row_num += 1
                    # if row_list[key] >= 4:
                    #     four_click_in_row_num += 1

    print('row_num', row_num)
    print('click_row_num', click_row_num)
    return total_click_num, click_in_row


if __name__ == "__main__":
    dataset = './dataset/f_remove_jump_before_click/'
    user_sqs, total_num = load_sq(dataset)
    total_click_num, click_in_row = count_two_clicks_in_a_row(user_sqs)
    print(total_click_num)
    sum = 0
    click_case_num = 0
    for i in range(1, 20):
        print(click_in_row[i])
        sum += click_in_row[i] * i
        click_case_num += click_in_row[i]
    print(click_case_num)
    print(sum)
