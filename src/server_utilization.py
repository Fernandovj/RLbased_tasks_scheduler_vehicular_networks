'''
****  M/M/1 queue simulation for calculating server utilization ****

The simulator has 3 functions:

- simulate(meanArrivalTime,meanServiceTime,endSimulationTime,repetitions) which contains
the two essential events: arrival and departure.  

- average(lista) receives a list as parameter aimed to calculate the average from the values that
compose the list-  

- standardDev(lista) which also has as input a list and calculates the standard
deviation from the values of the list.

'''

import math
import random
import numpy

#meanArrivalTime: Average time between arrivals
#meanServiceTime: Average service time of server

def simulate(meanArrivalTime, meanServiceTime, endSimulationTime, rep):    
        #print("Mean Arrival Time: " +str(meanArrivalTime))
        meanDelayList=[]
        utilizationList=[]
        throughputList=[]
        for i in range(rep): #Numero de repeticiones 
            currentTime = 0.0    # Simulation time
            finishTime = endSimulationTime
            arriveTime =   0.0  #        
            departureTime = finishTime #
            numberPk = 0;   #
            numberPk_queue = 0   #      Number of packets in the system
            numberPk_attended = 0  #    Number of service completions
            startBusyTime = 0.0  #      
            totalBusyTime = 0.0#
            throughput=0.0  #          
            utilization=0.0#
            totalDelay=0.0#
            meanDelay=0.0#
            processTime= 0.00001
            queueArrival=[]
            delayXpacket=[] #guarda el delay de cada paquete

            while(currentTime < finishTime):
                
                if arriveTime < departureTime: #Event to manage the arrival of packets 
                    currentTime  = arriveTime
                    numberPk=numberPk+1
                    
                    if currentTime == 0:
                        queueArrival.append(currentTime) # arrival time for the first packet is added into the queue
                        
                    numberPk_queue=numberPk_queue+1
    
                    arriveTime = currentTime + numpy.random.exponential(meanArrivalTime) # lambda(arrival rate) = 1/meanArrivalTime
                    queueArrival.append(arriveTime) # arrival time for next packet is added
                    
                    if numberPk_queue == 1 : #if queue has just one element, busy time is initialized                               
                        startBusyTime = currentTime
                        departureTime = arriveTime + numpy.random.exponential(meanServiceTime) + numpy.random.exponential(processTime)
                        

                else: #Event to manage the departure of packets
                    
                    currentTime = departureTime

                    if len(queueArrival) > 0:
                        numberPk_queue = numberPk_queue-1
                        numberPk_attended = numberPk_attended+1                        
                        
                        totalDelay = totalDelay + (currentTime - queueArrival[0])
                        delayXpacket.append(currentTime - queueArrival[0]) #calculo del delay de cada paquete                                   
                        queueArrival.pop(0) #se quita el elemento en cola

                    if numberPk_queue > 0:
                        
                        departureTime = currentTime + numpy.random.exponential(meanServiceTime) + numpy.random.exponential(processTime)

                    else: #Update busy time sum if empty
                        departureTime = finishTime
                        totalBusyTime = totalBusyTime + (currentTime - startBusyTime)
                        #print "++totalBusyTime: ",totalBusyTime
            
            totalBusyTime = totalBusyTime + (currentTime - startBusyTime)   ###quitarrrr          
            throughput = numberPk_attended/currentTime # Calculo del throughput
            throughputList.append(throughput)
            utilization  = (totalBusyTime/currentTime)*100 # Calculo de la utilizacion
            utilizationList.append(utilization)
            meanDelay = totalDelay/numberPk_attended # Calculo del retraso medio
            meanDelayList.append(meanDelay) 
            #print("Number of packtes generated: " + str(numberPk))
            #print("Number of packtes attended: " + str(numberPk_attended))
        
        mean_utilization = average(utilizationList)
        if mean_utilization > 100:
            mean_utilization = 100  
        return mean_utilization

def average(lista): # funcion para retornar el promedio de una lista de datos
    sum=0.0
    for l in range(0,len(lista)):
        sum=sum+lista[l] 
    return sum/len(lista)

def standardDev(lista): # funcion para calcular desviacion standard
    sum = 0.0
    size = len(lista)
    avrg = average(lista)
    #print "average: ",avrg
    for l in range(0,len(lista)):
        sum = sum + math.pow((lista[l] - avrg), 2.0)
    
    return math.sqrt(sum/(size));


#meanArrivalTime = 1
#meanServiceTime = .8
#endSimulationTime = 600
#repetitions = 1
#utilization = simulate(meanArrivalTime,meanServiceTime,endSimulationTime,repetitions) 
#print("utilization:", round(utilization))



