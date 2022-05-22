# checking program
import math
import matplotlib.pyplot as plt
import glob, os
import pathlib
import numpy as np
from matplotlib import patches
from matplotlib.lines import Line2D
import matplotlib.lines as mlines
import matplotlib as M
# import seaborn
#from future.backports.test.pystone import TRUE
from matplotlib import colors
plt.rcParams["figure.figsize"] = (25, 18)

N = [200]
n=200
Zproportion = [0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.26,0.27,0.28,0.29,0.3,0.31,0.32,0.33,0.34,0.35,0.36,0.37,0.38,0.39,0.4,0.41,0.42,0.43,0.44,0.45,0.46,0.47,0.48,0.49,0.5,0.51,0.52,0.53,0.54,0.55,0.56,0.57,0.58,0.59,0.6,0.61,0.62,0.63,0.64,0.65,0.66,0.67,0.68,0.69,0.7,0.71,0.72,0.73,0.74,0.75,0.76,0.77,0.78,0.79,0.8,0.81,0.82,0.83,0.84,0.85,0.86,0.87,0.88,0.89,0.9,0.91,0.92,0.93,0.94,0.95,0.96,0.97,0.98,0.99]
#Zproportion = [0.1]
Sproportion = [1-z for z in Zproportion]
heatMatrix = []
with open('/content/drive/MyDrive/matrixforcdciheatmaps/matrixfile2.txt') as f:
  for line in f:
    line = line.lstrip('[').rstrip('],\n')
    #print(line)
    heatMatrix.append([np.float128(x) for x in line.split(',')]) 
    #heatMatrix = [[float(x) for x in row.split(',')] for row in line]


#print(heatMatrix)
  

#binnedMatrix = [ [0]*(n+1)/3 for heatMatrix in range(n+1)/3 ]

#print(binnedMatrix)

#plt.imshow(heatMatrix, cmap='Reds')

    # plt.hist2d(dump_list_x_points, dump_list_y_points, bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())
for i in heatMatrix:
    print("yhis line",i)
heatMatrixFull = []
for z in np.arange(0, 1, 2.0 / n):
    found = False
    for zi, zVal in enumerate(Zproportion):
        if np.abs(zVal - z) < 0.0000000001:
            heatMatrixFull.append(heatMatrix[zi])
            found = True
            break
    if not found:
        heatMatrixFull.append([0] * (n * 2 + 1))
        print("On the x-axis the value " + str(z) + " has not been found.")
heatMatrixFull = list(reversed(list(zip(*heatMatrixFull))))

heatMatrixFull.pop(0)

    #heatMatrixFull= np.delete(heatMatrixFull, 0, 0)
    #N = len(heatMatrixFull)
  #  M = len(heatMatrixFull[0])

    #heatMatrixFull = list(heatMatrixFull)
print(len(heatMatrixFull),len(heatMatrixFull[0]))   #prints (200, 50)--> rows,columns

binnedMatrix =[[0]*(len(heatMatrixFull[0])) for i in range(len(heatMatrixFull)//5)]

for i in range(len(heatMatrixFull)):
  for j in range(len(heatMatrixFull[0])):
      binnedMatrix[int(np.floor(i/5))][int(np.floor(j))] += heatMatrixFull[i][j]
plt.imshow(binnedMatrix, cmap='Reds',norm=M.colors.SymLogNorm(linthresh="0.000000000001"), aspect='auto')
#print(heatMatrixFull)
#plt.hist2d( heatMatrixFull[:,0], heatMatrixFull[:,1], bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())
#norm=M.colors.SymLogNorm(linthresh=0.000000003, linscale=0.0000000003)

#norm=M.colors.PowerNorm(gamma=0.1)
#plt.imshow(heatMatrixFull, cmap='Reds',aspect="auto",norm=norm)
#plt.matshow(heatMatrixFull, cmap='Reds',aspect="auto",interpolation='nearest')
#plt.imshow(heatMatrixFull, cmap='Reds',norm=norm,aspect="auto")

# plt.xticks([-1, -0.5, 0, 0.5, 1])
plt.xticks(fontsize=36)
# plt.yticks([])
plt.yticks(fontsize=36)

# plt.xlabel(r'population $X-Y$', fontsize=44)
# plt.ylabel(r'stationary probability distribution', fontsize=44)

ax = plt.gca()
    # ax.set_xlim([0, 1])
    # ax.set_ylim([-1, 1])
ax.margins(0)

plt.xlabel(r'asocial behavior $z_x+z_y$', fontsize=44)
plt.ylabel(r'population $X-Y$', fontsize=44)
# plt.title('Population Evolution: Zealots- QRatio-1.05, CDCI, N=200', fontsize=32)


# plt.show()
# plt.savefig('images/cdci_qr105_zvary_insetfig4.pdf', dpi=300, bbox_inches='tight')

plt.show()