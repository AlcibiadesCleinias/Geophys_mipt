#!/usr/bin/env python

import numpy as n_p
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

#the main variable data

dt = 8.5e-7 
Nt = 40001 
save = 500 
Nt_soft_half = 20000 

h_y = 0.005 
h_x = 0.01 

V_train = 120*0.277777778  
#90.0 - gruzeny, 100 - porozny, 120 - 140 - passajirsky, 160 - 200 - Moscow - SPt

P_norm = 1.88e8 
F_norm = 165375 
if_polzun = 0 
h_polzun = 0
eps = 0.001 
J_rail = 553.55 
R_wheel = 0.475 
dis_polzun = 0.0 

dis_between_wheels = 1.850 
dis_between_wheels_long = 8.150 
n_x_impulse = 5 

#sleepers = shpala. Type I: 180 mm X 250 mm - glavnye puti
#sleepers = shpala. Type II: 160 mm X 230 mm
#sleepers = shpala. Type III: 150 mm X 230 mm - malodeyatelnye puti
sleeper_height = 0.180 
sleeper_wigth = 0.250 
sleeper_into_embankment = 0.120 

embankment_height = 0.25 
earth_height = 2.0 

N_sleepers = 46 
rail_length = 25.0 
dis_butt_sleepers = 0.420 
rail_height = 0.180 

c1_steel = 5740.0 
c2_steel = 3092.0 
rho_steel = 7800.0 
max_tension_steel = 7.8e8 

c1_sleeper = 1000.0 
c2_sleeper = 500.0 
rho_sleeper = 400.0 

c1_embankment = 800.0 
c2_embankment = 400.0 
rho_embankment = 2000.0 

c1_earth = 2000.0 
c2_earth = 1000.0 
rho_earth = 2000.0 



c1_air = 330.0
c2_air = 0.0001
rho_air = 1.2


#vrode ne nado
#M_train = 90.0e3 #22 t pustoi, + 66 t tovar. 60.5 passagirskiy, 
#g = 9.8
#S_contact = 0.0005 #1 sm^2 - 10 sm^2
#N_wheel = 8
#koef_railway = 4 # 3,4 nerovnosti, 1.5 - 2 - rovno 
#P_polzun = 3.0e8 #is grapika stati
#t_polzun = 0.5e-3

T_real = (Nt-1)*dt 

n_x_dis_bet_sleepers = n_p.empty((N_sleepers+1), dtype = 'int')

n_y_sleeper_height = (int) (sleeper_height/h_y)
n_y_sleeper_into_embankment = (int) (sleeper_into_embankment/h_y)
n_y_air_height = n_y_sleeper_height - n_y_sleeper_into_embankment

n_y_embankment_height = (int) (embankment_height/h_y)
n_yx_earth_height = (int) (earth_height/h_x)
n_y_rail_height = (int) (rail_height/h_y)

n_x_sleeper_wigth = (int) (sleeper_wigth/(h_x))
n_x_sleeper_wigth_half_left = (int) (n_x_sleeper_wigth/2)
n_x_sleeper_wigth_half_right = n_x_sleeper_wigth - n_x_sleeper_wigth_half_left

n_x_rail_length = (int) (rail_length/h_x)

n_x_dis_butt_sleepers = (int) ( dis_butt_sleepers/h_x )
n_x_n_x_dis_butt_sleepers_half_left = (int) (n_x_dis_butt_sleepers/2)
n_x_n_x_dis_butt_sleepers_half_right = n_x_dis_butt_sleepers - n_x_n_x_dis_butt_sleepers_half_left

n_x_remainder = n_x_rail_length - n_x_dis_butt_sleepers
n_x_bet = (int) (n_x_remainder/(N_sleepers-1))

n_plus = n_x_remainder % (N_sleepers-1)

for i in range (n_plus):
    n_x_dis_bet_sleepers[i+1] = n_x_bet+1

for i in range (N_sleepers-n_plus-1):
    n_x_dis_bet_sleepers[i+n_plus+1] = n_x_bet

n_x_dis_bet_sleepers[0] = n_x_n_x_dis_butt_sleepers_half_left
n_x_dis_bet_sleepers[N_sleepers] = n_x_n_x_dis_butt_sleepers_half_right

