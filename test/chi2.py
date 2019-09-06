import numpy as np
from scipy.stats import chi2_contingency

d = np.array([[37, 49, 23], [150, 100, 57]])
# print (d[0][0])
cols = np.sum(d, axis=0)
rows = np.sum(d, axis=1)
total = np.sum(d)
print(cols)
print(rows)
print(total)
exp_d = np.zeros([2, 3])
for r in range(2):
    for c in range(3):
        exp_d[r][c] = cols[c] * rows[r] / total

chi2 = 0
for r in range(2):
    for c in range(3):
        chi2 += pow((d[r][c]-exp_d[r][c]), 2) / exp_d[r][c]

# chi2 /= 6
print(chi2)
print(exp_d)
print(chi2_contingency(d))