from NetworkGenerator import Network
import NetworkSimulator as ns
import numpy as np
import u_functions as uf
from scipy import integrate
import matplotlib.pyplot as plt


nodes = 10
min_edge = 15
max_edge = 15

event_n = 2

network_list = []
state_space_list = []
for events in xrange(event_n):
    network = Network()
    network.populate_random_graph(nodes, min_edge, max_edge)
    network_list.append(network)
    state_space_list.append(ns.create_state_space(network.adjacency_matrix))

y0 = np.array([1]*len(state_space_list[0]))
u_func = uf.simple(amp=2,freq=2,bias=1)
B = np.array([1,0,0,0,0,0,0,0,0,0])

#define t
#define ode integration from the previous network
t01 = np.linspace(0,50,21)
t12 = np.linspace(50,100,21)

Y01 = integrate.odeint(ns.ode_func, y0, t01, args=(state_space_list[0], u_func, B, ))
last_state=Y01[-1]
expected01 = u_func.signal(t01)

Y12 = integrate.odeint(ns.ode_func, last_state, t12, args=(state_space_list[1], u_func, B, ))
last_state=Y01[-1]
expected12 = u_func.signal(t12)

combinedY = np.vstack((Y01,Y12))
combinedt = np.append(t01,t12)
combinedexpected = np.append(expected01,expected12)
plt.plot(combinedt, combinedY, combinedt, combinedexpected)
plt.legend(['x1','x2','x3','x4','x5','x6','x7','x8','x9','x10','expected'])
plt.show()

