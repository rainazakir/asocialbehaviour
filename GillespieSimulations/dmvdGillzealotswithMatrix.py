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
#from plotting import plotit

import matplotlib.pyplot as plt
%matplotlib inline

listA = []
listB = []

opdir = '/scratch/data2/'  # os.getcwd()
data_files = []
statusofNA = "none"
time1 = "none"
time2 = "none"
totaltime = 0
alltimes = []

DEBUG = False


#################FUNCTIONS#########################
def gillespieStep(state, N, gammas, alphas, rhos, sigmas, vectorsOfChange, timeLeft):    # Computing the probabilities of change
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
    numOptions = int((len(state)) / 2)  # state matrix is now 0, 1, 2 ,3
    # for i in range(0, numOptions ): # PAY ATTENTION THAT i IS NOT THE CORRECT state[i] BUT IT MUST BE state[i+1], WHILE WORKS FOR gammas[i], alphas[i], rhos[i]
    # print(i)   #0,1
    #################Normal Recruitment:
    probabilitiesOfChange.append(state[0] * state[1] * r[0] / (N - 1))
    ################Zealot Recruitment:
    probabilitiesOfChange.append(state[1] * state[2] * r[2] / (N - 1))

    probabilitiesOfChange.append(state[0] * state[1] * r[1] / (N - 1))

    probabilitiesOfChange.append(state[0] * state[3] * r[3] / (N - 1))

    # Discovery
    # probabilitiesOfChange.append( state[0]*state[1]*gamma[i] ) # U -> A and U -> B
    # Abandonment
    # probabilitiesOfChange.append( state[i+1]*alphas[i] )# A -> U and B -> U
    # Recruitment
    # probabilitiesOfChange.append( state[0]*state[i+1]*rhos[i]/N ) # U + A -> A + A
    # Cross-inhibition
    # for j in range(0, numOptions):
    #    if (i==j):
    #        continue
    #    probabilitiesOfChange.append( state[i+1]*state[j+1]*sigmas[j]/N )
    # Recruitment from zealot
    # probabilitiesOfChange.append( state[0]*state[ i+numOptions+1 ]*rhos[i]/N ) # U + ZA -> A + ZA
    # Cross-inhibition from zealot
    # for j in range(0, numOptions):
    #    if (i==j):
    #        continue
    #    probabilitiesOfChange.append( state[i+1]*state[j+numOptions+1]*sigmas[j]/N ) # A + ZJ -> U + ZJ

    #    print("PoC:", probabilitiesOfChange)

    probSum = sum(probabilitiesOfChange)
    timeInterval = np.random.exponential(1 / probSum)
    # The transition happens after the maximum time length, so we do not include it and terminate the step
    if timeInterval > timeLeft:
        return True, timeLeft

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

    # print("PoC NEW:", probabilitiesOfChange)

    index = -1
    for i, prob in enumerate(probabilitiesOfChange):
        if (reaction >= bottom and reaction < (bottom + prob)):
            index = i
            break
        bottom += prob
        # print("Index, Prob", i, prob)

    # print("timeInterval is", timeInterval)
    # print("reaction is", reaction)
    # print("index is ", index)

    if (index == -1):
        print("Transition not found. Error in the algorithm execution.")
        # sys.exit()
    #     print(state)
    #     print(vectorsOfChange[index])
    state += np.array(vectorsOfChange[index])
    #     print(state)
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
        out = '{:.20f}'.format(t) + "\t" + '\t'.join(str(x) for x in state) + "\n"
        evoStream.write(out)

    # Creating the list of vector of change
    vectorsOfChange = []
    for i in [1, 2]:
        if (i == 1):  # pop A
            # [A B ZA ZB]
            plus = [1, -1, 0, 0]  # the important thing is that sum is ZERO
            negative = [-1, 1, 0, 0]
        if (i == 2):  # pop B
            plus = [-1, 1, 0, 0]
            negative = [1, -1, 0, 0]

        #         # Positive change
        #         plus = [-1] + [0]*n
        #         plus[i+1] = 1
        #         # Negative change
        #         negative = [1] + [0]*n
        #         negative[i+1] = -1

        # Switch to A/B from Normal Agent
        # vectorsOfChange.append( plus )
        # Abandonment
        # vectorsOfChange.append( negative )
        # Recruitment
        vectorsOfChange.append(plus)
        # Cross-inhibition
        # for _ in range(n-1):
        #    vectorsOfChange.append( negative )
        # Recruitment from zealot
        vectorsOfChange.append(plus)
        # Cross-inhibition from zealot
        # for _ in range(n-1):
        #    vectorsOfChange.append( negative )

        ## vectorsOfChange for the case n=2
        ## plusDicoveryOfA  minusAbandonmentOfA  plusRecruitA  plusInhibitionA plusRecruitFromZealotA  plusInhibitionFromZealotA  plusDicoveryOfB minusAbandonmentOfB  plusRecruitB  plusInhibitionB plusRecruitFromZealotB  plusInhibitionFromZealotB
    print((sum(state[0:2])) + 1)
    print(int(sum(state[0:2])) + 1)
    # create data structure of the size of all possible states
    #    print("VoC:", vectorsOfChange)
    quorum_reached = False
    while t < T:
        sim_finished, time_step = gillespieStep(state, N, gammas, alphas, rhos, sigmas, vectorsOfChange, T - t)        # print(time_step, t)
        # update time variable
        previous_state = copy.deepcopy(state)
        t += time_step
        # update SPD matrix which keeps track of the time spent in each state
        spd[int(previous_state[0])][int(previous_state[1])] += time_step
        # print(spd[168][1], file=open("/content/drive/MyDrive/matrixforGillcdci/outputofspd_10zealots_qr1time.txt", "a"))
        # if (temporalEvolution == "none"):
        #   if (t>1398):
        #  	print("t: ", t, "state: ", state)
        ##if (temporalEvolution == "none"):
        ##   if (t>999100):
        ##      out = str(t) + "\t" + '\t'.join(str(x) for x in state)
        ##     print(out)
        #             #evoStream.write(out)
        ## Checking each timestep if the quorum is reached
        if (quorum > 0):  # 0.79>0 true
            quorum_reached = False
            for i in np.arange(0, len(state) - 2):
                # print (i);
                if (int(state[i]) > (N - Z) * quorum):
                    # print("reaches quorum")
                    quorum_reached = True
                    break
        if sim_finished or quorum_reached:
            break
    # print("Middle round", np.array(spd))

    if (finalStateFile != "none"):
        os.makedirs(os.path.dirname(finalStateFile), exist_ok=True)
        with open(finalStateFile, "a") as f:
            out = ' '.join(str(x) for x in r)
            if (len(out) > 0): out += ' '
            out += str(t) + " " + ' '.join(str(x) for x in state) + "\n"
            f.write(out)
    out = str(r[0]) + "\t" + str(r[1]) + "\t" + str(r[2]) + "\t" + str(r[3]) + "\t" + str(t) + "\t" + '\t'.join(
        str(x) for x in state)
    print(out)

    if DEBUG:
        out = ' '.join(str(x) for x in r)
        out += str(t) + " " + ' '.join(str(x) for x in state) + "\n"
        print(out)
        # print("Gillespie run ended")
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
        else:
            plotit(temporalEvolution, T, state, N, evoStream, Z, SA, SB, theAavg, theBAvg, rate)


