import glob
import os
import pathlib
from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import matplotlib as M

plt.rcParams["figure.figsize"] = (25, 18)
plt.rcParams['axes.xmargin'] = 0

# colours for the lines and points    ///add more if needed
colours = ["#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", '#21918c', '#e41a1c']
# symbols to be used for gillespie points     ///add more if needed
symbols = ["o", "v", "*", "d", "h", "X", "P", "+", "^"]

# ======GILLESPIE OR NOT=======#
gillespie_plot = "false"
# =============================#
# ======GILLESPIE OR NOT=======#
equation_plot = "true"
# ==If plotting heatmaps set to true otherwise false will generate SPD==#
heatmaps = "true"
# =============================#


# array to store gillespie files
data_files = []
# array to store gillespie points
op1 = []
op2 = []
# array to store formatted gillespie points to be plotted
pointxaxis = []
pointyaxis = []
# axis range
plt.xlim(-1, 1)
plt.ylim(0, 0.2)

patch = []

# =======Specify variables for equation to be plotted-if equation_plot set to true=====#
# total number of agents
N = 200
# specify the exponent for q voter model---> fixed to one
q = 1
# specify the qratios, ra is changed to vary qratio for agents A and Za
ra = 2
rb = 1
# specify the Susceptibles (Sa+Sb in numbers not percentage)
"""
Slist = [180, 160, 140, 100, 40, 20]
"""
Slist = [198, 196, 194, 192, 190, 188, 186, 184, 182, 180, 178, 176, 174, 172, 170, 168, 166, 164, 162, 160, 158, 156,
         154, 152, 150, 148, 146, 144, 142, 140, 138, 136, 134, 132, 130, 128, 126, 124, 122, 120, 118, 116, 114, 112,
         110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60,
         58, 56, 54, 52, 50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]

# specify the Zealots (Za in numbers and not percentage)
"""
Zplus = [10, 20, 30, 50, 80, 90]
"""
Zplus = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
         59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86,
         87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
# """
# specify the Zealots (Za in numbers and not percentage)
# """
Zminus = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
          31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
          58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84,
          85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
"""
Zminus = [10, 20, 30, 50, 80, 90]
"""
dump_list_x_points = []
dump_list_y_points = []

# =====================================================================#

# =========DIRECTORIES FOR GILLESPIE RUNS-if gillespie_plot set to true=========#
# opdir = 'D:/Simpaperresults/probabilitydistfromGillespieandsim/datafiles/'  # os.getcwd()
#####opdir = 'D:/Simpaperresults/DMVDGillespie/data1.05/VaryingZealots/'
# opdir= 'D:/Simpaperresults/probabilitydistfromGillespieandsim/datafiles_dmvd_varyZ/'
# opdir = '/Users/rzakir/Documents/fromasus/probabilitydistfromGillespieandsim/datafiles_dmvd_varyZqr2/'
opdir = '/Users/rzakir/Documents/fromasus/probabilitydistfromGillespieandsim/datafiles_dmvd_varyZ/'


# opdir = '/Users/rzakir/Documents/fromasus/Runs/dmvd105varyz/'

# =====================================================================#
#########
# ==========FUNCTIONS===================#

# Function "T plus a" for the increase of 1 a
def Tpa(S, a, Za, Zb, qa):
    return qa * (S - a) * ((a + Za) / (S - 1))


# Function "T minus a" for the decrease of 1 a
def Tma(S, a, Za, Zb, qb):
    return qb * a * (((S - a) + Zb) / (S - 1))


# ===============================

# ==========To plot gillespie points for SPD===================#
if gillespie_plot == "true":
    # get all the gillespie files and store in this array
    data_files += [file for file in os.listdir(opdir)]

    xx = 0  # used to change the point symbol and colour
    for file1 in sorted(data_files):
        print(file1)
        # print(float(file1[40:44]) * 200)
        # S = 200 - (float(file1[40:44]) * 200)
        # Z = (float(file1[40:44]) * 200) / 2
        # print("The S is: ", S)
        # print("The Z+ is: ", Z)

        # toadd=int(file1[40:42])*0
        with open(opdir + file1) as f:
            for line in f:
                line.strip()  # Removes \n and spaces on the end
                # print(line.split()[5])
                if line.split()[0] != 'SEED:' and line.split()[0] != 'TS':
                    # value of susceptibles with value A
                    op1.append(int(float(line.split()[5])))
                    # total number of agents --> Sa+Sb+Za+Zb
                    Ntot = int(float(line.split()[5])) + int(float(line.split()[6])) + int(
                        float(line.split()[7])) + int(
                        float(line.split()[8]))
                    # value of Za
                    Za = int(float(line.split()[7]))

            # print("Length od Op1:", len(op1))

            # find the percentage of how many times each Sa and Za occurs in teh gillespie files
            for i in range(min(op1), max(op1)):
                percen = op1.count(i)
                if percen != 0:
                    pointxaxis.append(((i + Za) - (Ntot - (i + Za))) / Ntot)
                    pointyaxis.append((percen / len(op1)) * 1)
            # plot gillespie points to show SPD
            plt.plot(pointxaxis, pointyaxis, symbols[xx], markersize=15, alpha=.8, color=colours[xx])

            if equation_plot != "true":  ####just to print the right legend when displaying only gillespie without eq
                patch.append(mlines.Line2D([], [], color=colours[xx], marker=symbols[xx], markersize=15, label=str(Za)))

            # plt.plot(pointxaxis, pointyaxis, 'o', markersize=15, alpha=.8, color=colours[xx])
            xx = xx + 1

            # reset variables for next file
            pointxaxis = []
            pointyaxis = []
            op1 = []
            op2 = []

