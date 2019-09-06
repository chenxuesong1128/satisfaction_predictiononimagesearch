from collections import defaultdict

s1 = [0,0,0,0,0,0,0,0]
filename='./dataset/query_satisfaction1119.csv'
# query_satisfaction[task_id][user][query_id] = satisfaction
satisfaction_dict = defaultdict(lambda: defaultdict(lambda: {}))
fin = open(filename).readlines()[1:]
# explore e.g.You want to know some information about Los Angelas (e.g. streets, landscapes, buildings).
# Entertaining e.g. You want to browse some posters or photos of your favorite stars to kill time.
# Locating e.g. You need to make a slide about Harry Potter film to introduce the protagonists.
Exp, Ent, Loc = 0, 0, 0
for line in fin:
    user, task_id, query_id, query, satisfaction = line.strip().split(',')
    satisfaction = int(satisfaction)
    s1[satisfaction] += 1
    satisfaction_dict[task_id][user][query_id] = int(satisfaction)  # satisfaction from 1
    if 1 <= int(task_id) <= 4:
        Exp += 1
    if 5 <= int(task_id) <= 8:
        Ent += 1
    if 9 <= int(task_id) <= 12:
        Loc += 1
print("num of Explore:", Exp)
print("num of Entertainment:",Ent)
print("num of locating", Loc)

