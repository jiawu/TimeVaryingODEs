#!/usr/bin/env python
##
## renovations:
# need a class called RandomNetwork

import numpy as np
import networkx as nx
from scipy.integrate import odeint as oi
import random as rd
import matplotlib.pyplot as plt
import math
import string
import os

time = np.linspace(0,100,2000.)
#Parameter generation for stimulation to specific nodes. It's all random,
#so you can fuck with it however you so choose. Just be careful, external
#perturbations should be kept pretty small to maintain convergence.
pulses = [(rd.choice([0.2,0.25,0.3]),rd.choice([0.35,0.4,0.45]),rd.choice([0.05,0.1,0.15])/20.)
          if rd.random() > 0.8 else 0 for i in range(50)]

#Randomized decay rates of various strength
dec = [5./math.pow(10,rd.choice([1,2,3,4])) for i in range(50)]

#Actual ODE system. Don't fuck with this part, there aren't any parameters here anyway
def system(y,t,mat,par):
	#The system works as such - the return is a list of summed contributions from
	#parent nodes established by the adjacency matrix, mat, which is passed in as
	#an argument. The contributions from the parent nodes are combined with another
	#randomized matrix of the same size as mat, par, which contains the necessary
	#parameters for a hill function. After the contributions are summed, a decay
	#term is subtracted, and input pulses are applied based on a random matrix,
	#see above.
    return [sum([hill(i,j)*k for i,j,k in zip(y,x[2],x[3])])-x[0]*x[1]+pulse(pulses[n])
            for n,x in enumerate(zip(dec, y, par, mat))]

#A pulse to be used as inputs to nodes
def pulse(pulse_pars, t, prob):
	#This can really easily be changed to a step, ramp, or other input function.
	#You could also always just turn this off with a return 0 statement.
	on, off, amp = pulse_pars
	return amp if ((t < off*max(time) and t > on*max(time))) else 0

#Hill kinetics, there's a try-catch to handle potential domain errors because
#discrete math is hard
def hill(c,pars):
	#This could be changed to some other type of kinetics, but then you'll also
	#need to adjust the function below that makes paraemeters.
    n, K = pars
    try:
        return math.pow(c,n) / (K + math.pow(c,n))
        #return n*c/(K+c)
    #Sometimes Hill kinetics are ridiculous
    except ValueError:
    	return 0

#Sets up random hill kinetic parameters for each possible edge, the first parameter
#is the exponent and the second is the K value
def make_pars(adj_mat):
    return [[(rd.uniform(1,3),rd.uniform(3,6)) for i in row] for row in adj_mat]

#Actually runs the ODEs and saves the dynamics,
#not much to change here unless you strictly want to fuck with initial conditions or time span
def run_sim(adj_mat,path):
    #initial conditions, with some randomly one order of magnitude greater than the others
    y0 = [rd.uniform(5,10)/20. if rd.random() > 0.6 else rd.uniform(5,10) for i,x in enumerate(adj_mat)]
    parameters = make_pars(adj_mat)

    soln = oi(system,y0,time,args=(adj_mat,parameters))
    plt.clf()
    for i, x in enumerate(soln.transpose()):
    	if i == 2:
    		plt.plot(time,soln[:,i],linewidth=3, label="Node %d"%(i+1), color="red")
        else:
        	plt.plot(time,soln[:,i], linewidth=3, label="Node %d"%(i+1), alpha=0.2, color="black")
        plt.ylim(0,np.amax(soln)*1.1)
        plt.yticks([])
        plt.xticks([])
    plt.savefig(path)

#Generates random graphs that still have no self-edges because fuck that
def random_edges(adj_mat, p):
	#Set up the edges in a directional form, which can be adjusted for "context"
	earray = np.array([[0 if rd.random() > p else 1 if rd.random() > 0.5 else -1 for i in row] for row in adj_mat])
	size = adj_mat.shape[0]
	#Exclude self edges because the ODE system won't handle those well
	earray[range(size),range(size)] = 0
	return earray

#Makes a dot file from the adjacency matrix to be made into a graph by graphviz
#You probably don't need to worry about this one
def make_graph(adj_mat,path):
	graph = "digraph G {\n\t"
	for i,x in enumerate(adj_mat):
		c = "red" if i == 2 else "blue" if i < 2 else "black"
		l = "0%d"%i if i < 10 else str(i)
		graph += '%s [color="%s" shape="circle" fontcolor="#00000000" penwidth=3]\n\t'%(l,c)
	for i,row in enumerate(adj_mat):
		for j,char in enumerate(row):
			l1 = "0%d"%i if i < 10 else str(i)
			l2 = "0%d"%j if j < 10 else str(j)
			a = "tee" if char < 0 else "vee"
			if char != 0:
				graph += '%s -> %s [arrowhead="%s" penwidth=2]\n\t'%(l2,l1,a)
	else:
		graph += "}"
	writer = open(path,"w")
	writer.write(graph)
	writer.close()

#What happens when you run the program from the terminal, don't fuck with this shit either.
if __name__ == "__main__":
	run = "".join([rd.choice(string.uppercase+string.digits) for i in range(6)])
	head = "/Users/Jupiter/Desktop/NedaPics2/"
	d = os.path.dirname(head)
	if not os.path.exists(d):
		os.makedirs(d)

	stopper = True
	while stopper:
		sub_array = random_edges(np.ones((3,3)),0.4)
		G = nx.DiGraph(sub_array)
		if nx.is_connected(G.to_undirected()):
			stopper = False
	run_sim(sub_array,head+"3Nodes/%s_dynamics.png"%run)
	dot = head + "3Nodes/%s_graph.dot"%run
	grh = head + "3Nodes/%s_graph.png"%run
	make_graph(sub_array,dot)
	os.system("circo -Tpng %s -o %s"%(dot,grh))

	for s in [5,10,30]:
		stopper = True
		while stopper:
			new_array = random_edges(np.ones((s,s)),1.5/s)
			G = nx.DiGraph(new_array)
			if nx.is_connected(G.to_undirected()):
				stopper = False
		new_array[:3,:3] = sub_array
		run_sim(new_array,head+"%dNodes/%s_dynamics.png"%(s,run))
		dot = head + "%dNodes/%s_graph.dot"%(s,run)
		grh = head + "%dNodes/%s_graph.png"%(s,run)
		make_graph(new_array,dot)
		os.system("circo -Tpng %s -o %s"%(dot,grh))

