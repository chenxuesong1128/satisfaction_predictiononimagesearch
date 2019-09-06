from collections import defaultdict

valid_users = ['20160113535', '2016011528', '2016011386', '2016011387', '2016011395', '2016010022', '2016011397',
               '2016011391', '2016011290', '2016011303', '2016011392', '2016010811', '2016011297', '2016011330',
               '2015012820', '2015011753', '2015012610', '2013011818', '2015012739', '2015012630', '2015011759',
               '2015012822', '2015012881', '2015011771', '2015011742', '2015013055', '2015011285', '2015012647',
               '2016211382', '2015012867', '2015011770', '2015011348', '2015011748', '2015012620', '2015011765',
               '2015011727']


def load_sq(dataset):

    # user_sqs[user][task_id][query_id] = [['PAGE_START', abs_time], ['JUMP_OUT', abs_time], ['JUMP_IN', abs_time], ['CLICK', url, dwell_time, abs_time, rank], ['HOVER', url, dwell_time, abs_time, rank], ['SCROLL', y1, y2, abs_time], ['PAGE_END', abs_time]]

    user_sqs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    total_num = 0
    for user in valid_users:
        fin = open(dataset + user, 'r').readlines()
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
                    row = int(infos[5])
                    col = int(infos[6])
                    user_sqs[user][task_id][query_id].append([name, url, time, abs_time, rank, row, col])
                elif name == 'SCROLL':
                    y1 = float(infos[1])
                    y2 = float(infos[2])
                    abs_time = int(infos[3])
                    user_sqs[user][task_id][query_id].append([name, y1, y2, abs_time])
                else:
                    abs_time = int(infos[1])
                    user_sqs[user][task_id][query_id].append([name, abs_time])

    return user_sqs, total_num


def get_valid_users():
    return valid_users


def store_info(user_sqs: object, err_case: object, target_dir: object, mark_num: object) -> object:
    """

    :rtype:
    """
    remain_row_num = 0

    for user in valid_users:
        filename = target_dir + user
        fout = open(filename, 'w')
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                if err_case[user][task_id][query_id] == mark_num:
                    continue
                else:
                    query = user_sqs[user][task_id][query_id][0][0]
                    row = task_id + '-' + query_id + '-' + query
                    for sequence in user_sqs[user][task_id][query_id][1:]:
                        tmp = '|'.join(str(s) for s in sequence)
                        row += '\t' + tmp
                    fout.write(row)
                    fout.write('\n')
                    remain_row_num += 1

    return remain_row_num


def case_num_check(user_sqs):

    case_num = 0

    for user in valid_users:
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                for sequence in user_sqs[user][task_id][query_id]:
                    case_num += 1

    return case_num


def store_info_2_variable(user_sqs, err_case, target_dir, mark_num, err_case_return):
    remain_row_num = 0

    for user in valid_users:
        filename = target_dir + user
        fout = open(filename, 'w')
        for task_id in user_sqs[user]:
            for query_id in user_sqs[user][task_id]:
                if err_case_return[user][task_id][query_id] == mark_num:
                    query = user_sqs[user][task_id][query_id][0][0]
                    row = task_id + '-' + query_id + '-' + query
                    for sequence in user_sqs[user][task_id][query_id][1:]:
                        tmp = '|'.join(str(s) for s in sequence)
                        row += '\t' + tmp
                    fout.write(row)
                    fout.write('\n')
                    remain_row_num += 1
                if err_case[user][task_id][query_id] == mark_num:
                    continue
                else:
                    query = user_sqs[user][task_id][query_id][0][0]
                    row = task_id + '-' + query_id + '-' + query
                    for sequence in user_sqs[user][task_id][query_id][1:]:
                        tmp = '|'.join(str(s) for s in sequence)
                        row += '\t' + tmp
                    fout.write(row)
                    fout.write('\n')
                    remain_row_num += 1

    return remain_row_num


def load_query_satisfaction(filename='./dataset/query_satisfaction1119.csv'):
    # query_satisfaction[task_id][user][query_id] = satisfaction
    satisfaction_dict = defaultdict(lambda: defaultdict(lambda: {}))
    fin = open(filename).readlines()[1:]
    # explore e.g.You want to know some information about Los Angelas (e.g. streets, landscapes, buildings).
    # Entertaining e.g. You want to browse some posters or photos of your favorite stars to kill time.
    # Locating e.g. You need to make a slide about Harry Potter film to introduce the protagonists.
    Exp, Ent, Loc = 0, 0, 0
    for line in fin:
        user, task_id, query_id, query, satisfaction = line.strip().split(',')
        satisfaction_dict[task_id][user][query_id] = int(satisfaction)  # satisfaction from 1
        if 1 <= int(task_id) <= 4:
            Exp += 1
        if 5 <= int(task_id) <= 8:
            Ent += 1
        if 9 <= int(task_id) <= 12:
            Loc += 1
    print("num of Explore:", Exp)
    print("num of Entertainment:", Ent)
    print("num of locating", Loc)
    return satisfaction_dict

