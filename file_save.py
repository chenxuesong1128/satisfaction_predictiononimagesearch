import pickle
# create dict
list = {"01":2,"02":3,"03":4}
# save dict
f1 = open("./test.txt","wb")
pickle.dump(list, f1)
f1.close()
# load dict
f2 = open("./test.txt","rb")
load_list = pickle.load(f2)
f2.close()