for i in range (N_sleepers+1):
    print "# dis_bet_sleepers[%s]_real = %s" %(i, n_x_dis_bet_sleepers[i]*h_x)

print ""
print "# dis_butt_sleepers_real = %s" %(n_x_dis_butt_sleepers*h_x)
print "# rail_length_real = %s" %(n_x_rail_length*h_x)
print "# sleeper_wigth_real = %s" %(n_x_sleeper_wigth*h_x)
print "# sleeper_height_real = %s" %(n_y_sleeper_height*h_y)
print "# sleeper_into_embankment_real = %s" %(n_y_sleeper_into_embankment*h_y)
print "# embankment_height_real = %s" %(n_y_embankment_height*h_y)
print "# earth_height_real = %s" %(n_yx_earth_height*h_x)
print "# rail_height_real = %s" %(n_y_rail_height*h_y)
print ""

print "# T_real = %s" %(dt*(Nt-1))

print ""

print "verbose = true"

print ""
print "dt = %s" %(dt)
print ""
print "steps = %s" %(Nt)
print """#steps = 2

[grids]"""

# set rail
n_x_size_grid = n_x_rail_length 
n_y_size_grid = n_y_rail_height 
n_x_origin_grid = 0
n_y_origin_grid = 0
print "	[grid]"
print "		id = rail" 
print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]"""
print "			c1 = %s" %(c1_steel)	
print "			c2 = %s" %(c2_steel)	
print "			rho = %s" %(rho_steel)	
print "			max_tension = %s" %(max_tension_steel)	
print """		[/material]
		[factory]
			name = RectGridFactory"""	
print "			size = %s, %s" %(n_x_size_grid+1, n_y_size_grid+1)
print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
print "			spacing = %s, %s" %(h_x, h_y)
print """			curve = false	
		[/factory]
		[schema]
			name = ElasticRectSchema2DMMRusanov3	
		[/schema]
		[fillers]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 1
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 1
			[/filler]
		[/fillers]
		[correctors]
			[corrector]
				name = ForceRectElasticBoundary2D
				axis = 1
				side = 0
			[/corrector]
			[corrector]
				name = ForceRectElasticBoundary2D
				axis = 1
				side = 1"""
print """				[function]		
					name = TrainFunction"""	
print "					velocity = %s, 0.0, 0.0" %(V_train)	
print "					force = 0.0, %s, 0.0" %(0.0-P_norm)	
print "					h = %s" %(dis_between_wheels)	
print "					l = %s" %(dis_between_wheels+dis_between_wheels_long)
print "					w = %s" %(n_x_impulse*h_x)
print "					pos = %s, %s, 0.0" %(rail_length/2.0, n_y_rail_height*h_y) #-dis_between_wheels-dis_between_wheels_long/2.0 - n_x_impulse*h_x/2.0
print "					t_soft_half = %s" %(Nt_soft_half*dt)
print "					if_polzun = %s" %(if_polzun)
print "					h_polzun = %s" %(h_polzun)
print "					r_wheel = %s" %(R_wheel)
print "					cp_rail = %s" %(c1_steel)
print "					rho_rail = %s" %(rho_steel)
print "					height_rail = %s" %(n_y_rail_height*h_y)
print "					eps = %s" %(eps)
print "					dis_polzun = %s" %(dis_polzun)
print "					J_rail = %s" %(J_rail)
print "					F_norm = %s" %(F_norm)
#print "					polzun_koef = %s" %(P_polzun/P_norm)
#print "					r_wheel = %s" %(R_wheel)
#print "					eps = %s" %(len_polzun)
print """					[impulse]
						name = FileInterpolationImpulse
						[interpolator]
							name = PiceWiceInterpolator1D"""
print "							file = impulse.txt"
print """						[/interpolator]
					[/impulse]
				[/function]
			[/corrector]"""
print """			[corrector]
				name = DestructionSplitCorrector2D"""
print "				save = %s" %(save)
print "				path_model = Fr/!!!!splits_"
print "				split_len = %s" %(h_y*0.8)
print """				axis = 1
				side = 1
			[/corrector]"""
print """		[/correctors]
	[/grid]"""
print "	[grid]"
print "		id = !_d_rail"
print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]
			c1 = 100.0	
			c2 = 100.0	
			rho = 100.0	
		[/material]
		[factory]
			name = RectGridFactory
			size = 2, 2"""
