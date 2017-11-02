from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import LVector3
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomNode, GeomLinestrips
from panda3d.core import Material
from math import pi, sin, cos
import numpy
from body import Body
import values
import random
t = 600
g = 6.67408e-11/1000**2
tick = 0.010
x = 35
geoms = 600
def getforce (o2, o1) :
	k = o1.mass*o2.mass*g
	d = k/numpy.linalg.norm(numpy.subtract(o2.pos, o1.pos))**3
	return numpy.multiply(d, numpy.subtract(o2.pos,o1.pos))

scale = 10000
class Test(ShowBase) :
	def __init__ (self):
		ShowBase.__init__(self)
		b = OnscreenImage(parent=render2d, image="textures/sky.jpg")
		base.cam.node().getDisplayRegion(0).setSort(20)
		self.gNode = GeomNode('gnode')
		n = render.attachNewNode(self.gNode)
		self.bodies = []
		self.loadModels()
		camera.reparentTo(self.bodies[3].node)
		camera.lookAt(self.bodies[3].node)
		base.camLens.setFov(1000000000*100)
		self.setUpLights()
		m = Material()
		m.setEmission((1,1,1,1))
		self.bodies[0].node.setMaterial(m)
		NodePath(self.gNode).setMaterial(m)
		self.taskMgr.doMethodLater(tick, self.physTask, 'PhysTask')
	
	def spinCameraTask(self, task):
		angleDegrees = task.time * 24.0
		self.camera.setHpr(angleDegrees, 0, 0)
		return Task.cont
		
	def physTask(self, task) :
		for o in self.bodies :
			o.setPos(numpy.sum([o.pos, numpy.multiply(t, o.v)], axis = 0), scale)
			o.lines.drawTo(o.node.getPos())
			if (o.lines.getNumVertices() > 200) :
				del o.lines.getVertices()[0] 
			o.lines.create(o.gNode)
			if (len(o.gNode.getGeoms()) > geoms) :
				o.gNode.removeGeom(0)
			print(len(o.gNode.getGeoms()))
			thpr = o.node.getHpr()
			hpr = numpy.sum([numpy.array([thpr[0],thpr[1],thpr[2]]), numpy.multiply(t, o.av)], axis = 0)
			o.node.setHpr(hpr[0], hpr[1], hpr[2])
			for o2 in self.bodies :
				if o2 != o :
					f = getforce(o2, o)
					a = numpy.divide(f, o.mass)
					o.v = numpy.sum([o.v, numpy.multiply(t, a)], axis = 0)
		return Task.again
	
	def loadModels(self) : 
		self.addPlanet('sun')
		self.addPlanet('mercury')
		self.bodies[-1].setPos(numpy.array([0,57909227,0]), scale)
		self.bodies[-1].v = numpy.array([50*x, 0 ,0])
		self.addPlanet('venus')
		self.bodies[-1].setPos(numpy.array([0, 108942109, 0]), scale)
		self.bodies[-1].v = numpy.array([35*x, 0 ,0])
		self.addPlanet('earth')
		self.bodies[-1].setPos(numpy.array([0, 150000000, 0]), scale)
		self.bodies[-1].v = numpy.array([30*x, 0 ,0])
		self.bodies[-1].av = numpy.array([0,0,0])
		self.addPlanet('mars')
		self.bodies[-1].setPos(numpy.array([0, 2.3e+8, 0]), scale)
		self.bodies[-1].v = numpy.array([24*x, 0 ,0])
		self.addPlanet('jupiter')
		self.bodies[-1].setPos(numpy.array([0, 7.79e+8, 0]), scale)
		self.bodies[-1].v = numpy.array([13*x, 0 ,0])
		self.addPlanet('uranus')
		self.bodies[-1].setPos(numpy.array([0, 2.9e+10, 0]), scale)
		self.bodies[-1].v = numpy.array([6.8*x, 0 ,0])
		self.addPlanet('neptune')
		self.bodies[-1].setPos(numpy.array([0, 4.5e+10, 0]), scale)
		self.bodies[-1].v = numpy.array([5.4*x, 0 ,0])
		self.addPlanet('moon')
		self.bodies[-1].setPos(numpy.array([384399, 150000000, 0]), scale)
		self.bodies[-1].v = numpy.array([30*x, 1*x ,0])
		for o in self.bodies :
			o.lines.moveTo(o.node.getPos())
		
	def setUpLights(self) : 
		plight = PointLight('plight')
		plight.setColor(VBase4(3, 3, 3, 1))
		plnp = render.attachNewNode(plight)
		plnp.setPos(0, 0, 0)
		render.setLight(plnp)

		# Important! Enable the shader generator.
		render.setShaderAuto()

		# default values
		self.cameraSelection = 0
		self.lightSelection = 0
		
	def addPlanet(self, name):
		planet = loader.loadModel('models/sphere')
		planet.setTexture(loader.loadTexture('textures/' + name + '.jpg'))
		r = values.values[name]['r']/scale
		planet.setSx(r)
		planet.setSy(r)
		planet.setSz(r)
		body = Body(planet, values.values[name]['m'])
		lines = LineSegs()
		lines.setThickness(1)
		gn = lines.create()
		m = Material()
		m.setEmission((1,0.4,0.4,1))
		NodePath(gn).setMaterial(m)
		NodePath(gn).reparentTo(render)
		body.setTrail(lines, gn)
		planet.reparentTo(render)
		self.bodies.append(body)
		
		
test = Test()
test.run()