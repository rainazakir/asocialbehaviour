'''
Created on 24 Jun 2016
@author: Andreagiovanni Reina.
University of Sheffield, UK.
'''

# import RungeKutta.bestOfN

import numpy as np
import sys
import os
import copy
# import matplotlib.pyplot as plt
#from plotting import plotit

DEBUG = False
listA = []
listB = []
opdir = '/scratch/data2/'  # os.getcwd()
data_files = []
statusofNA = "none"
time1 = "none"
time2 = "none"
totaltime = 0
alltimes = []
totallist = []


#################FUNCTIONS#########################
def gillespieStep(state, N, gammas, alphas, rhos, sigmas, vectorsOfChange, timeLeft):
    # Computing the probabilities of change
    probabilitiesOfChange = []
    ## A -(x)-> B
    ## x=5   1/s
    ## when the change will happen?
    ## 0.2s  # on average for one A
    ## but you have many A
    ## a is the number of guys in state A
    ## population level transition rate = a*x
    ## A -(x)-> B
    ## B -(y)-> A
    ## B+A -(y)-> A+A
    ## sum of all rates at population level Z = a*x + b*y + b*a*y / (N)^(number of agents involved minus 1)
    ## (N)^(number of agents involved minus 1) --> it means that for
    ###### number of agents involved=1 ---> a*x/ (N^0)  = a*x/1 = a*x
    ###### number of agents involved=2 ---> b*a*y/ (N^1)  = b*a*x/N
    ## sum of all rates at population level Z = a*x + b*y + b*a*y/N
    ## from Z we compute WHEN the change will happen
    ## what about which change (that is, if x or y)?
    ## probabilitiesOfChange = [ a*x , b*y , b*a*x/N ]
    numOptions = int((len(state) - 1) / 2)
    for i in range(0, numOptions):  # PAY ATTENTION THAT i IS NOT THE CORRECT state[i] BUT IT MUST BE state[i+1], WHILE WORKS FOR gammas[i], alphas[i], rhos[i]
        # Discovery
        # probabilitiesOfChange.append( state[0]*gammas[i]) # U -> A and U -> B
        # Abandonment
        # probabilitiesOfChange.append( state[i+1]*alphas[i] )# A -> U and B -> U
        ############Recruitment###################
        probabilitiesOfChange.append(state[0] * state[i + 1] * rhos[i] / (N - 1))  # U + A -> A + A
        #############Cross-inhibition#############
        for j in range(0, numOptions):
            if (i == j):
                continue
            probabilitiesOfChange.append(state[i + 1] * state[j + 1] * sigmas[j] / (N - 1))
        ########Recruitment from zealot###########
        probabilitiesOfChange.append(state[0] * state[i + numOptions + 1] * rhos[i] / (N - 1))  # U + ZA -> A + ZA
        ########Cross-inhibition from zealot#######
        for j in range(0, numOptions):
            if (i == j):
                continue
            probabilitiesOfChange.append(
                state[i + 1] * state[j + numOptions + 1] * sigmas[j] / (N - 1))  # A + ZJ -> U + ZJ
        ###############Noise:
        probabilitiesOfChange.append(state[i + 1] * noisetype1)  # this is same for both cdci
        ###############Noise:
        probabilitiesOfChange.append(state[i + 1] * noisetype2[0])  # this is same for both cdci
        ##############Noise for Discovery:
        probabilitiesOfChange.append(state[0] * noisetype2[1])  # U -> A and U -> B

    #    print("PoC:", probabilitiesOfChange)

    probSum = sum(probabilitiesOfChange)
    timeInterval = np.random.exponential(1 / probSum);
    # The transition happens after the maximum time length, so we do not include it and terminate the step
    if timeInterval > timeLeft:
        return True, timeLeft

    # Selecting the occurred reaction in a randomly, proportionally to their probabilities
    bottom = 0.0
    # Get a random between [0,1) (but we don't want 0!)
    reaction = 0.0
    while (reaction == 0.0):
        reaction = np.random.random_sample()

    ## probabilitiesOfChange = [ 0.5 , 0.7 , 0.1 ]  ->> WHICH? the first with prob 0.5/(0.5+0.7+0) and second with prob 0.7/(0.5+0.7+0)
    ## probabilitiesOfChange = [ 0.38 , 0.54 , 0.08 ]  ->> WHICH? the first with prob 0.5/(0.5+0.7+0) and second with prob 0.7/(0.5+0.7+0)
    ## random is 0.6
    ## pick 1 if random <0.38
    ## pick 2 if 0.38 < random < (0.38+0.54)
    ## pick 3 if (0.38+0.54) < random < (0.38+0.54+0.08)
    # Normalising probOfChange in the range [0,1]
    probabilitiesOfChange = [pc / probSum for pc in probabilitiesOfChange]
    index = -1
    for i, prob in enumerate(probabilitiesOfChange):
        if (reaction >= bottom and reaction < (bottom + prob)):
            index = i
            break
        bottom += prob
        # print(i, prob)

    #     print("timeInterval is", timeInterval)
    #     print("reaction is", reaction)
    #     print("index is ", index)

    if (index == -1):
        print("Transition not found. Error in the algorithm execution.")
        # sys.exit()
    #     print(state)
    #    print(vectorsOfChange[index])
    state += np.array(vectorsOfChange[index])
    #    print(state)
    return False, timeInterval