print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
print "			spacing = %s, %s" %(n_x_size_grid*h_x, n_y_size_grid*h_y)
print """			curve = false	
		[/factory]
		[schema]
			name = DummySchema	
		[/schema]
		[fillers]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

# set earth
n_x_size_grid = n_x_rail_length 
n_y_size_grid = n_yx_earth_height
n_x_origin_grid = 0
n_y_origin_grid = 0 - n_y_embankment_height - n_y_sleeper_height
print "	[grid]"
print "		id = earth" 
print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]"""
print "			c1 = %s" %(c1_earth)	
print "			c2 = %s" %(c2_earth)	
print "			rho = %s" %(rho_earth)	
print """		[/material]
		[factory]
			name = RectGridFactory"""	
print "			size = %s, %s" %(n_x_size_grid+1, n_y_size_grid+1)
print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y - n_yx_earth_height*h_x)	
print "			spacing = %s, %s" %(h_x, h_x)
print """			curve = false	
		[/factory]
		[schema]
			name = ElasticRectSchema2DMMRusanov3	
		[/schema]
		[fillers]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 1
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 1
			[/filler]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

print "	[grid]"
print "		id = !_d_earth"
print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]
			c1 = 100.0	
			c2 = 100.0	
			rho = 100.0	
		[/material]
		[factory]
			name = RectGridFactory
			size = 2, 2"""
print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y - n_yx_earth_height*h_x)	
print "			spacing = %s, %s" %(n_x_size_grid*h_x, n_y_size_grid*h_x)
print """			curve = false	
		[/factory]
		[schema]
			name = DummySchema	
		[/schema]
		[fillers]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

# set d_all
n_x_size_grid = n_x_rail_length 
n_y_size_grid = n_y_embankment_height + n_y_sleeper_height
n_x_origin_grid = 0
n_y_origin_grid = 0 - n_y_embankment_height - n_y_sleeper_height
print "	[grid]"
print "		id = !_d_all"
print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]
			c1 = 100.0	
			c2 = 100.0	
			rho = 100.0	
		[/material]
		[factory]
			name = RectGridFactory
			size = 2, 2"""
print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
print "			spacing = %s, %s" %(n_x_size_grid*h_x, n_y_size_grid*h_y)
print """			curve = false	
		[/factory]
		[schema]
			name = DummySchema	
		[/schema]
		[fillers]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

# set embankment
n_x_size_grid = n_x_rail_length 
n_y_size_grid = n_y_embankment_height
n_x_origin_grid = 0
n_y_origin_grid = 0 - n_y_embankment_height - n_y_sleeper_height
print "	[grid]"
print "		id = embankment_under" 
print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]"""
print "			c1 = %s" %(c1_embankment)	
print "			c2 = %s" %(c2_embankment)	
print "			rho = %s" %(rho_embankment)	
print """		[/material]
		[factory]
			name = RectGridFactory"""	
