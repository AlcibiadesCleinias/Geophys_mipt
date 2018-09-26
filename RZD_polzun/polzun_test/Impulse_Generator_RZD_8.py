#!/usr/bin/env python

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import bicgstab
from scipy.sparse.linalg import bicg
from scipy.sparse.linalg import inv
from scipy.sparse.linalg import gmres
from scipy.linalg import norm
from scipy.sparse.linalg import spsolve
import sys
from tvtk.api import tvtk, write_data
from math import sin, cos, exp, sqrt


#start of the main variable data

n_x_impulse = 5 #>=2

#end of data

Count = 200
dx = 1.0/((float)(n_x_impulse * Count))

f = open( "impulse.txt", 'w')

for i in range (n_x_impulse * Count):
    if (i<Count):
        f.write("%s %s \n" % (i*dx, ((float)(i))/((float)(Count)) ) )
    else:
        if (i>((n_x_impulse-1)*Count)):
            f.write("%s %s \n" % (i*dx, 1.0 - ((float)(i-(n_x_impulse-1)*Count))/((float)(Count)) ) )
        else:
            f.write("%s %s \n" % (i*dx, 1.0) )

f.write("%s %s \n" % (n_x_impulse * Count*dx, 0.0) )
f.close()

