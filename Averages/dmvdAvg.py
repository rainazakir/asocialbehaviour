'''
Created on 24 Jun 2016

@author: Andreagiovanni Reina.
University of Sheffield, UK.
'''

#import RungeKutta.bestOfN

import numpy as np
import sys
import os
from plotting import plotit

#import matplotlib.pyplot as plt
# import matplotlib.pyplot as plt
listA =[]
listB =[]

opdir = '/scratch/data2/'#os.getcwd()
data_files = []
statusofNA ="none"
time1 = "none"
time2 = "none"
totaltime = 0
alltimes = []


DEBUG=False

#################FUNCTIONS#########################
def gillespieStep(state, r, N, Z, gammas, alphas, rhos, sigmas, vectorsOfChange):
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
    numOptions = int((len(state))/2)    #state matrix is now 0, 1, 2 ,3 
    #for i in range(0, numOptions ): # PAY ATTENTION THAT i IS NOT THE CORRECT state[i] BUT IT MUST BE state[i+1], WHILE WORKS FOR gammas[i], alphas[i], rhos[i] 
       # print(i)   #0,1
        #################Normal Recruitment:
    probabilitiesOfChange.append( state[0]*state[1]*r[0]/(N-1)) 
        ################Zealot Recruitment:
    probabilitiesOfChange.append( state[1]*state[2]*r[2]/(N-1))

    probabilitiesOfChange.append( state[0]*state[1]*r[1]/(N-1)) 

    probabilitiesOfChange.append( state[0]*state[3]*r[3]/(N-1))


        # Discovery
        #probabilitiesOfChange.append( state[0]*state[1]*gamma[i] ) # U -> A and U -> B
        # Abandonment
        #probabilitiesOfChange.append( state[i+1]*alphas[i] )# A -> U and B -> U
        # Recruitment
        #probabilitiesOfChange.append( state[0]*state[i+1]*rhos[i]/N ) # U + A -> A + A
        #Cross-inhibition
        #for j in range(0, numOptions):
        #    if (i==j):
        #        continue
        #    probabilitiesOfChange.append( state[i+1]*state[j+1]*sigmas[j]/N )
        # Recruitment from zealot
        #probabilitiesOfChange.append( state[0]*state[ i+numOptions+1 ]*rhos[i]/N ) # U + ZA -> A + ZA
        # Cross-inhibition from zealot
        #for j in range(0, numOptions):
        #    if (i==j):
        #        continue
        #    probabilitiesOfChange.append( state[i+1]*state[j+numOptions+1]*sigmas[j]/N ) # A + ZJ -> U + ZJ
    
#    print("PoC:", probabilitiesOfChange)   
  
    probSum = sum(probabilitiesOfChange)
    timeInterval = np.random.exponential( 1/probSum );
    #print("Time iNtervale: ", timeInterval)
#    print ( "Probablity Sum: ", probSum)
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
    probabilitiesOfChange = [pc/probSum for pc in probabilitiesOfChange]

   # print("PoC NEW:", probabilitiesOfChange)   

    index = -1
    for i, prob in enumerate(probabilitiesOfChange):
        if ( reaction >= bottom and reaction < (bottom + prob)):
            index = i
            break
        bottom += prob
        #print("Index, Prob", i, prob)
                
    #print("timeInterval is", timeInterval)
    #print("reaction is", reaction)
    #print("index is ", index)
    
    if (index == -1):
        print("Transition not found. Error in the algorithm execution.")
        #sys.exit()
#     print(state)
#     print(vectorsOfChange[index])
    state += np.array(vectorsOfChange[index])
#     print(state)
    return(timeInterval)

def runGillespie(state, r, T, N, Z, gammas, alphas, rhos, sigmas, rnd_seed, finalStateFile, temporalEvolution, plot_evo, quorum):
    np.random.seed(rnd_seed)
    n = len(gammas)
    state = np.array(state)
    t = 0
    #if DEBUG:
    #    print("t: ", t, "state: ", state)
    
    # Opening output file if needed
    if (temporalEvolution != "none"):
        os.makedirs(os.path.dirname(temporalEvolution), exist_ok=True)
        evoStream = open(temporalEvolution, "w+")
        out = '{:.20f}'.format(t) + "\t" + '\t'.join(str(x) for x in state) + "\n"
        evoStream.write(out)
    
    # Creating the list of vector of change
    vectorsOfChange = []
    for i in [1,2]:
        if (i == 1): # pop A
            # [A B ZA ZB]
            plus = [1, -1, 0, 0] # the important thing is that sum is ZERO 
            negative = [-1, 1, 0, 0]
        if (i == 2): # pop B
            plus = [-1, 1, 0, 0]
            negative = [1, -1, 0, 0]

#         # Positive change
#         plus = [-1] + [0]*n
#         plus[i+1] = 1
#         # Negative change
#         negative = [1] + [0]*n
#         negative[i+1] = -1
        
        # Switch to A/B from Normal Agent
        #vectorsOfChange.append( plus )
        # Abandonment
        #vectorsOfChange.append( negative )
        # Recruitment
        vectorsOfChange.append( plus )
        #Cross-inhibition
        #for _ in range(n-1):
        #    vectorsOfChange.append( negative )
        # Recruitment from zealot
        vectorsOfChange.append( plus )
        #Cross-inhibition from zealot
        #for _ in range(n-1):
        #    vectorsOfChange.append( negative )
            
        ## vectorsOfChange for the case n=2
        ## plusDicoveryOfA  minusAbandonmentOfA  plusRecruitA  plusInhibitionA plusRecruitFromZealotA  plusInhibitionFromZealotA  plusDicoveryOfB minusAbandonmentOfB  plusRecruitB  plusInhibitionB plusRecruitFromZealotB  plusInhibitionFromZealotB  
        