def runGillespie(state, T, N, gammas, alphas, rhos, sigmas, rnd_seed, finalStateFile, temporalEvolution, plot_evo, extraLog, quorum):
    np.random.seed(rnd_seed)
    n = len(gammas)
    state = np.array(state)
    t = 0
    # if DEBUG:
    #    print("t: ", t, "state: ", state)

    # Opening output file if needed
    if (temporalEvolution != "none"):
        os.makedirs(os.path.dirname(temporalEvolution), exist_ok=True)
        evoStream = open(temporalEvolution, "w+")
        out = str(t) + "\t" + '\t'.join(str(x) for x in state) + "\t" + str(noisevalue) + "\n"
        evoStream.write(out)

    # Creating the list of vector of change
    vectorsOfChange = []
    for i in [1, 2]:
        if (i == 1):  # pop A
            # [U A B]
            plus = [-1, 1, 0, 0, 0]  # the important thing is that sum is ZERO
            negative = [1, -1, 0, 0, 0]
            noisetrans1 = [0, -1, 1, 0, 0]
            noisetrans2 = [1, -1, 0, 0, 0]
            noisediscovery = [-1, 1, 0, 0, 0]
        if (i == 2):  # pop B
            plus = [-1, 0, 1, 0, 0]
            negative = [1, 0, -1, 0, 0]
            noisetrans1 = [0, 1, -1, 0, 0]
            noisetrans2 = [1, 0, -1, 0, 0]
            noisediscovery = [-1, 0, 1, 0, 0]

        #         # Positive change
        #         plus = [-1] + [0]*n
        #         plus[i+1] = 1
        #         # Negative change
        #         negative = [1] + [0]*n
        #         negative[i+1] = -1

        # Discovery
        # vectorsOfChange.append( plus )
        # Abandonment
        # vectorsOfChange.append( negative )
        # Recruitment
        vectorsOfChange.append(plus)
        # Cross-inhibition
        for _ in range(n - 1):
            vectorsOfChange.append(negative)
        # Recruitment from zealot
        vectorsOfChange.append(plus)
        # Cross-inhibition from zealot
        for _ in range(n - 1):
            vectorsOfChange.append(negative)

        vectorsOfChange.append(noisetrans1)
        vectorsOfChange.append(noisetrans2)
        vectorsOfChange.append(noisediscovery)
        ## vectorsOfChange for the case n=2        ## plusDicoveryOfA  minusAbandonmentOfA  plusRecruitA  plusInhibitionA plusRecruitFromZealotA  plusInhibitionFromZealotA  plusDicoveryOfB minusAbandonmentOfB  plusRecruitB  plusInhibitionB plusRecruitFromZealotB  plusInhibitionFromZealotB

    # print("VoC:", vectorsOfChange)

    quorum_reached = False
    while t < T:
        previous_state = copy.deepcopy(state)

        sim_finished, time_step = gillespieStep(state, N, gammas, alphas, rhos, sigmas, vectorsOfChange, T - t)
        # update time variable
        t += time_step
        # update SPD matrix which keeps track of the time spent in each state
        spd[int(previous_state[0])][int(previous_state[1])] += time_step
        # evoStream.write(out)
        # if (temporalEvolution != "none"):
        # if (t>1000000):#999000
        #  out = str(t) + "\t" + '\t'.join(str(x) for x in state) + "\t" + str(noise)
        # print(out)
        # out = str(t) + "\t" + '\t'.join(str(x) for x in state) + "\t"
        # evoStream.write(out)
        #   #print("t: ", t, "state: ", state)
        """
        if whichAvg == "Aavg":
            if float(state[1] > S*0.5):
                listA.append(float(state[1]))
        else:
            if float(state[2] > S*0.5):
                listB.append(float(state[2]))
        """
        ## Checking each timestep if the quorum is reached
        if (quorum > 0):  # 0.79>0 true
            #quorum_reached = False
            for i in np.arange(1, len(state) - 2):
                # print (i);
                # if (int(state[i]) > (N-Z)*quorum):
                if (state[i] >= N * quorum):
                    # print("reaches quorum")
                    quorum_reached = True
                    break
        if sim_finished or quorum_reached:
            break
    print((np.array(spd)).shape)
    out = str(t) + "\t" + '\t'.join(str(x) for x in state) + "\t" + str(noisevalue)
    print(out)
    if (finalStateFile != "none"):
        os.makedirs(os.path.dirname(finalStateFile), exist_ok=True)
        with open(finalStateFile, "a") as f:
            out = '\t'.join(str(x) for x in extraLog)
            if (len(out) > 0): out += '\t'
            out += str(t) + "\t" + '\t'.join(str(x) for x in state) + "\n"
            f.write(out)
    # if DEBUG:
    #     out = '\t'.join(str(x) for x in extraLog)
    #     if (len(out)>0): out += '\t'
    #     out += str(t) + "\t" + '\t'.join(str(x) for x in state) + "\n"
    #     print(out)
    """
    theAavg = 0
    theBAvg = 0
    if whichAvg == "Aavg":
        if len(listA) !=0:
            theAavg = np.mean(listA)
            print("A-Average:",theAavg)
    else:
        if len(listB) !=0:
            theBAvg = np.mean(listB)
            print("B-Average:",theBAvg)
    """
    if (plot_evo):
        if (temporalEvolution == "none"):
            print(
                "WARNING! - to plot the temporal evolution, please specify a temporalEvolution file (e.g., a temp-file)")
        #else:
        #    plotit(temporalEvolution, T, state, N, evoStream, Z, SA, SB, valuesA)


