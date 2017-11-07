import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import LVector3
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomNode, GeomLinestrips
from panda3d.core import Material, WindowProperties, MouseButton
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
geoms = 600
fov = 100
scale = 1
def getforce (o2, o1) :
	k = o1.mass*o2.mass*g
	d = k/numpy.linalg.norm(numpy.subtract(o2.pos, o1.pos))**3
	return numpy.multiply(d, numpy.subtract(o2.pos,o1.pos))

class Test(ShowBase) :
	def __init__ (self):
		log.info('Loading started')
		ShowBase.__init__(self)
		b = OnscreenImage(parent=render2d, image="textures/sky.jpg")
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
		self.taskMgr.add(self.controllTask, 'ControllTask')
		self.cameraSetup()
		self.initText()
		self.setUpKeys()
		log.info('Loading done')
	
	def cameraSetup(self) :
		self.cameraNode = render.attachNewNode('cameraNode')
		camera.reparentTo(self.cameraNode)
		base.camLens.setFov(100)
		base.cam.node().getDisplayRegion(0).setSort(20)
		self.cameraNode.reparentTo(self.bodies[0].node)
		self.cameraNode.setCompass(render)
	
	def physTask(self, task) :
		for o in self.bodies :
			o.setPos(numpy.sum([o.pos, numpy.multiply(t, o.v)], axis = 0))
			o.lines.drawTo(o.getPos())
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
		
	def controllTask(self, task) :
		global fov
		if self.keys['fovup'] and fov < 360 :
			fov+=(180-fov)/100
			base.camLens.setFov(fov)
		if self.keys['fovdown'] and fov > 0.5 :
			fov-=(fov)/100
			base.camLens.setFov(fov)
		parent = self.cameraNode.getParent()
		if self.keys['fwd'] == 1:
			camera.setY(camera, 0.1)
		if self.keys['bwd'] == 1:
			camera.setY(camera, -0.1)
			
		if self.keys['lft'] == 1:
			camera.setX(camera, -0.1)
		if self.keys['rt'] == 1:
			camera.setX(camera, 0.1)	
		
		return Task.cont
	
	def loadModels(self) : 
		planets = ['sun', 'mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'moon']
		for x in planets :
			self.addPlanet(x)		
		
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
		self.scaleText = OnscreenText(text = 'scale : 1 [Z/X]', pos = (-0.9, 0.8), scale = 0.07, fg = (1,1,1,1))
		
	def setUpKeys(self) :
	
		self.keys = {'fovup' : 0, 'fovdown' : 0, 'fwd' : 0, 'bwd' : 0, 'lft' : 0, 'rt' : 0}
		self.accept("escape", sys.exit)
		self.accept("+", self.incSpeed)
		self.accept("-", self.decSpeed)
		self.accept("z", self.incScale)
		self.accept("x", self.decScale)

		self.accept('arrow_up', self.setKey, ['fovdown', 1])
		self.accept('arrow_up-up', self.setKey, ['fovdown', 0])
		self.accept('arrow_down', self.setKey, ['fovup', 1])
		self.accept('arrow_down-up', self.setKey, ['fovup', 0])
		
		self.accept('w', self.setKey, ['fwd', 1])
		self.accept('w-up', self.setKey, ['fwd', 0])
		self.accept('s', self.setKey, ['bwd', 1])
		self.accept('s-up', self.setKey, ['bwd', 0])
		self.accept('d', self.setKey, ['rt', 1])
		self.accept('d-up', self.setKey, ['rt', 0])
		self.accept('a', self.setKey, ['lft', 1])
		self.accept('a-up', self.setKey, ['lft', 0])
		
		self.setUpMouse()
	
	def setKey(self, key, val) :
		self.keys[key] = val
	
	def setUpMouse(self) :

		self.disableMouse()

		self.mouseMagnitude = 3

		self.rotateX, self.rotateY = 0, 0

		self.lastMouseX, self.lastMouseY = None, None

		taskMgr.add(self.mouseTask, "Mouse Task")

	def mouseTask (self, task):
		mw = base.mouseWatcherNode
		wp = WindowProperties()

		hasMouse = mw.hasMouse() 
		if hasMouse and mw.is_button_down(MouseButton.one()):
			x, y = mw.getMouseX(), mw.getMouseY()
			if self.lastMouseX is not None:
				
				dx, dy = x - self.lastMouseX, y - self.lastMouseY

			else:
				dx, dy = 0, 0

			self.lastMouseX, self.lastMouseY = x, y
			
		else:
			x, y, dx, dy, self.lastMouseX, self.lastMouseY = 0, 0, 0, 0, 0, 0

		self.rotateX += dx * 10 * self.mouseMagnitude
		self.rotateY += dy * 10 * self.mouseMagnitude

		self.cameraNode.setH(self.rotateX)
		self.cameraNode.setP(self.rotateY)
		return Task.cont

	def incSpeed(self) :
		global t
		t+= 20
		self.speedText.setText('{0} seconds per tick [+/-]'.format(t))
		
	def decSpeed(self) :
		global t
		t-= 20
		self.speedText.setText('{0} seconds per tick [+/-]'.format(t))
		
	def incScale(self) : 
		factor = 3
		global scale 
		scale*= factor
		self.scaleText.setText('scale : {0} [Z/X]'.format(scale))
		
		for b in self.bodies :
			b.node.setScale(b.node.getScale()[0]*factor)
		
	def decScale(self) : 
		factor = 3
		global scale 
		if scale >= factor :
			scale//= factor
			for b in self.bodies :
				b.node.setScale(b.node.getScale()[0]//factor)
			self.scaleText.setText('scale : {0} [Z/X]'.format(scale))
	
	def addPlanet(self, name):
		planet = loader.loadModel('models/planet_sphere')
		planet.setTexture(loader.loadTexture('textures/' + name + '.jpg'))
		r = values.values[name]['r']*scale
		planet.setScale(r)
		planet.reparentTo(render)
		body = Body(planet, values.values[name]['m'], numpy.array(values.values[name]['p']), numpy.array(values.values[name]['v']), numpy.array(values.values[name]['av']))
		lines = LineSegs()
		lines.setThickness(1)
		lines.moveTo(planet.getPos())
		gn = lines.create()
		m = Material()
		m.setEmission((random.random() ,random.random() ,random.random() ,1))
		NodePath(gn).setMaterial(m)
		NodePath(gn).reparentTo(render)
		body.setTrail(lines, gn)
		self.bodies.append(body)
		

test = Test()
test.run()