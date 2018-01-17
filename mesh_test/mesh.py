from panda3d.core import *
from panda3d.core import MeshDrawer
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

                generator = MeshDrawer()
                generator.setBudget(1000)
                generatorNode = generator.getRoot()
                generatorNode.reparentTo(render)
               
##                generatorNode.setDepthWrite(False)
##                generatorNode.setTransparency(True)
##                generatorNode.setTwoSided(True)
##                generatorNode.setTexture(loader.loadTexture("textures/mesh.png"))
##                generatorNode.setBin("fixed",0)
##                generatorNode.setLightOff(True)

                generator.begin(base.cam, begin)
                generator.linkSegment(Vec3(-1, 10, -1), Vec4(0,0,1,1), 3, Vec4(1,1,1,1))
                generator.linkSegment(Vec3(1, 10, 1), Vec4(0,0,1,1), 3, Vec4(1,1,1,1))
                generator.linkSegmentEnd( Vec4(0,0,1,1), Vec4(1,1,1,1))
                generator.end()
        def drawtask(taks):
    """ this is called every frame to regen the mesh """
            t = globalClock.getFrameTime()
            generator.begin(base.cam,render)
            for v,pos,frame,size,color in particles:        
                generator.billboard(pos+v*t,frame,size*sin(t*2)+3,color)

            for start,stop,frame,size,color in lines:
                generator.segment(start,stop,frame,size*sin(t*2)+2,color)
            generator.end()
            return taks.cont
test = Test()
test.run()