print "			size = %s, %s" %(n_x_size_grid+1, n_y_size_grid+1)
print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
print "			spacing = %s, %s" %(h_x, h_y)
print """			curve = false	
		[/factory]
		[schema]
			name = ElasticRectSchema2DMMRusanov3	
		[/schema]
		[fillers]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 1
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 1
			[/filler]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

n_x_origin_var = 0
for i in range (N_sleepers+1):

    # set embankment
    n_x_size_grid = n_x_dis_bet_sleepers[i] - n_x_sleeper_wigth
    if (i == 0):
        n_x_size_grid = n_x_dis_bet_sleepers[0] - n_x_sleeper_wigth_half_left
    if (i == N_sleepers):
        n_x_size_grid = n_x_dis_bet_sleepers[N_sleepers] - n_x_sleeper_wigth_half_right

    n_x_origin_grid = n_x_origin_var + n_x_sleeper_wigth_half_right
    if (i == 0):
        n_x_origin_grid = n_x_origin_var
    n_x_origin_var = n_x_origin_var + n_x_dis_bet_sleepers[i]

    n_y_size_grid = n_y_sleeper_into_embankment
    n_y_origin_grid = 0 - n_y_sleeper_height
    print "	[grid]"
    print "		id = embankment_bet_%s" %(i+100) 
    print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]"""
    print "			c1 = %s" %(c1_embankment)	
    print "			c2 = %s" %(c2_embankment)	
    print "			rho = %s" %(rho_embankment)	
    print """		[/material]
		[factory]
			name = RectGridFactory"""	
    print "			size = %s, %s" %(n_x_size_grid+1, n_y_size_grid+1)
    print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
    print "			spacing = %s, %s" %(h_x, h_y)
    print """			curve = false	
		[/factory]
		[schema]
			name = ElasticRectSchema2DMMRusanov3	
		[/schema]
		[fillers]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 1
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 1
			[/filler]
		[/fillers]
		[correctors]
			[corrector]
				name = ForceRectElasticBoundary2D
				axis = 1
				side = 1
			[/corrector]
		[/correctors]
	[/grid]"""

    n_y_size_grid = n_y_sleeper_height - n_y_sleeper_into_embankment
    n_y_origin_grid = 0 - n_y_sleeper_height + n_y_sleeper_into_embankment
    print "	[grid]"
    print "		id = !_d_air_%s" %(i+100)
    print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]
			c1 = 100.0	
			c2 = 100.0	
			rho = 100.0	
		[/material]
		[factory]
			name = RectGridFactory
			size = 2, 2"""
    print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
    print "			spacing = %s, %s" %(n_x_size_grid*h_x, n_y_size_grid*h_y)
    print """			curve = false	
		[/factory]
		[schema]
			name = DummySchema	
		[/schema]
		[fillers]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

# set sleeper
n_x_size_grid = n_x_sleeper_wigth
n_y_size_grid = n_y_sleeper_height
n_y_origin_grid = 0 - n_y_sleeper_height

n_x_origin_var = 0
for i in range (N_sleepers):
    n_x_origin_var = n_x_origin_var + n_x_dis_bet_sleepers[i]
    n_x_origin_grid = n_x_origin_var - n_x_sleeper_wigth_half_left
    print "	[grid]"
    print "		id = sleeper_%s" %(i+100) 
    print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]"""
    print "			c1 = %s" %(c1_sleeper)	
    print "			c2 = %s" %(c2_sleeper)	
    print "			rho = %s" %(rho_sleeper)	
    print """		[/material]
		[factory]
			name = RectGridFactory"""	
    print "			size = %s, %s" %(n_x_size_grid+1, n_y_size_grid+1)
    print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
    print "			spacing = %s, %s" %(h_x, h_y)
    print """			curve = false	
		[/factory]
		[schema]
			name = ElasticRectSchema2DMMRusanov3	
		[/schema]
		[fillers]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 0
				side = 1
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 0
			[/filler]
			[filler]
				name = RectNoReflectFiller
				axis = 1
				side = 1
			[/filler]
		[/fillers]
		[correctors]
			[corrector]
				name = ForceRectElasticBoundary2D
				axis = 0
				side = 0
			[/corrector]
			[corrector]
				name = ForceRectElasticBoundary2D
				axis = 0
				side = 1
			[/corrector]
		[/correctors]
	[/grid]"""

    print "	[grid]"
    print "		id = !_d_sleeper_%s" %(i+100)
    print """		[node]
			name = ElasticMetaNode2D
		[/node]
		[material_node]
		[/material_node]
		[material]
			c1 = 100.0	
			c2 = 100.0	
			rho = 100.0	
		[/material]
		[factory]
			name = RectGridFactory
			size = 2, 2"""
    print "			origin = %s, %s" %(n_x_origin_grid*h_x, n_y_origin_grid*h_y)	
    print "			spacing = %s, %s" %(n_x_size_grid*h_x, n_y_size_grid*h_y)
    print """			curve = false	
		[/factory]
		[schema]
			name = DummySchema	
		[/schema]
		[fillers]
		[/fillers]
		[correctors]
		[/correctors]
	[/grid]"""

print """[/grids]
[contacts]"""

#set contacts

print """	[contact]
		name = GlueRectElasticContact2D"""
print "		grid1 = embankment_under" 
print "		grid2 = earth" 
print "		tol = %s" %(h_y/2.0)
print """		currect_bounds = true
		axis1 = 1
		axis2 = 1
		side1 = 0
		side2 = 1
	[/contact]"""

for i in range(N_sleepers+1):
    print """	[contact]
		name = GlueRectElasticContact2D"""
    print "		grid1 = embankment_bet_%s" %(i+100) 
    print "		grid2 = embankment_under" 
    print "		tol = %s" %(h_y/2.0)
    print """		currect_bounds = true
		axis1 = 1
		axis2 = 1
		side1 = 0
		side2 = 1
	[/contact]"""

for i in range(N_sleepers):
    print """	[contact]
		name = GlueRectElasticContact2D"""
    print "		grid1 = rail" 
    print "		grid2 = sleeper_%s" %(i+100) 
    print "		tol = %s" %(h_y/2.0)
    print """		currect_bounds = true
		axis1 = 1
		axis2 = 1
		side1 = 0
		side2 = 1
	[/contact]"""
    print """	[contact]
		name = GlueRectElasticContact2D"""
    print "		grid1 = sleeper_%s" %(i+100) 
    print "		grid2 = embankment_under" 
    print "		tol = %s" %(h_y/2.0)
    print """		currect_bounds = true
		axis1 = 1
		axis2 = 1
		side1 = 0
		side2 = 1
	[/contact]"""

    print """	[contact]
		name = GlueRectElasticContact2D"""
    print "		grid1 = embankment_bet_%s" %(i+100) 
    print "		grid2 = sleeper_%s" %(i+100) 
    print "		tol = %s" %(h_y/2.0)
    print """		currect_bounds = true
		axis1 = 0
		axis2 = 0
		side1 = 1
		side2 = 0
	[/contact]"""

    print """	[contact]
		name = GlueRectElasticContact2D"""
    print "		grid1 = embankment_bet_%s" %(i+1+100) 
    print "		grid2 = sleeper_%s" %(i+100) 
    print "		tol = %s" %(h_y/2.0)
    print """		currect_bounds = true
		axis1 = 0
		axis2 = 0
		side1 = 0
		side2 = 1
	[/contact]"""

print """[/contacts]

