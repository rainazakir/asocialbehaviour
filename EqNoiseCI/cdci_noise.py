# checking program
import matplotlib.pyplot as plt
import glob, os
from pathlib import Path
import math
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib as M
import pickle
plt.rcParams["figure.figsize"] = (25, 18)

colours = ["#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
symbols = ["o", "v", "*", "d", "h", "X", "P", "+"]
patch = []

# array to store gillespie points
op1 = []
op2 = []

#noise = [0.001, 0.005, 0.01, 0.03, 0.055]
plt.xlim(-1, 1)
plt.ylim(0, 0.150)
######


# =======Specify variables for equation to be plotted-if equation_plot set to true=====#
# set qratios
qa = 1
qb = 1

#noise list for equation to plot
#noiselist = [0.012,0.02,0.03,0.04,0.05]
noiselist = [0.01,0.02,0.03,0.04,0.05]
#noiselist = [0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.26,0.27,0.28,0.29,0.3,0.31,0.32,0.33,0.34,0.35,0.36,0.37,0.38,0.39,0.4,0.41,0.42,0.43,0.44,0.45,0.46,0.47,0.48,0.49]

# total number of agents
N = [200]

computePoo = False
patch = []

# array to store formatted gillespie points to be plotted
pointxaxis = []
pointyaxis = []

# =========DIRECTORIES FOR GILLESPIE RUNS-if gillespie_plot set to true=========#

# opdir = 'D:/Simpaperresults/probabilitydistfromGillespieCDCI/datafiles/' # os.getcwd()
# opdir = 'D:/Simpaperresults/cdcinoise2spd/'
opdir = 'D:/Simpaperresults/varyNCDCI/'


useLog = True

# ======GILLESPIE OR NOT=======#
gillespie_plot = False
# =============================#
# ======GILLESPIE OR NOT=======#
equation_plot = "true"
# ==If plotting heatmaps set to true otherwise false will generate SPD==#
heatmaps = True
# =============================#

# =================================================#

###to store heatmap points########
dump_list_x_points = []
dump_list_y_points = []

showDebugMatrix = False
averageTwoMatrixes = True


# =============================
# ==========FUNCTIONS===================

def calculatePoo():
    # Caluclate  To,b+/To,b+1-
    sumTb_Tb = 0
    for k in range(1, n + 1):
        multTb_Tb = 1  # 10**-30
        for b in range(0, k):
            multTb_Tb = multTb_Tb * (Tpb(0, b, n, nn) / Tmb(0, b + 1, n, nn))
        sumTb_Tb = sumTb_Tb + multTb_Tb
    print("To,b+/To,b+1: ", sumTb_Tb)

    sumTj_Tj = 0
    # Calculate Tj,o+/Tj+1,o-
    for a in range(1, n + 1):
        multTj_Tj = 1  # 10**-90
        for j in range(0, a):
            sumTab_Tab = 0
            # Calculate Ta,b+/Ta,b-
            for k in range(1, (n - a) + 1):
                multTab_Tab = 1
                for b in range(0, k):  # TPB= Tab+b
                    multTab_Tab = multTab_Tab * (Tpb(a, b, n, nn) / Tmb(a, b + 1, n, nn))
                sumTab_Tab = sumTab_Tab + multTab_Tab
            multTj_Tj = multTj_Tj * (Tpa(j, 0, n, nn) / Tma(j + 1, 0, n, nn)) * (1 + sumTab_Tab)
            # print(a,j,k,b,( Tpa(j, 0, Za, Zb, n)/Tma(j+1, 0, Za, Zb, n) ) * (1 + sumTab_Tab))
        if math.isinf(multTj_Tj): print('multTj_Tj inf!!!', a, j, k, b, sumTab_Tab)
        sumTj_Tj = sumTj_Tj + multTj_Tj

    print("To,b+/To,b+1-: ", multTb_Tb)
    print("Tj,o+/Tj,j+1-: ", multTj_Tj)
    print("Ta,b+/Ta,b+1-: ", multTab_Tab)

    # Adding up the equation to get Po,o
    Poo = 1 / (1 + sumTb_Tb + sumTj_Tj)
    print("Poo = ", Poo)


# Function "T plus a" for the increase of 1 a , TJo+a
def Tpa(a, b, n, noise):
    # print( qa * ((n - a - b) * (a + (noise * (n - 1)))))
    return qa * ((n - a - b) * (a + (noise * (n - 1))))


# Function "T minus a" for the decrease of 1 a, TJo-a
def Tma(a, b, n, noise):
    return qb * (a * (b + (noise * (n - 1))))


# Function "T plus b" for the increase of 1 b, #TPB= Tab+b, same for three
def Tpb(a, b, n, noise):
    return qb * ((n - a - b) * (b + (noise * (n - 1))))


# Function "T minus b" for the decrease of 1 b,  #TPB= Tab-b, same for three
def Tmb(a, b, n, noise):  # Ta,b-
    return qa * (b * (a + (noise * (n - 1))))


# =============================
#   Calculate Pa,o
# Poo = 1
def calculatePao(a, n, poo):
    multTj_Pao = 1
    # Tj,o+/Tj+1,o-
    for j in range(0, a):
        multTj_Pao = multTj_Pao * ((Tpa(j, 0, n, nn) / 1) / (Tma(j + 1, 0, n, nn)) / 1)
    # print(poo*multTj_Pao)
    return poo * multTj_Pao


# =============================
#   Calculate Pa,o
# Poo = 1
def calculatePao(a, n, poo):
    multTj_Pao = 1
    # Tj,o+/Tj+1,o-
    for j in range(0, a):
        multTj_Pao = multTj_Pao * ((Tpa(j, 0, n, nn) / 1) / (Tma(j + 1, 0, n, nn)) / 1)
    return poo * multTj_Pao


def calculatePob(b, n, poo):
    multTj_Pao = 1
    # Tj,o+/Tj+1,o-
    for j in range(0, b):
        multTj_Pao = multTj_Pao * ((Tpb(0, j, n, nn) / 1) / (Tmb(0, j + 1, n, nn)) / 1)
    return poo * multTj_Pao

def calculatePaoLog(a, n, poo):
    multTj_Pao = 0
    for j in range(0, a):
        multTj_Pao = multTj_Pao + np.log(Tpa(j, 0, n, nn)) - np.log(Tma(j + 1, 0, n, nn))
    return multTj_Pao


def calculatePobLog(b, n, poo):
    multTj_Pao = 0
    for j in range(0, b):
        multTj_Pao = multTj_Pao + np.log(Tpb(0, j, n, nn)) - np.log(Tmb(0, j + 1, n, nn))
    return multTj_Pao

def findPadiff(myListA, qa, qb):
    for a in range(0, n + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = 0
        pao = (calculatePao(a, n, Poo))
        for b in range(0, n - a + 1):  # sum b-->S-a
            multTaj_Taj = 1
            for j in range(0, b):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj * (Tpb(a, j, n, nn) / Tmb(a, j + 1, n, nn))
            ProbabilityA_B = pao * multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            myListA.append([a, b, ProbabilityA_B])
        #############################################

def findPabOnPaoLog(allProbFromA, qa, qb):
    for a in range(0, n + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = np.float128(0)
        logpao = calculatePaoLog(a, n, Poo)
        for b in range(0, n - a + 1):  # sum b-->S-a
            multTaj_Taj = np.float128(0)
            for j in range(0, b):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj + np.log(Tpb(a, j, n, nn)) - np.log(Tmb(a, j + 1, n, nn))
            ProbabilityA_B = logpao + multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            allProbFromA.append([a, b, ProbabilityA_B])


def findPbdiff(myListB, qa, qb):
    for b in range(0, n + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = 0
        pob = (calculatePob(b, n, Poo))
        for a in range(0, n - b + 1):  # sum b-->S-a
            multTaj_Taj = 1
            for j in range(0, a):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj * (Tpa(j, b, n, nn) / Tma(j + 1, b, n, nn))
            ProbabilityA_B = pob * multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            myListB.append([a, b, ProbabilityA_B])


def findPabOnPobLog(allProbsFromB, qa, qb):
    for b in range(0, n + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = np.float128(0)
        logpob = calculatePobLog(b, n, Poo)
        for a in range(0, n - b + 1):  # sum b-->S-a
            multTaj_Taj = np.float128(0)
            for j in range(0, a):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj + np.log(Tpa(j, b, n, nn)) - np.log(Tma(j + 1, b, n, nn))
            ProbabilityA_B = logpob + multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            allProbsFromB.append([a, b, ProbabilityA_B])


heatMatrix = []
if equation_plot == "true":

# =========================
    for numn, nn in enumerate(noiselist):
        for num, n in enumerate(N):
            print("Num of agents = " + str(n))
            # print("Num of zealots = " + str(Z) + " = " + str(Za) + " + " + str(Zb))

            # print(n,)

            # =========CALCULATE Po,o=====
            if computePoo:
                calculatePoo()
            else:
                Poo = 1

            # =======FIND SPD(Pa,b)=============
            # This is the part where I needed summation, right?
            # SumTaj_Taj = 0
            # Ta,j+/Ta,j+1
            pastar = []

            padiff = {}
            pbdiff = {}
            pbavg = {}
            # to store the Pa,b
            myListA = []
            myListB = []
            listAvg = []

            # to store the Pa,b
            allProbsFromA = []
            if averageTwoMatrixes: allProbsFromB = []
            allProbsAvg = []
            if showDebugMatrix:
                matrixVals = [[0] * (n + 1) for _ in range(n + 1)]

            # compute all teh probabilities for P_a_b
            if useLog:
                findPabOnPaoLog(allProbsFromA, qa, qb)
                if averageTwoMatrixes: findPabOnPobLog(allProbsFromB, qa, qb)
            else:
                findPadiff(allProbsFromA, qa, qb)
                if averageTwoMatrixes: findPbdiff(allProbsFromB, qa, qb)

            # compute the average value between values of allProbsFromA and allProbsFromB
            if averageTwoMatrixes:
                for i in allProbsFromA:
                    for j in allProbsFromB:
                        if i[0] == j[0] and i[1] == j[1]:
                            # print( "pos [" + str(i[0]) + "," + str(i[1]) + "] = " + str(i[2]) + " and " + str(j[2]) + " diff=" + str(i[2]-j[2]) )
                            if useLog:
                                allProbsAvg.append([i[0], i[1], np.exp((i[2] + j[2]) / 2.0)])
                                if showDebugMatrix:
                                    matrixVals[i[0]][i[1]] = np.exp((i[2] + j[2]) / 2.0)
                                    # matrixVals[ int(np.floor(i[0]/3)) ][ int(np.floor(i[1]/3)) ] += np.exp((i[2] + j[2]) / 2.0)
                            else:
                                allProbsAvg.append([i[0], i[1], (i[2] + j[2]) / 2.0])
                                if showDebugMatrix:
                                    matrixVals[i[0]][i[1]] = (i[2] + j[2]) / 2.0
            else:
                if useLog:
                    for i in allProbsFromA:
                        allProbsAvg.append([i[0], i[1], np.exp(i[2])])
                        if showDebugMatrix:
                            matrixVals[i[0]][i[1]] = np.exp(i[2])
                else:
                    allProbsAvg = allProbsFromA
                    if showDebugMatrix:
                        for i in allProbsFromA:
                            matrixVals[i[0]][i[1]] = i[2]

            if showDebugMatrix:
                # for i in matrixVals:
                #     print(i)
                plt.imshow(matrixVals, cmap='hot', interpolation='nearest')
                plt.colorbar()
                plt.show()
                # exit()

            for i in allProbsAvg:
                number = i[0] - i[1]
                # number = i[0]
                if pbavg.get(number) is not None:
                    # print("there is already a number in this index")
                    pbavg[number] = pbavg.get(number) + i[2]
                else:
                    # print("this is the first number for this difference")
                    pbavg[number] = i[2]

            # normalize the probabilities
            summedVals = sum(pbavg.values())
            # print(summedVals)
            for d, v in pbavg.items():
                pbavg[d] = v / summedVals

            # sort the dictionary containing X points and Y points
            listx_y = sorted(pbavg.items())
            # listx_y = sorted(ret.items())
            # listB = sorted(pbdiff.items())

            # separate them into lists
            x, y = zip(*listx_y)
         #   print(x)
         #   print(y)
            # for legend of the plot

            y = list(y)
            #print(y)
            if gillespie_plot:
                patch.append(
                    mlines.Line2D([], [], linewidth=6, color=colours[Snum], marker=symbols[Snum], markersize=15,
                                  label=str(int(Z))))
            if not heatmaps:
                #########plot the equation
                plt.plot([a / n for a in x], y, linewidth=6, color=colours[Snum])
                #plt.yscale('log')
                patch.append(mlines.Line2D([], [], linewidth=6, color=colours[Snum], label=str(int(Z))))
            # patch.append(mpatches.Patch(Line2D([0], [0], linewidth=3, linestyle='-'), color=colours[numn],label="Noise:" + str(nn) + " " + str(symbol[num])))

            ###if heatmaps is set to true
            if heatmaps:
                line = [0] * (n * 2 + 1)
                heatMatrix.append(line)
                for x, y in listx_y:
                    print(x,n)
                    heatMatrix[n][x + n] = y
            if heatmaps and gillespie_plot:
                for j, val in enumerate(y):
                    if not math.isnan(val):
                        for i in range(int(np.round(val * 1000000))):
                            dump_list_y_points.append(x[j] / n)
                            dump_list_x_points.append(Za + Zb / n)
                    else:
                        print("nan")
                # for i in range(int(3)):
                #  dump_list_y_points.append(x[j] / n)
                #  dump_list_x_points.append((Za + Zb) / n)
"""
if heatmaps:
    with open("test.txt", "wb") as fp:   #Pickling
       pickle.dump(dump_list_x_points, fp)
    with open("test1.txt", "wb") as fp:   #Pickling
       pickle.dump(dump_list_y_points, fp)
    plt.hist2d(dump_list_x_points, dump_list_y_points, bins=[46, 36], cmap='Reds', norm=M.colors.SymLogNorm(linthresh="0.03"))
"""
if heatmaps:
    # plt.hist2d(dump_list_x_points, dump_list_y_points, bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())
    for i in heatMatrix:
        print("yhis line",i)
#        with open('matrixfile2.txt', 'a') as f:
 #         print(i, file=f)

    heatMatrixFull = []
    for z in np.arange(0, 1, 2.0 / n):
        found = False
        for zi, zVal in enumerate(noiselist):
            if np.abs(zVal - z) < 0.00001:
                heatMatrixFull.append(heatMatrix[zi])
                found = True
                break
        if not found:
            heatMatrixFull.append([0] * (n * 2 + 1))
            print("On the x-axis the valsue " + str(z) + " has not been found.")
    heatMatrixFull = list(reversed(list(zip(*heatMatrixFull))))
    #print(heatMatrixFull)
    #plt.hist2d( heatMatrixFull[:,0], heatMatrixFull[:,1], bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())

    plt.imshow(heatMatrixFull, cmap='Reds', norm=M.colors.LogNorm(), aspect='auto')
if gillespie_plot:

    data_files = []
    data_files += [file for file in os.listdir(opdir)]
    print(data_files)

    xx = 0

    for file1 in data_files:

        with open(opdir + file1) as f:
            for line in f:
                line.strip()  # Removes \n and spaces on the end
                if line.split()[0] != 'SEED:' and line.split()[0] != 'TS':
                    # get X-Y
                    op1.append((int(float(line.split()[4])) - (int(float(line.split()[5])))))
                    Ntot = int(float(line.split()[3])) + int(float(line.split()[4])) + int(float(line.split()[5])) + int(float(line.split()[6]))+int(float(line.split()[7]))
                    # op2.append(int(line.split()[3]))
                    Za = int(float(line.split()[6]))
                    Zb = int(float(line.split()[7]))
                    # op2.append(int(line.split()[3]))
            print("Lenngth od Op1:", len(op1))
            for i in range(min(op1), max(op1) + 1):
                percen = op1.count(i)

                pointxaxis.append((i / Ntot))
                pointyaxis.append(float((percen / len(op1))) * 1)

            plt.plot(pointxaxis, pointyaxis, symbols[xx], markersize=15, alpha=.8, color=colours[xx])
            if equation_plot != "true":
                patch.append(mlines.Line2D([], [], color=colours[xx], marker=symbols[xx], markersize=15,
                                           label=str(Za+Zb)))
            xx = xx + 1

            # reset variables for next file
            pointxaxis = []
            pointyaxis = []
            op1 = []
            op2 = []


#legend1 = plt.legend(handles=patch, title='Noise', fontsize=32)

#plt.setp(legend1.get_title(), fontsize=32)
#plt.title('CDCI Noise Type 2 N=200')

# plt.show()
# plt.savefig(name, dpi=1200)
plt.xticks(fontsize=32)
plt.yticks(fontsize=32)

plt.xlabel(r'population $X-Y$', fontsize=44)
plt.ylabel(r'stationary probability distribution', fontsize=44)
#plt.savefig('images/spd_cdci_vary_noise2_n200.pdf', dpi=300, bbox_inches='tight')
plt.show()