#    print("VoC:", vectorsOfChange)
    while t < T:
        t += gillespieStep(state, r, N, Z, gammas, alphas, rhos, sigmas, vectorsOfChange)
        #if DEBUG:
        #   if (t>1398):
        #  	print("t: ", t, "state: ", state)
        if (temporalEvolution != "none"):
            out = str(t) + "\t" + '\t'.join(str(x) for x in state) + "\n"
            evoStream.write(out)
        if whichAvg == "Aavg":
            if float(state[0] > S*0.5):
                listA.append(float(state[0]))
        else:
            if float(state[1] > S*0.5):
                listB.append(float(state[1]))
        ## Checking each timestep if the quorum is reached
        if (quorum > 0): #0.79>0 true
            quorum_reached = False
            for i in np.arange(0,len(state)-2):  
                #print (i);
                if (int(state[i]) > (N-Z)*quorum):
                    #print("reaches quorum")
                    quorum_reached = True
                    break
            if (quorum_reached):
                break
        
    if (finalStateFile != "none"):
        os.makedirs(os.path.dirname(finalStateFile), exist_ok=True)
        with open(finalStateFile, "a") as f:
            out = ' '.join(str(x) for x in r)
            if (len(out)>0): out += ' '
            out += str(t) + " " + ' '.join(str(x) for x in state) + "\n"
            f.write(out)
    if DEBUG:
        out = ' '.join(str(x) for x in r)
        out += str(t) + " " + ' '.join(str(x) for x in state) + "\n"
        print (out)
        #print("Gillespie run ended")
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
    if (plot_evo):
       if (temporalEvolution == "none"):
             print("WARNING! - to plot the temporal evolution, please specify a temporalEvolution file (e.g., a temp-file)")
       else:
           plotit(temporalEvolution,T,state,N,evoStream,Z,SA,SB,theAavg,theBAvg,rate)

##################################################

if __name__ == '__main__':
    if DEBUG: 
        print("Process Started")
    
    repetitions = 1
    
    # Computing input params
#     valuesA = np.arange(7.5, 13, 0.5)
    valuesA = [1]
#     valuesB = np.arange(6.5, 15.01, 0.1)
    n=2
    k=1
    h=1
    quorum = 0
    rate = float(sys.argv[1])
    r = [rate,1,rate,1]
    
    # Experiment time length
    T = int(sys.argv[4])
    # Setup the initial state
    N = 200
    Z = int(sys.argv[2])
    whichAvg = sys.argv[3]
    if whichAvg == "Aavg":
        SA = N-Z
        SB = 0
    else:
        SB = N-Z
        SA = 0
    S = N-Z
    print(N,Z,"Finding DMVD:", whichAvg,"QRatio: ",rate)
    #print(r)
    state = [SA] + [SB] + [Z/2] + [Z/2]
    
    # Reading output file path from config file    
#     finalStateFile = 'fs_k-' + str(k) + '_h-' + str(h) + '.txt'
#    temporalEvolution = 'none'
    #temporalEvolution = 'data/tmp.txt'
    if sys.argv[5].lower() == 'true':
        plot_evo = True
    elif sys.argv[5].lower() == 'false':
        plot_evo = False
    for valueA in valuesA:
        finalStateFile = 'data/fs_k-' + str(k) + '_h-' + str(h) + '_vA-' + str(valueA) + '-r1.txt'
#         valuesB = np.arange(valueA-3, valueA+3.01, 0.1)
        valuesB = [1]
        for valueB in valuesB:
            gammas = [k*valueA] + [k*valueB]*(n-1)
            alphas = [k/valueA] + [k/valueB]*(n-1)
            rhos = [h*valueA] + [h*valueB]*(n-1)
            sigmas = [h*valueA] + [h*valueB]*(n-1) 
            for i in range(0,repetitions):
                temporalEvolution = 'popevodmvd/evo-N' + str(N) + '-v' + str(valueA) + "-" + str(valueB) + "-" + str(Z) +  "-"+str(whichAvg)+'.txt'
                rnd_seed = np.random.randint(4294967295)
                plt = runGillespie(state, r, T, N, Z, gammas, alphas, rhos, sigmas, rnd_seed, finalStateFile, temporalEvolution, plot_evo, quorum)

#         dt=1
#         state=[0, 0]
#         temporalEvolution = 'rk-v' + str(valueA) + '-' + str(valueB) + '.txt'
#         RungeKutta.bestOfN.runRungeKutta(state, T, dt, gammas, alphas, rhos, sigmas, finalStateFile, 'none', temporalEvolution, '', plot_evo, N)
#    if (plot_evo): 
#        print("yes")
        #plt.rcParams["figure.figsize"] = [16,9]
        #plt.show()
    if DEBUG:
        print("Process Ended")