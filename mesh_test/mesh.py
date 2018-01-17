from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import random

class Test(ShowBase) :
        def __init__ (self):
                ShowBase.__init__(self)
                sphere = loader.loadModel('models/planet_sphere')
                sphere.setTexture(loader.loadTexture('textures/sun.jpg'))
                #sphere.reparentTo(render)
                sphere.setPos(render, -1, 10, -1)
                camera.setPos(render, 0, -10, 0)

                lines = LineSegs()
                lines.setThickness(1)
                gn = lines.create()
                print(len(gn.getGeoms()))
                NodePath(gn).reparentTo(render)
                lines.moveTo(-1, 10, -1)

             
                print(len(gn.getGeoms()))
                lines.moveTo(-1, 10, -1)
                
                print(len(gn.getGeoms()))
                lines.drawTo(1, 10, -1)

                gn = lines.create(gn)
                print(len(gn.getGeoms()))
test = Test()
test.run()