# ==========To plot SPD or heatmaps from the equation===================#

if equation_plot == "true":
    # =========CALCULATE Po=====
    for Snum in range(0, len(Slist)):
        print("Snum: ", Snum)
        total_sum = 0
        for k in range(1, Slist[Snum] + 1):
            total_mult = 1
            for j in range(0, k):
                total_mult = total_mult * ((Tpa(Slist[Snum], j, Zplus[Snum], Zminus[Snum], ra)) / (
                    Tma(Slist[Snum], j + 1, Zplus[Snum], Zminus[Snum], rb)) ** q)
                # total_mult = total_mult * (((ra * (Slist[Snum] - j)) / (rb * (j + 1))) * ((j + Zplus[Snum]) / (Slist[Snum] + Zminus[Snum] - j - 1)) ** q)
            total_sum = total_sum + total_mult
        # disp(total_mult);
        Po1 = 1 / (1 + total_sum)
        print(Po1)

        # ============================
        # =======FIND SPD based on Po found=============
        # array to store spd points to plot
        plotmexaxis = []
        plotmeyaxis = []
        for plotting in range(0, Slist[Snum]):
            hans = 1
            for i in range(0, plotting):
                hans = hans * ((Tpa(Slist[Snum], i, Zplus[Snum], Zminus[Snum], ra)) / (
                    Tma(Slist[Snum], i + 1, Zplus[Snum], Zminus[Snum], rb)) ** q)
            #  hans = hans * (((ra * (Slist[Snum] - i)) / (rb * (i + 1))) * ((i + Zplus[Snum]) / (Slist[Snum] + Zminus[Snum] - i - 1)) ** q)
            # plt.plot(plotting, Po1 * hans, 'ro')
            # plt.plot(plotting / Slist[Snum], Po1 * hans, 'o', color=colours[Snum])

            # add teh points to plot SPD
            plotmexaxis.append((plotting + (Zplus[Snum]) - (N - (plotting + (Zplus[Snum])))) / N)
            plotmeyaxis.append(Po1 * hans)

            # plot SPD only when heatmaps are not to be generated
            if heatmaps == "false":
                # plt.plot((plotting + (Zplus[Snum]) - (200 - (plotting + (Zplus[Snum])))) / 200, Po1 * hans,'o', color=colours[Snum])
                plt.plot(plotmexaxis, plotmeyaxis, linewidth=6, color=colours[Snum])

            # print(plotmexaxis)
            # print(plotmeyaxis)

            # to convert probability to numbers and append to plot them based on number of times each number occurs
            if heatmaps == "true":
                for i in range(int(Po1 * hans * 100000)):
                    dump_list_x_points.append((Zplus[Snum] + Zminus[Snum]) / N)
                    dump_list_y_points.append((plotting + (Zplus[Snum]) - (N - (plotting + (Zplus[Snum])))) / N)

        if gillespie_plot == "true":  # just for setting correct legend
            patch.append(mlines.Line2D([], [], linewidth=6, color=colours[Snum], marker=symbols[Snum], markersize=15,
                                       label=str((Zplus[Snum]))))
        if heatmaps == "false":  # just for setting correct legend
            patch.append(mlines.Line2D([], [], linewidth=6, color=colours[Snum], label=str((Zplus[Snum]))))

# print(dump_list_x_points)
# print(dump_list_y_points)

#plotting heatmaps of heatmaps egenration is set to true
if heatmaps == "true":
    plt.hist2d(dump_list_x_points, dump_list_y_points, bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())

# patch.append(
#     mpatches.Patch(Line2D([0], [0], linewidth=3, linestyle='-'), color=colours[Snum], label=str((Zplus[Snum]))))


#==========Formatting the plot====================#

plt.xticks(fontsize=32)
plt.yticks(fontsize=32)

if heatmaps == "true":
    ax = plt.gca()
    ax.set_xlim([0, 1])
    ax.set_ylim([-1, 1])
    ax.margins(0)
    ax.margins(x=0)

if heatmaps == "false":
    plt.xlabel(r'population $X-Y$', fontsize=44)
    plt.ylabel(r'stationary probability distribution', fontsize=44)
    plt.title('Population Evolution: Zealots- QRatio-2.00, DMVD, N=200', fontsize=32)
    legend1 = plt.legend(handles=patch, title='Zealot Proportion', fontsize=32)
    plt.setp(legend1.get_title(), fontsize=32)
else:
    plt.xlabel(r'asocial behavior $z_x+z_y$', fontsize=44)
    plt.ylabel(r'population $X-Y$', fontsize=44)

plt.savefig('images/Heatmaps_GillespieEqDMVDvaryingZealotsQR2.pdf', dpi=300, bbox_inches='tight')

# plt.savefig('images/dmvd_qr2.00_zvary.png', dpi=300, bbox_inches='tight')
plt.show()#generate heatmaps in 4AB- from gillespie