from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import LVector3
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomNode, GeomLinestrips
from panda3d.core import Material
from direct.gui.OnscreenText import OnscreenText
from math import pi, sin, cos
import numpy
from body import Body
import values
import random
import sys
t = 600
g = 6.67408e-17
tick = 0.003
x = 35
scale = 1
geoms = 600
def getforce (o2, o1) :
	k = o1.mass*o2.mass*g
	d = k/numpy.linalg.norm(numpy.subtract(o2.pos, o1.pos))**3
	return numpy.multiply(d, numpy.subtract(o2.pos,o1.pos))

class Test(ShowBase) :
	def __init__ (self):
		ShowBase.__init__(self)
		b = OnscreenImage(parent=render2d, image="textures/sky.jpg")
		base.cam.node().getDisplayRegion(0).setSort(20)
		self.gNode = GeomNode('gnode')
		n = render.attachNewNode(self.gNode)
		self.bodies = []
		self.loadModels()
		self.setUpLights()
		m = Material()
		m.setEmission((1,1,1,1))
		self.bodies[0].node.setMaterial(m)
		NodePath(self.gNode).setMaterial(m)
		self.taskMgr.doMethodLater(tick, self.physTask, 'PhysTask')
		camera.reparentTo(self.bodies[3].node)
		camera.lookAt(self.bodies[3].node)
		base.camLens.setFov(1000000000*100)
		self.initText()
		self.setUpKeys()
	
	def physTask(self, task) :
		for o in self.bodies :
			o.setPos(numpy.sum([o.pos, numpy.multiply(t, o.v)], axis = 0))
			o.lines.drawTo(o.node.getPos())
			o.lines.create(o.gNode)
			if (len(o.gNode.getGeoms()) > geoms) :
				o.gNode.removeGeom(0)
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
		self.addPlanet('venus')
		self.addPlanet('earth')
		self.addPlanet('mars')
		self.addPlanet('jupiter')
		self.addPlanet('saturn')
		self.addPlanet('uranus')
		self.addPlanet('neptune')
		self.addPlanet('moon')
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
		
	def initText(self) :
		self.speedText = OnscreenText(text = '600 seconds per tick [+/-]', pos = (-0.9, 0.9), scale = 0.07, fg = (1,1,1,1))
		
	def setUpKeys(self) :
	
		self.keys = {"inc", "dec"}
		self.accept("escape", sys.exit)
		self.accept("+", self.incSpeed)
		self.accept("-", self.decSpeed)

	def incSpeed(self) :
		global t
		t+= 20
		self.speedText.setText('{0} seconds per tick [+/-]'.format(t))
	def decSpeed(self) :
		global t
		t-= 20
		self.speedText.setText('{0} seconds per tick [+/-]'.format(t))
	
	def addPlanet(self, name):
		planet = loader.loadModel('models/sphere')
		planet.setTexture(loader.loadTexture('textures/' + name + '.jpg'))
		r = values.values[name]['r']*scale
		planet.setSx(r)
		planet.setSy(r)
		planet.setSz(r)
		body = Body(planet, values.values[name]['m'], numpy.array(values.values[name]['p']), numpy.array(values.values[name]['v']), numpy.array(values.values[name]['av']))
		lines = LineSegs()
		lines.setThickness(1)
		gn = lines.create()
		m = Material()
		m.setEmission((random.random() ,random.random() ,random.random() ,1))
		NodePath(gn).setMaterial(m)
		NodePath(gn).reparentTo(render)
		body.setTrail(lines, gn)
		planet.reparentTo(render)
		self.bodies.append(body)
		
		
test = Test()
test.run()