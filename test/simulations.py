rad = 57.2958
x = 1
simulations = {
'sim1' : {
'objects' : {
'sun' : {'m' : 1.99E+30, 'r' : 695700, 'p' : [0,0,0], 'v' : [0,0,0], 'av' : [0,0,-2.77e-6], 'temperature' : 6500, 'texture' : 'textures/sun2.jpg'},
'mercury' : {'m' : 3.3e+23, 'r' : 2439, 'p' : [0,57909227,0], 'v' : [50*x,0,0], 'av' : [0,0,-124e-6], 'temperature' : 100, 'texture' : 'textures/mercury.jpg'},
'venus' : {'m' : 4.87e+24, 'r' : 6052, 'p' : [0,108942109,0], 'v' : [35*x,0,0], 'av' : [0,0,2.99e-7], 'temperature' : 100, 'texture' : 'textures/venus.jpg'},
'earth' : {'m' : 5.97e+24, 'r' : 6371, 'p' : [0,15e7,0], 'v' : [30*x,0,0], 'av' : [0,0,-7.29e-5], 'temperature' : 100, 'texture' : 'textures/earth.jpg'},
'mars' : {'m' : 6.39e+23, 'r' : 3390, 'p' : [0,2.3e8,0], 'v' : [24*x,0,0], 'av' : [0,0,-7.09e-5], 'temperature' : 100, 'texture' : 'textures/mars.jpg'},
'jupiter' : {'m' : 1.98e+27, 'r' : 69911, 'p' : [0,7.79e8,0], 'v' : [13*x,0,0], 'av' : [0,0,-7.09e-5], 'temperature' : 100, 'texture' : 'textures/jupiter.jpg'},
'saturn' : {'m' : 5.68e+26, 'r' : 58232, 'p' : [0,1.4e9,0], 'v' : [9.7*x,0,0], 'av' : [0,0,-1.64e-4], 'temperature' : 100, 'texture' : 'textures/saturn.jpg'},
'uranus' : {'m' : 8.68e+25, 'r' : 25362, 'p' : [0,2.9e10,0], 'v' : [6.8*x,0,0], 'av' : [0,0,-1.64e-4], 'temperature' : 100, 'texture' : 'textures/uranus.jpg'},
'neptune' : {'m' : 1.02e+26, 'r' : 24622, 'p' : [0,4.5e10,0], 'v' : [5.4*x,0,0], 'av' : [0,0,1.08e-4], 'temperature' : 100, 'texture' : 'textures/neptune.jpg'},
'moon' : {'m' : 7.48e+22, 'r' : 1738, 'p' : [384399,15e7,0], 'v' : [30*x,1*x,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/moon.jpg'}
},
'time' : 10000
}, 
'sim2' : {
'objects' : {
'venus' : {'m' : 4.87e+24, 'r' : 6052, 'p' : [0,0,0], 'v' : [0,0,0], 'av' : [0,0,0], 'temperature' : 6500, 'texture' : 'textures/earth.jpg'},
'earth' : {'m' : 5.97e+24, 'r' : 6371, 'p' : [2000,1e5,0], 'v' : [0,-100,0], 'av' : [0,0,0], 'temperature' : 100, 'texture' : 'textures/earth.jpg'}
},
'time' : 10
}}