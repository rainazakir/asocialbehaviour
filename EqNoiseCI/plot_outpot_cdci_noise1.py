import pickle
import matplotlib.pyplot as plt
import glob, os
from pathlib import Path
import math
import numpy as np
import matplotlib as M

plt.rcParams["figure.figsize"] = (25, 18)
plt.rcParams["axes.grid"] = False
##plotting noise 1 output from equation



withBif = True
# array to load bifurcation files
data_files_bif = []

# to store bifurcation points to plot
bix = []
biy = []
opdir_bifurcation = '/Users/rzakir/Documents/fromasus/2022/Eq10MobiliaPRE/bifurcationlines/N1/'  # os.gtcwd()

with open("/Users/rzakir/Documents/fromasus/2022/Eq10MobiliaPRE/matrixforcdciheatmaps/test.txt", "rb") as fp:
  listx = pickle.load(fp)

with open("/Users/rzakir/Documents/fromasus/2022/Eq10MobiliaPRE/matrixforcdciheatmaps/test1.txt", "rb") as fp:
  listy = pickle.load(fp)

plt.grid(False)
plt.hist2d(listx, listy, bins=[38, 38], cmap='Reds', norm=M.colors.SymLogNorm(linthresh=0.000000001) ,linewidth=0)
#plt.imshow(heatMatrixFull,cmap='Reds', norm=M.colors.SymLogNorm(linthresh=0.000000003, linscale=0.0000000003),aspect='auto')

if withBif:
    data_files_bif += [file1 for file1 in os.listdir(opdir_bifurcation)]  # for adding your i
    name1 = sorted(data_files_bif, reverse=True)
    print(data_files_bif)
    for file1 in data_files_bif:
        print(file1)
        with open(opdir_bifurcation + file1, 'r') as f1:
            if (file1.endswith('.txt')):
                plt.axhline(y=0.0,linewidth=14, linestyle='dashed', color="royalblue",zorder=1)

                if (file1.endswith('P5.txt')):
                    for line1 in f1:
                        bix.append(float(line1.split()[0]) * 100)
                        biy.append((-1 * (200 * float(line1.split()[1])) + 200))
                        ###without formatting:
                        ###bix.append(float(line1.split()[0]))
                        ###bix.append(float(line1.split()[1]))
                        plt.plot(bix, biy, linewidth=14, linestyle='dashed', color="royalblue")
                        # plt.axhline(y=200,linewidth=14, linestyle='dashed', color="royalblue",zorder=1)
                        # plt.plot(bix,biy,linewidth=14, color=[0.0, 01.0, 0.0])

                else:
                    # if ra == 1:
                    print("nothing")
                    # else:
                    for line1 in f1:
                            bix.append(float(line1.split()[0]))
                            biy.append(float(line1.split()[1]))
                            #plt.plot(bix, biy, linewidth=14, color=[0.0, 01.0, 0.0])
                        ###without formatting:
                        ###bix.append(float(line1.split()[0]))
                        ###bix.append(float(line1.split()[1]))
                    plt.plot(bix, biy, linewidth=14, color=[0.0, 01.0, 0.0])

                bix = []
                biy = []

#plt.pcolormesh(listx,listy,cmap='Blues',linewidth=0)
plt.xticks(fontsize=44)
plt.yticks(fontsize=44)



plt.xlabel(r'noise type 1 $σ$', fontsize=62)
#plt.ylabel(r'stationary probability distribution', fontsize=48)
#plt.savefig('images/NEWFIG22/spd_cdci_vary_noise1_n200_22_22.pdf', dpi=300, bbox_inches='tight')

plt.show()
