'''
Created on 24 Jun 2016
@author: Andreagiovanni Reina.
University of Sheffield, UK.
'''

#import RungeKutta.bestOfN

import numpy as np
import matplotlib.pyplot as plt
#plt.figure(figsize=(16,10)) 

def plotit(temporalEvolution,T,state,N,evoStream,Z,SA,SB,theAavg,theBAvg,qr):
        evoStream.seek(0)
        matStr = evoStream.read()
        matStr = matStr.replace("\t"," ")
        matStr = matStr.replace("\n",";")
        matStr = "" + matStr[0:len(matStr)-1] + ""
#        print(matStr)
        mat = np.matrix(matStr)
#         print(mat[0:3,(1,3)])
        if(len(state)==4):
            colours = ['r', 'b', 'g', 'c', 'm', 'y', 'fuchsia', 'aqua', 'peru', 'lime']
        else:
            colours = ['k', 'r', 'b', 'g', 'c', 'm', 'y', 'fuchsia', 'aqua', 'peru', 'lime']
        for c in range(len(state)):
            plt.plot(mat[0:,0],mat[0:,c+1],colours[c])
#         plt.plot(mat[0:,0],mat[0:,1],'k')
#         plt.plot(mat[0:,0],mat[0:,2],'b')
#         plt.plot(mat[0:,0],mat[0:,3],'r')
#         plt.plot(mat[0:,0],mat[0:,4],'g')
        #plt.xlim((0,max(mat[0:,0])))
        plt.xlim((0,T))
        plt.ylim((0,N))
        x_coordinates = [1,T]
        y_coordinates = [theAavg,theAavg]
        plt.plot(x_coordinates,y_coordinates, colours[5],label='A Avg', linewidth=3)
        x_coordinates = [1,T]
        y_coordinates = [theBAvg,theBAvg]
        plt.plot(x_coordinates,y_coordinates, colours[6],label='B Avg',linewidth=3)
        plt.xlabel('time')
        plt.ylabel('populations')
        plt.legend(['Z:'+str(Z)+" SA:"+ str(SA)+" SB:"+str(SB)+ " QR:"+str(qr)])
        plt.draw()
        #plt.show(block=False)
#        plt.ion()
        plt.show()
        plt.savefig('fig'+str(Z)+"_SA-"+str(SA)+ "_SB-"+str(SB)+"_"+str(qr)+'.png')