
#!/bin/bash
#TO FIND THE AVERAGES
model="cdci"            # "cdci dmvd"
zealots="18"            # "18 20 22 52 76"
qratio="1.1"        # "1.05 1.5 1.1 .."
whichAvg="Aavg Bavg"         # "Aavg Bavg"
timesteps=500           # 
i=0
needplot="True"         # "False"
for z in $zealots
do
	for avg in $whichAvg
	do
		for qr in $qratio
		do
        		for mod in $model
        		do
        		    echo "executed"
            		if [ $mod == "cdci" ]; then
                		python3 cdciAvg.py $qr $z $avg $timesteps $needplot; echo Finished
            		else
            		    python3 dmvdAvg.py $qr $z $avg $timesteps $needplot; echo Finished
                    fi
                done
		done

	done
done


