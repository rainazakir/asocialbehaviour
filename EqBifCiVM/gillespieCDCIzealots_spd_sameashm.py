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
from scipy import stats
from scipy.stats import binned_statistic_2d
from itertools import groupby
from operator import itemgetter

plt.rcParams["figure.figsize"] = (25, 18)
plt.rcParams.update({
    "figure.facecolor":  (1.0, 1.0, 1.0, 0),  # red   with alpha = 30%
    "axes.facecolor":    (1.0, 1.0, 1.0, 1),  # white with alpha = 100%-->no transparency
    "savefig.facecolor": (1.0, 1.0, 1.0, 0),  # blue  with alpha = 20%
})

colours = ["#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
colours = ["#000000","#3DB7E9", "#F748A5", "#359B73","#e69f00","#2271B2","#f0e442","#d55e00"]

symbols = ["o", "v", "*", "d", "h", "X", "P", "+"]
patch = []

# ======GILLESPIE OR NOT=======#
gillespie_plot = False
# =============================#
# ======Equation OR NOT=======#
equation_plot = True
# ==If plotting heatmaps set to true otherwise false will generate SPD==#
heatmaps = False
# =============================#


# to store gillespie values
op1 = []
op2 = []

# to store gillespie points to plot
pointxaxis = []
pointyaxis = []
# to store gillespie files to read
listFiles = []

plt.xlim(-1, 1)
#plt.ylim(0.000000000000000000000000000000000000000008, 0.85)

# specify the qratios, ra is changed to vary qratio for agents A and Za
qa = 1.05
qb = 1

x = []
y = []
######
# =========DIRECTORIES FOR GILLESPIE RUNS-if gillespie_plot set to true=========#
# opdir = 'D:/Simpaperresults/Runs/cdci2.0/'
# opdir = '/content/drive/MyDrive/cdci105varyz/'
opdir = 'D:/Simpaperresults/Runs/cdci105varyz/'
# opdir = '/Users/rzakir/Documents/fromasus/Runs/cdci2.0/'

# ===============================


# =======Specify variables for equation to be plotted-if equation_plot set to true=====#
N = [100]
# specify the Zealots (Za+Zb in percentage)
#Zproportion = [0.1, 0.2, 0.3, 0.5, 0.8, 0.9]
Zproportion = [0.1,0.2,0.5,0.9]
#Zproportion = [0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.26,0.27,0.28,0.29,0.3,0.31,0.32,0.33,0.34,0.35,0.36,0.37,0.38,0.39,0.4,0.41,0.42,0.43,0.44,0.45,0.46,0.47,0.48,0.49,0.5,0.51,0.52,0.53,0.54,0.55,0.56,0.57,0.58,0.59,0.6,0.61,0.62,0.63,0.64,0.65,0.66,0.67,0.68,0.69,0.7,0.71,0.72,0.73,0.74,0.75,0.76,0.77,0.78,0.79,0.8,0.81,0.82,0.83,0.84,0.85,0.86,0.87,0.88,0.89,0.9,0.91,0.92,0.93,0.94,0.95,0.96,0.97,0.98,0.99]
Sproportion = [1 - z for z in Zproportion]
computePoo = False
useLog = True
showDebugMatrix = False
averageTwoMatrixes = True

# =================================================#

###to store heatmap points########
dump_list_x_points = []
dump_list_y_points = []


# ==========FUNCTIONS===================

def findPoo():
    # Caluclate  To,b+/To,b+1-
    sumTb_Tb = 0
    for k in range(1, S + 1):
        multTb_Tb = 1  # 10**-30
        for b in range(0, k):
            multTb_Tb = multTb_Tb * (Tpb(0, b, Za, Zb, n, qb) / Tmb(0, b + 1, Za, Zb, n, qa))
        sumTb_Tb = sumTb_Tb + multTb_Tb
    print("To,b+/To,b+1: ", sumTb_Tb)

    sumTj_Tj = 0
    # Calculate Tj,o+/Tj+1,o-
    for a in range(1, S + 1):
        multTj_Tj = 1  # 10**-90
        for j in range(0, a):
            sumTab_Tab = 0
            # Calculate Ta,b+/Ta,b-
            for k in range(1, (S - a) + 1):
                multTab_Tab = 1
                for b in range(0, k):
                    multTab_Tab = multTab_Tab * (Tpb(a, b, Za, Zb, n, qb) / Tmb(a, b + 1, Za, Zb, n, qa))
                sumTab_Tab = sumTab_Tab + multTab_Tab
            multTj_Tj = multTj_Tj * (Tpa(j, 0, Za, Zb, n, qa) / Tma(j + 1, 0, Za, Zb, n, qb)) * (1 + sumTab_Tab)
            # print(a,j,k,b,( Tpa(j, 0, Za, Zb, n)/Tma(j+1, 0, Za, Zb, n) ) * (1 + sumTab_Tab))
        if math.isinf(multTj_Tj): print('multTj_Tj inf!!!', a, j, k, b, sumTab_Tab)
        sumTj_Tj = sumTj_Tj + multTj_Tj

    print("To,b+/To,b+1-: ", multTb_Tb)
    print("Tj,o+/Tj,j+1-: ", multTj_Tj)
    print("Ta,b+/Ta,b+1-: ", multTab_Tab)

    # Adding up the equation to get Po,o
    Poo = 1 / (1 + sumTb_Tb + sumTj_Tj)
    return Poo


# Function "T plus a" for the increase of 1 a
def Tpa(a, b, za, zb, n, qualityofa):
    return qualityofa * ((a + za) / (n - 1)) * (n - za - zb - a - b)


# Function "T minus a" for the decrease of 1 a
def Tma(a, b, za, zb, n, qualityofb):
    return qualityofb * ((b + zb) / (n - 1)) * a


# Function "T plus b" for the increase of 1 b
def Tpb(a, b, za, zb, n, qualityofb):
    return qualityofb * ((b + zb) / (n - 1)) * (n - za - zb - a - b)


# Function "T minus b" for the decrease of 1 b
def Tmb(a, b, za, zb, n, qualityofa):
    return qualityofa * ((a + za) / (n - 1)) * b


def calculatePao(a, za, zb, n, poo, qualityofa, qualityofb):
    multTj_Pao = 1
    # Tj,o+/Tj+1,o-
    for j in range(0, a):
        multTj_Pao = multTj_Pao * (Tpa(j, 0, za, zb, n, qualityofa) / Tma(j + 1, 0, za, zb, n, qualityofb))
    return poo * multTj_Pao


def calculatePob(b, za, zb, n, poo, qualityofa, qualityofb):
    multTj_Pao = 1
    # Tj,o+/Tj+1,o-
    for j in range(0, b):
        multTj_Pao = multTj_Pao * (Tpb(0, j, za, zb, n, qualityofb) / Tmb(0, j + 1, za, zb, n, qualityofa))
    return poo * multTj_Pao


def calculatePaoLog(a, za, zb, n, qualityofa, qualityofb):
    multTj_Pao = 0
    for j in range(0, a):
        multTj_Pao = multTj_Pao + np.log(Tpa(j, 0, za, zb, n, qualityofa)) - np.log(
            Tma(j + 1, 0, za, zb, n, qualityofb))
    return multTj_Pao


def calculatePobLog(b, za, zb, n, qualityofa, qualityofb):
    multTj_Pao = 0
    for j in range(0, b):
        multTj_Pao = multTj_Pao + np.log(Tpb(0, j, za, zb, n, qualityofb)) - np.log(
            Tmb(0, j + 1, za, zb, n, qualityofa))
    return multTj_Pao


def findPadiff(allProbFromA, qa, qb):
    for a in range(0, S + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = 0
        pao = (calculatePao(a, Za, Zb, n, Poo, qa, qb))
        for b in range(0, S - a + 1):  # sum b-->S-a
            multTaj_Taj = 1
            for j in range(0, b):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj * (Tpb(a, j, Za, Zb, n, qb) / Tmb(a, j + 1, Za, Zb, n, qa))
            ProbabilityA_B = pao * multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            allProbFromA.append([a, b, ProbabilityA_B])


def findPabOnPaoLog(allProbFromA, S, qa, qb):
    for a in range(0, S + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = np.float128(0)
        logpao = calculatePaoLog(a, Za, Zb, n, qa, qb)
        for b in range(0, S - a + 1):  # sum b-->S-a
            multTaj_Taj = np.float128(0)
            for j in range(0, b):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj + np.log(Tpb(a, j, Za, Zb, n, qb)) - np.log(Tmb(a, j + 1, Za, Zb, n, qa))
            ProbabilityA_B = logpao + multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            allProbFromA.append([a, b, ProbabilityA_B])


def findPbdiff(allProbsFromB, qa, qb):
    for b in range(0, S + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = 0
        pob = (calculatePob(b, Za, Zb, n, Poo, qa, qb))
        for a in range(0, S - b + 1):  # sum b-->S-a
            multTaj_Taj = 1
            for j in range(0, a):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj * (Tpa(j, b, Za, Zb, n, qa) / Tma(j + 1, b, Za, Zb, n, qb))
            ProbabilityA_B = pob * multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            allProbsFromB.append([a, b, ProbabilityA_B])


def findPabOnPobLog(allProbsFromB, S, qa, qb):
    for b in range(0, S + 1):  # j=0--> a-1 inside Poo=Pao
        ProbabilityA_B = np.float128(0)
        logpob = calculatePobLog(b, Za, Zb, n, qa, qb)
        for a in range(0, S - b + 1):  # sum b-->S-a
            multTaj_Taj = np.float128(0)
            for j in range(0, a):  # Taj+b/Taj+1-b
                multTaj_Taj = multTaj_Taj + np.log(Tpa(j, b, Za, Zb, n, qa)) - np.log(Tma(j + 1, b, Za, Zb, n, qb))
            ProbabilityA_B = logpob + multTaj_Taj  # Pa,b=    Pao*j-->b-1*mulTaj
            if (a == 0 and b == 0):
                ProbabilityA_B = 0
            allProbsFromB.append([a, b, ProbabilityA_B])

def binArray(data, axis, binstep, binsize, func=np.nanmean):
    data = np.array(data)
    dims = np.array(data.shape)
    argdims = np.arange(data.ndim)
    argdims[0], argdims[axis]= argdims[axis], argdims[0]
    data = data.transpose(argdims)
    data = [func(np.take(data,np.arange(int(i*binstep),int(i*binstep+binsize)),0),0) for i in np.arange(dims[axis]//binstep)]
    data = np.array(data).transpose(argdims)
    return data
# =============================

# =========================
heatMatrix = []
if equation_plot:
    for num, n in enumerate(N):
        print("Num of agents = " + str(n))
        for Snum in range(0, len(Sproportion)):
            Z = Zproportion[Snum] * n
            Za = int(Z // 2)
            Zb = int(Z // 2)
            print("Num of zealots = " + str(Z) + " = " + str(Za) + " + " + str(Zb))
            S = int(n - Za - Zb)
            print(n, Z, Za, Zb, S)

            # =========CALCULATE Po,o=====
            if computePoo:
                Poo = findPoo()
                print("Poo = ", Poo)
            else:
                Poo = 1

            # =======FIND SPD(Pa,b)=============
            # This is the part where I needed summation, right?
            # SumTaj_Taj = 0
            # Ta,j+/Ta,j+1
            padiff = {}
            pbdiff = {}
            pbavg = {}
            # to store the Pa,b
            allProbsFromA = []
            if averageTwoMatrixes: allProbsFromB = []
            allProbsAvg = []
            if showDebugMatrix:
                #matrixVals = [[0] * (n + 1) for _ in range(n + 1)]
                matrixVals = [[0] * (101) for _ in range(101)]########################################################

            # compute all teh probabilities for P_a_b
            if useLog:
                findPabOnPaoLog(allProbsFromA, S, qa, qb)
                if averageTwoMatrixes: findPabOnPobLog(allProbsFromB, S, qa, qb)
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
                                allProbsAvg.append([i[0], i[1], np.exp((i[2] + j[2]) / 2.0)])    #the original
                                #allProbsAvg.append([ int(np.floor(i[0]/2)) , int(np.floor(i[1])) ,np.exp((i[2] + j[2]) / 2.0)])
                                if showDebugMatrix:
                                    #matrixVals[i[0]][i[1]] = np.exp((i[2] + j[2]) / 2.0)
                                    # matrixVals[ int(np.floor(i[0]/2)) ][ int(np.floor(i[1]/2)) ] += np.exp([i][j])###################################
                                    matrixVals[ int(np.floor(i[0]/2)) ][ int(np.floor(i[1]/2)) ] += np.exp((i[2] + j[2]) / 2.0)
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
              #  for i in matrixVals:
               #     print(i)
                plt.imshow(matrixVals, cmap='hot', interpolation='nearest')
                #plt.colorbar()
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
            #print(np.matrix(listx_y))

            # separate them into lists
            x, y = zip(*listx_y)

           # sums, edges = np.histogram(x, bins=10, weights=y)
           # counts, _ = np.histogram(x, bins=10)
           # revbinnedstars = sums / counts
           # print(np.matrix(sums))

           # print(y)
            if gillespie_plot:
                patch.append(
                    mlines.Line2D([], [], linewidth=6, color=colours[Snum], marker=symbols[Snum], markersize=15,
                                  label=str(int(Z))))
            if not heatmaps:
                #########plot the equation
                plt.plot([a / n for a in x], y, linewidth=17, color=colours[Snum])
               # plt.yscale('log')
                patch.append(mlines.Line2D([], [], linewidth=9, color=colours[Snum], label=str(int(Z))))
            # patch.append(mpatches.Patch(Line2D([0], [0], linewidth=3, linestyle='-'), color=colours[numn],label="Noise:" + str(nn) + " " + str(symbol[num])))

            ###if heatmaps is set to true
            if heatmaps:
                line = [0] * (n * 2 + 1)
               ## binnedMatrix = [ [0]*(n+1)/binsize for _ in range(n+1)/binsize ]
                heatMatrix.append(line)
                for x, y in listx_y:
                    heatMatrix[Snum][x + n] = y
                   # matrixVals[ int(np.floor( i /binsize)) ][ j ] += matrixVals[i][j]
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



if heatmaps:
    # plt.hist2d(dump_list_x_points, dump_list_y_points, bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())
    #for i in heatMatrix:
        #print("yhis line",i)
        #with open('matrixfile2.txt', 'a') as f:
        #  print(i, file=f)

    heatMatrixFull = []
    for z in np.arange(0, 1, 2.0 / n):
        found = False
        for zi, zVal in enumerate(Zproportion):
            if np.abs(zVal - z) < 0.00001:
                heatMatrixFull.append(heatMatrix[zi])
                found = True
                break
        if not found:
            heatMatrixFull.append([0] * (n * 2 + 1))
            print("On the x-axis the value " + str(z) + " has not been found.")
    heatMatrixFull = list(reversed(list(zip(*heatMatrixFull))))
   
    print(np.array(heatMatrixFull).shape)
    heatMatrixFull= np.delete(heatMatrixFull, 0, 0)
    print(np.array(heatMatrixFull).shape)
   # binnedMatrix = []

    N, M = np.array(heatMatrixFull).shape
    assert N % 2 == 0
    assert M % 2 == 0
   # binnedMatrix =[[0]*N//2 for i in range(M//2)]
    binnedMatrix = np.empty((N//2, M))
    for i in range(N//2):
      for j in range(M):
         binnedMatrix[i,j] = heatMatrixFull[2*i:2*i+2, j].sum()
         #binnedMatrix[i,j] = heatMatrixFull[2*i:2*i+2, 2*j:2*j+2].sum()
    """
    for i in range(N//2):
      for j in range(M//2):
        # binnedMatrix[i][j] = heatMatrixFull[2*i:2*i+2,(2*j:2*j+2).sum()]
         #binnedMatrix[i,j] = heatMatrixFull[2*i:2*i+2, 2*j:2*j+2].sum()
    """
   # binnedMatrix = [[0]*(n+1)/2 for _ in range(n+1)/2 ]
    #for i in range(len(heatMatrixFull)):
    #  for j in range(len(heatMatrixFull[i])):
     #   binnedMatrix[int(np.floor(i /2)) ][ j ] += heatMatrixFull[i][j]
    

    #plt.hist2d( x,y, bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())
    #bin_data_mean = binArray(heatMatrixFull, 0, 10, 5, np.mean)
    #plt.hist2d( heatMatrixFull[:,0], heatMatrixFull[:,1], bins=[99, 36], cmap='Reds', norm=M.colors.LogNorm())
   # print(np.matrix(binnedMatrix))
    plt.imshow(binnedMatrix, cmap='Reds',aspect='auto')
   # plt.imshow(list(binnedMatrix), cmap='Reds',norm=M.colors.LogNorm(), aspect='auto')

if gillespie_plot:

    data_files = []
    data_files += [file for file in os.listdir(opdir)]
    # varibale to iterate colour list
    legend = []
    xx = 0

    fileno = 0
    for file1 in sorted(data_files):

        #  print("The S is: ", S)
        # toadd=int(file1[40:42])*0
        with open(opdir + file1) as f:
            for line in f:
                line.strip()  # Removes \n and spaces on the end
                if line.split()[0] != 'SEED:' and line.split()[0] != 'TS':
                    # get X-Y
                    op1.append((int(float(line.split()[4])) - (int(float(line.split()[5])))))
                    Ntot = int(float(line.split()[3])) + int(float(line.split()[4])) + int(
                        float(line.split()[5])) + int(float(line.split()[6])) + int(float(line.split()[7]))
                    # op2.append(int(line.split()[3]))
                    Za = int(float(line.split()[6]))
                    Zb = int(float(line.split()[7]))

            print("Lenngth od Op1:", len(op1))
            for i in range(min(op1), max(op1) + 1):
                percen = op1.count(i)

                pointxaxis.append((i / Ntot))
                pointyaxis.append(float((percen / len(op1))) * 1)

            plt.plot(pointxaxis, pointyaxis, symbols[xx], markersize=18, alpha=.8, color=colours[xx])

            if not equation_plot:
                patch.append(mlines.Line2D([], [], color=colours[xx], marker=symbols[xx], markersize=15,
                                           label=str(Za + Zb)))
            xx = xx + 1
            # rest variables
            print(pointyaxis)
            pointxaxis = []
            pointyaxis = []
            op1 = []
            op2 = []

# Y.append(values[1])

#plt.legend(handles=patch)
# plt.xticks([-1, -0.5, 0, 0.5, 1])
plt.xticks(fontsize=60)
# plt.yticks([])8
plt.yticks(fontsize=60)

# plt.xlabel(r'population $X-Y$', fontsize=44)
# plt.ylabel(r'stationary probability distribution', fontsize=44)
if not heatmaps:
    plt.xlabel(r'$X-Y$', fontsize=80)
    plt.ylabel(r'spd', fontsize=80)
   # legend1 = plt.legend(handles=patch, title='Zealot Proportion', fontsize=40)
    #plt.setp(legend1.get_title(), fontsize=38)
    plt.yticks([])
    ax = plt.gca()  # grab the current axis
    ax.set_xticks([-1,0,1])  # choose which x locations to have ticks
if heatmaps:
    ax = plt.gca()
    # ax.set_xlim([0, 1])
    # ax.set_ylim([-1, 1])
    ax.margins(0)

    plt.xlabel(r'asocial behavior $z_x+z_y$', fontsize=54)
    plt.ylabel(r'population $X-Y$', fontsize=54)
# plt.title('Population Evolution: Zealots- QRatio-1.05, CDCI, N=200', fontsize=32)


# plt.show()
plt.savefig('ncc22_eq_cdci_qr105_zvary_insetfig4.png', dpi=300, bbox_inches='tight')

plt.show()




#used to generate insets