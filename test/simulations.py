from math import pi
rad = 57.2958
x = 1
AU = 149597870.7
simulations = {
'sim1' : {
'objects' : {
'sun' : {'m' : 1.99E+30, 'r' : 695700, 'p' : [1.9, -6.4, 0], 'v' : [0,0,0], 'av' : [0,0,-2.77e-6], 'temperature' : 6500, 'texture' : 'textures/gstar.jpg'},
'mercury' : {'m' : 3.3e+23, 'r' : 2439, 'p' : [-26400000.0, 60583589, -7371471], 'v' : [-34.9, -21.9, -1.4], 'av' : [0,0,-124e-6], 'temperature' : 100, 'texture' : 'textures/mercury.jpg'},
'venus' : {'m' : 4.87e+24, 'r' : 6052, 'p' : [15648964, -106600000.0, 2364628], 'v' : [34.8, 5.29, 1.94], 'av' : [0,0,2.99e-7], 'temperature' : 100, 'texture' : 'textures/venus.jpg'},
'earth' : {'m' : 5.97e+24, 'r' : 6371, 'p' : [33233989, -143000000.0, -5893.1], 'v' : [29.5, 6.84, 0.391], 'av' : [0,0,-7.29e-5], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'mars' : {'m' : 6.39e+23, 'r' : 3390, 'p' : [1.53*AU,-9.95e7, 7707319], 'v' :[8.78, 20.1, -0.2], 'av' : [0,0,-7.09e-5], 'temperature' : 100, 'texture' : 'textures/mars.jpg'},
'jupiter' : {'m' : 1.98e+27, 'r' : 69911, 'p' : [1.32*AU,-751000000.0, 1351613], 'v' : [12.8, 2.7, 0.3], 'av' : [0,0,-7.09e-5], 'temperature' : 100, 'texture' : 'textures/jupiter.jpg'},
'saturn' : {'m' : 5.68e+26, 'r' : 58232, 'p' : [6.77*AU, 1077104669.04, 59243312], 'v' : [-6.5, 6.65, -0.14], 'av' : [0,0,-1.64e-4], 'temperature' : 100, 'texture' : 'textures/saturn.jpg'},
'uranus' : {'m' : 8.68e+25, 'r' : 25362, 'p' : [-2.94e9,-603000000.0, -35800000.0], 'v' : [1.4, -6.36, 0.04], 'av' : [0,0,-1.64e-4], 'temperature' : 100, 'texture' : 'textures/uranus.jpg'},
'neptune' : {'m' : 1.02e+26, 'r' : 24622, 'p' : [-4.05e9, 1929812532.03, -53300000.0], 'v' : [-2.3, -4.94, -0.16], 'av' : [0,0,1.08e-4], 'temperature' : 100, 'texture' : 'textures/neptune.jpg'},
'moon' : {'m' : 7.48e+22, 'r' : 1738, 'p' : [33046068.63, -142645200, -54404], 'v' : [28.65, 6.36, 0.382], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/moon.jpg'}
},
'time' : 10000
}, 
'sim2' : {
'objects' : {
'venus' : {'m' : 5.97e+24, 'r' : 6052, 'p' : [0,0,0], 'v' : [0,0,0], 'av' : [0,0,0], 'temperature' : 6500, 'texture' : 'textures/earth.jpg'},
'earth' : {'m' : 4.87e+24, 'r' : 6371, 'p' : [2000,1e5,0], 'v' : [0,-100,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'}
},
'time' : 10
},
'sim3' : {
'objects' : {
'venus' : {'m' : 4.87e+24, 'r' : 6052, 'p' : [0,0,0], 'v' : [1,0,0], 'av' : [0,0,2*pi/60], 'temperature' : 5800, 'texture' : 'textures/gstar.jpg'}
},
'time' : 1
},
'sim4' : {
'objects' : {
'venus' : {'m' : 4.87e+24, 'r' : 6052, 'p' : [0,0,0], 'v' : [1,0,0], 'av' : [0,0,2*pi/10000], 'temperature' : 6500, 'texture' : 'textures/moon.jpg'},
'oa' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [0,12000,0], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'ob' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [3000,0,10000], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'oc' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [0,-10000,0], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'od' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [0,0,10000], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'oe' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [-11000,0,5000], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'of' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [0,20000,0], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'og' : {'m' : 4.87e+10, 'r' : 1000, 'p' : [10000,10000,0], 'v' : [1,0,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'}
},
'time' : 10
}}