##################################################

if __name__ == '__main__':
    if DEBUG:
        print("Process Started")

    repetitions = 1
    # Computing input params
    #     valuesA = np.arange(7.5, 13, 0.5)
    valuesA = [1.05]
    #     valuesB = np.arange(6.5, 15.01, 0.1)
    n = 2
    k = 1
    h = 1
    quorum = 0
    rate = 1.05
    r = [rate, 1, rate, 1]

    # Experiment time length
    T = 1000
    # Setup the initial state
    N = 200
    Z = 40
    whichrun = "random"
    spd = [[0] * (int(N - Z) + 1) for _ in range(int(N - Z) + 1)]

    # Reading output file path from config file
    #     finalStateFile = 'fs_k-' + str(k) + '_h-' + str(h) + '.txt'
    #    temporalEvolution = 'none'
    # temporalEvolution = 'data/tmp.txt'
    #if sys.argv[5].lower() == 'true':
    #    plot_evo = True
    #elif sys.argv[5].lower() == 'false':
    plot_evo = False
    for valueA in valuesA:
        finalStateFile = 'data/fs_k-' + str(k) + '_h-' + str(h) + '_vA-' + str(valueA) + '-r1.txt'
        #         valuesB = np.arange(valueA-3, valueA+3.01, 0.1)
        valuesB = [1]
        for valueB in valuesB:
            gammas = [k * valueA] + [k * valueB] * (n - 1)
            alphas = [k / valueA] + [k / valueB] * (n - 1)
            rhos = [h * valueA] + [h * valueB] * (n - 1)
            sigmas = [h * valueA] + [h * valueB] * (n - 1)
            for i in range(0, repetitions):
                temporalEvolution = 'none'
                #                 temporalEvolution = 'popevodmvd/evo-N' + str(N) + '-v' + str(valueA) + "-" + str(valueB) + "-" + str(Z) +  "-"+str(whichrun)+'.txt'
                rnd_seed = np.random.randint(429496)
                print(rnd_seed)
                S = N - Z
                if whichrun == "Afull":
                    SA = S
                    SB = 0
                elif whichrun == "Bfull":
                    SA = 0
                    SB = S
                else:
                    # Compute a random point in the 3-simplex [U,A,B]
                    # r1 = np.sqrt(np.random.rand())
                    r2 = np.random.rand()
                    SA = int(r2 * S)
                    SB = int(S - SA)

                    state = [SA, SB, Z / 2, Z / 2]
                    print(state)
                    #print(SA + SB + Z)
                plt = runGillespie(state, T, N, gammas, alphas, rhos, sigmas, rnd_seed, finalStateFile,
                                   temporalEvolution, plot_evo, extraLog=[valueA, valueB], quorum=quorum)
    if DEBUG:
        print("Process Ended")
# Normalise the SPD: divide every value by the maximum time T
for a in range(int(sum(state[0:2])) + 1):
    for b in range(int(sum(state[0:2])) + 1):
        spd[a][b] /= repetitions * T
print(np.array(spd))
#print(spd, file=open("/content/drive/MyDrive/matrixforGillcdci/outputofspd_10zealots_qr1check.txt", "a"))