[initials]
[/initials]

[savers]"""

print """	[saver]
		name = StructuredVTKSaver
		path = VTK/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save)
print """		save_rank = false
		params = v
		norms = 1
		time_from = 0"""
print "		time_to = %s" %(save*5)
print "	[/saver]"""

save_local = save
time_to_local = Nt+2
time_from_local = Nt_soft_half

print """	[saver]
		name = StructuredVTKSaver
		path = V/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save_local)
print """		save_rank = false
		params = v
		norms = 1"""
print "		step_from = %s" %(time_from_local)
print "		step_to = %s" %(time_to_local)
print "	[/saver]"""


print """	[saver]
		name = StructuredVTKSaver
		path = Vx/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save)
print """		save_rank = false
		params = vx
		norms = 0"""
print "		step_from = %s" %(time_from_local)
print "		step_to = %s" %(time_to_local)
print "	[/saver]"""

print """	[saver]
		name = StructuredVTKSaver
		path = Vy/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save)
print """		save_rank = false
		params = vy
		norms = 0"""
print "		step_from = %s" %(time_from_local)
print "		step_to = %s" %(time_to_local)
print "	[/saver]"""

print """	[saver]
		name = StructuredVTKSaver
		path = Sxx/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save)
print """		save_rank = false
		params = sxx
		norms = 0"""
print "		step_from = %s" %(time_from_local)
print "		step_to = %s" %(time_to_local)
print "	[/saver]"""

print """	[saver]
		name = StructuredVTKSaver
		path = Sxy/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save)
print """		save_rank = false
		params = sxy
		norms = 0"""
print "		step_from = %s" %(time_from_local)
print "		step_to = %s" %(time_to_local)
print "	[/saver]"""

print """	[saver]
		name = StructuredVTKSaver
		path = Syy/%g_%s.vtk
		order = 0"""
print "		save = %s" %(save)
print """		save_rank = false
		params = syy
		norms = 0"""
print "		step_from = %s" %(time_from_local)
print "		step_to = %s" %(time_to_local)
print "	[/saver]"""

print "[/savers]"

