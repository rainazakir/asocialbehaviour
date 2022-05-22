#!/bin/bash
#TO FIND THE MST
rep=1
model="cdci"            # "cdci dmvd"
zealots="22 34"            # "18,20,22,24,26 ..."
qratio="1.1"        # "1.05 1.5 1.1 .."
whichMST="AtoB BtoA"         # "AtoB BtoA"
AveragesAcdci=(45)     #if finding B to A specify the values here 
AveragesBcdci=(44 22)
AveragesAdmvd=(56)
AveragesBdmvd=(54)
needplot="False"         # "False"
timesteps=500           # 
j=0
for z in $zealots
do
     for qr in $qratio
	 do
    		for mod in $model
        	do
            	if [ $mod == "cdci" ]
            	then
                	for mst in $whichMST
                	do
                        if [ $mst == "AtoB" ]
                        then
                    		    echo "executed"
                                python3 findMSTcdci.py $qr $z ${AveragesBcdci[$j]} $timesteps $needplot $mst $rep; echo Finished
                        else
                    		    echo "executed2"
                    		    echo $mst
                                python3 findMSTcdci.py $qr $z ${AveragesAcdci[$j]} $timesteps $needplot $mst $rep; echo Finished
                        fi
                    done
            	else
                	for mst in $whichMST
                    do
                        if [ $mst == "AtoB" ]
                        then
                                python3 findMSTdmvd.py $qr $z ${AveragesBdmvd[$j]} $timesteps $needplot $mst $rep; echo Finished
                        else
                                python3 findMSTdmvd.py $qr $z ${AveragesAdmvd[$j]} $timesteps $needplot $mst $rep; echo Finished
                        fi
                    done
               fi
            done
	 done
	 ((j=j+1))
done