##################################################

if __name__ == '__main__':

    repetitions = 10

    # Computing input params
    #     valuesA = np.arange(7.5, 13, 0.5)
    noisevalue = float(sys.argv[6])
    noisetype = sys.argv[8]
    if noisetype == "TypeA":
        noisetype1 = noisevalue
        noisetype2 = [0, 0]
    else:
        noisetype1 = 0
        noisetype2 = [noisevalue, noisevalue]
    valuesA = [float(sys.argv[1])]
    print(valuesA)
    #     valuesB = np.arange(6.5, 15.01, 0.1)
    n = 2
    k = 0
    h = 1
    quorum = 0
    # CHANGED
    # Experiment time length
    T = int(sys.argv[4])
    # Setup the initial state
    N = int(sys.argv[7])
    Z = int(sys.argv[2])
    whichrun = sys.argv[3]
    # SA = (N - Z) / 2
    # SB = (N - Z) / 2
    # create data structure of the size of all possible states
    spd = [[0] * (int(N-Z) + 1) for _ in range(int(N-Z) + 1)]
    ## (keep in mind that it may not sum up to N for certain conditions... we may look at this later)
    #    state = [N-Z] + [0]*n + [Z/2] + [Z/2]

    # Reading output file path from config file
    #     finalStateFile = 'data/fs_k-' + str(k) + '_h-' + str(h) + '.txt'
    #     temporalEvolution = 'none's
    # temporalEvolution = 'data/tmp.txt'

    if sys.argv[5].lower() == 'true':
        plot_evo = True
    elif sys.argv[5].lower() == 'false':
        plot_evo = False

    for valueA in valuesA:
        finalStateFile = 'none'
        # finalStateFile = 'data/fs_k-' + str(k) + '_h-' + str(h) + '_vA-' + str(valueA) + '-r1.txt'
        #         valuesB = np.arange(valueA-3, valueA+3.01, 0.1)
        valuesB = [1]
        for valueB in valuesB:
            gammas = [k * valueA] + [k * valueB] * (n - 1)
            alphas = [k / valueA] + [k / valueB] * (n - 1)
            # gammas = [0] + [0]
            # alphas = [0] + [0]
            rhos = [h * valueA] + [h * valueB] * (n - 1)
            sigmas = [h * valueA] + [h * valueB] * (n - 1)
            for i in range(0, repetitions):
                temporalEvolution = 'none'
                # temporalEvolution = 'popevocdci/evo-N' + str(N) + '-v' + str(valueA) + "-" + str(valueB) + "-" + str(Z) + "-" + str(whichrun) '.txt'
                rnd_seed = np.random.randint(4294965)
                #rnd_seed = 43431
                # print(rnd_seed)
                S = N - Z
                if whichrun == "Afull":
                    SA = S
                    SB = 0
                    SU = 0
                elif whichrun == "Bfull":
                    SA = 0
                    SB = S
                    SU = 0
                else:
                    # Compute a random point in the 3-simplex [U,A,B]
                    r1 = np.sqrt(np.random.rand())
                    r2 = np.random.rand()
                    SU = int(r1 * (1 - r2) * S)
                    SA = int(r1 * r2 * S)
                    SB = int((1 - r1 * (1 - r2) - r1 * r2) * S)
                    while SU + SA + SB < S:
                        rnd = np.random.rand()
                        if rnd < 0.33333:
                            SU += 1
                        elif rnd < 0.66666:
                            SA += 1
                        else:
                            SB += 1

                state = [SU, SA, SB, Z / 2, Z / 2]
                print(N, Z, "Finding CDCI:", whichrun, "(", state, ")  QRatio: ", valuesA)
                # state = [N-Z] + [0]*n + [Z/n
                plt = runGillespie(state, T, N, gammas, alphas, rhos, sigmas, rnd_seed, finalStateFile, temporalEvolution, plot_evo, extraLog=[valueA, valueB], quorum=quorum)
# Normalise the SPD: divide every value by the maximum time T
for a in range(int(sum(state[0:3])) + 1):
    for b in range(int(sum(state[0:3])) + 1):
        spd[a][b] /= repetitions * T
print(np.array(spd))
#print(spd, file=open("/content/drive/MyDrive/matrixforGillcdci/outputofspd_10zealots_qr1check.txt", "a"))