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
from direct.interval.LerpInterval import LerpPosInterval
from math import pi, sin, cos
import numpy
from body import Body
import values
import random
import sys
t = 10000
g = 6.67408e-20
tick = 1/100
geoms = 1500
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
		
		for i in range(geoms):
			for o in self.bodies :
                        
				o.setPos(numpy.sum([o.pos, numpy.multiply(t, o.v)], axis = 0))
				
				o.wayPoints.append(o.getPos())
				
				thpr = o.node.getHpr()
				hpr = numpy.sum([numpy.array([thpr[0],thpr[1],thpr[2]]), numpy.multiply(t, o.av)], axis = 0)
				o.node.setHpr(hpr[0], hpr[1], hpr[2])
				for o2 in self.bodies :
					if o2 != o :
						f = getforce(o2, o)
						a = numpy.divide(f, o.mass)
						o.v = numpy.sum([o.v, numpy.multiply(t, a)], axis = 0)
			if i % 100 == 0 : log.info(str(i))
		
		
		self.setUpLights()
		m = Material()
		m.setEmission((1,1,1,1))
		self.bodies[0].node.setMaterial(m)
		NodePath(self.gNode).setMaterial(m)
		self.taskMgr.doMethodLater(tick, self.physTask, 'PhysTask')
		self.taskMgr.add(self.controllTask, 'ControllTask')
		self.setUpKeys()
		self.cameraSetup()
		self.initText()

		self.gNode = GeomNode("Trails")
		NodePath(self.gNode).reparentTo(render)
		
		#self.taskMgr.doMethodLater(tick, self.drawTask, "DrawTask")
		
		log.info('Loading done')
	
	def cameraSetup(self) :
		self.cameraNode = render.attachNewNode('cameraNode')
		camera.reparentTo(self.cameraNode)
		base.camLens.setFov(100)
		base.cam.node().getDisplayRegion(0).setSort(20)
		self.cameraNode.reparentTo(self.bodies[0].node)
		self.cameraNode.lookAt(self.bodies[0].node)
		
		camera.setY(-2700);
		
		self.cameraNode.setP(90);
		self.rotateY = 90;
		self.cameraNode.setCompass()
		self.curPlanet = 0
	
	def physTask(self, task) :
		for o in self.bodies :
            
			o.setPos(numpy.sum([o.pos, numpy.multiply(t, o.v)], axis = 0))
			
			wps = o.wayPoints
            
			wps.append(o.getPos())
			
			if(len(wps) > geoms) : wps.pop(0)
			
			thpr = o.node.getHpr()
			hpr = numpy.sum([numpy.array([thpr[0],thpr[1],thpr[2]]), numpy.multiply(t, o.av)], axis = 0)
			o.node.setHpr(hpr[0], hpr[1], hpr[2])
			for o2 in self.bodies :
				if o2 != o :
					f = getforce(o2, o)
					a = numpy.divide(f, o.mass)
					o.v = numpy.sum([o.v, numpy.multiply(t, a)], axis = 0)
		self.draw()
		return Task.again
		
	def controllTask(self, task) :
	
		d = camera.getDistance(self.cameraNode.parent)
		
		if self.keys['zoomIn'] :
			camera.setY(camera, d/60.0)
		if self.keys['zoomOut']:
			
			camera.setY(camera, -d/60.0)
		parent = self.cameraNode.getParent()
		
		if self.keys['fwd'] == 1:
		
			self.detachCamera()
			self.cameraNode.setY(self.cameraNode, -self.fwdStep)
			
			self.fwdStep *= 1.01
		
		else : self.fwdStep = 0.1
		
		if self.keys['bwd'] == 1:
		
			self.detachCamera()
			camera.setY(camera, self.bwdStep)
			
			self.bwdStep *= 1.01
		
		else : self.bwdStep = 0.1
			
		if self.keys['lft'] == 1:
		
			self.detachCamera()
			camera.setY(camera, -self.lftStep)
			self.lftStep *= 1.01
		
		else : self.lftStep = 0.1
			
		if self.keys['rt'] == 1:
		
			self.detachCamera()
			camera.setX(camera, self.rtStep)
			self.rtStep *= 1.01
		
		else : self.rtStep = 0.1
		
		if self.keys['lft'] == 1:
		
			self.detachCamera()
			camera.setX(camera, -self.lftStep)
			self.lftStep *= 1.01
		
		else : self.lftStep = 0.1
		
		global t;		
		
		if self.keys['incSpeed'] == 1:
			t*=self.accFactor;
			self.accFactor*=1.001
			self.speedText.setText('{0} seconds per tick [+/-]'.format(round(t, 2)))
		
		if self.keys['incSpeed'] == 0 :
			self.accFactor = 1.01
		
		if self.keys['decSpeed'] == 1:
			t/=self.decFactor;
			self.decFactor*=1.001
			self.speedText.setText('{0} seconds per tick [+/-]'.format(round(t, 2)))
			
		if self.keys['decSpeed'] == 0 :
			self.decFactor = 1.01

		return Task.cont
	
	def loadModels(self) : 
		planets = ['sun', 'mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
		for x in planets :
			self.addPlanet(x)		
		
	def setUpLights(self) : 
		plight = PointLight('plight')
		plight.setColor(VBase4( 3, 3, 3, 1))
		plnp = render.attachNewNode(plight)
		plnp.setPos(0, 0, 0)
		render.setLight(plnp)

		# Important! Enable the shader generator.
		render.setShaderAuto()

		# default values
		self.cameraSelection = 0
		self.lightSelection = 0
		
	def initText(self) :
		self.speedText = OnscreenText(text = str(t) + ' seconds per tick [+/-]', pos = (-0.9, 0.9), scale = 0.07, fg = (1,1,1,1))
		self.scaleText = OnscreenText(text = 'scale : 1 [Z/X]', pos = (-0.9, 0.8), scale = 0.07, fg = (1,1,1,1))
		
	def setUpKeys(self) :
	
		self.keys = {'zoomIn' : 0, 'zoomOut' : 0, 'fwd' : 0, 'bwd' : 0, 'lft' : 0, 'rt' : 0, 'incSpeed' : 0, 'decSpeed' : 0}
		self.accept("escape", sys.exit)
		self.accept("z", self.incScale)
		self.accept("x", self.decScale)
		self.accept('r', self.resetCam)
		self.accept('y', self.detachCamera)
		self.accept('i', self.logCam)

		self.accept('arrow_up', self.setKey, ['zoomIn', 1])
		self.accept('arrow_up-up', self.setKey, ['zoomIn', 0])
		self.accept('arrow_down', self.setKey, ['zoomOut', 1])
		self.accept('arrow_down-up', self.setKey, ['zoomOut', 0])
		
		self.accept("+", self.setKey, ['incSpeed', 1])
		self.accept("+-up", self.setKey, ['incSpeed', 0])
		self.accept("-", self.setKey, ['decSpeed', 1])
		self.accept("--up", self.setKey, ['decSpeed', 0])

		
		self.accept('w', self.setKey, ['fwd', 1])
		self.accept('w-up', self.setKey, ['fwd', 0])
		self.accept('s', self.setKey, ['bwd', 1])
		self.accept('s-up', self.setKey, ['bwd', 0])
		self.accept('d', self.setKey, ['rt', 1])
		self.accept('d-up', self.setKey, ['rt', 0])
		self.accept('a', self.setKey, ['lft', 1])
		self.accept('a-up', self.setKey, ['lft', 0])
		self.accept('o', self.prevPlanet)
		self.accept('p', self.nextPlanet)
		
		self.accFactor = 1.01
		self.decFactor = 1.01
		
		self.fwdStep = 0.1
		self.bwdStep = 0.1
		self.lftStep = 0.1
		self.rtStep = 0.1
		
		self.setUpMouse()
	
	def logCamera (self) :
		log.info("Logging camera")
		log.info(camera.getPos(render))
		log.info(camera.getHpr(render))
		log.info("Logging cameraNode")
		log.info(self.cameraNode.getPos(render))
		log.info(self.cameraNode.getHpr(render))
	
	def setKey(self, key, val) :
		self.keys[key] = val
	
	def resetCam(self) :
		self.attachCam(self.bodies[self.curPlanet].node)
	
	def attachCam(self, node) :

		if self.detached : 
		
			self.detached = False
			
			self.cameraNode.wrtReparentTo(render)
			camera.wrtReparentTo(self.cameraNode)
			
			hpr = camera.getHpr()
			
			camera.setHpr(0,0,0)
			
			self.cameraNode.wrtReparentTo(node)
			self.cameraNode.setHpr(hpr)
			
			self.rotateX = self.cameraNode.getH()
			self.rotateY = self.cameraNode.getP()
			
			self.cameraNode.setPos(0,0,0)
		
	def logCam(self):
		log.info('camera')
		log.info(camera.getPos())
		log.info(camera.getHpr())
		log.info('node')
		log.info(self.cameraNode.getPos())
		log.info(self.cameraNode.getHpr())

		
	def nextPlanet(self) :
		if self.curPlanet < len(self.bodies) - 1 :
			self.curPlanet += 1
			self.attachCam(self.bodies[self.curPlanet].node)
			self.cameraNode.setPos(0,0,0)
			camera.setY(-2)
			
	def prevPlanet(self) :
		if self.curPlanet > 0 :
			self.curPlanet -= 1
			self.attachCam(self.bodies[self.curPlanet].node)
			self.cameraNode.setPos(0,0,0)
			camera.setY(-2)
			
	def setUpMouse(self) :

		self.disableMouse()

		self.mouseMagnitude = 3

		self.rotateX, self.rotateY, self.rotateXd, self.rotateYd = 0, 0, 0, 0

		self.lastMouseX, self.lastMouseY = None, None

		taskMgr.add(self.mouseTask, "Mouse Task")
		self.scrolling = False
		self.detached = False
	
	def detachCamera(self):
		if not self.detached : 
			self.detached = True
			camera.wrtReparentTo(render)
			self.cameraNode.wrtReparentTo(camera)
	
	def mouseTask (self, task):
		mw = base.mouseWatcherNode
		wp = WindowProperties()

		hasMouse = mw.hasMouse() 
		if hasMouse and mw.is_button_down(MouseButton.one()):
			x, y = mw.getMouseX(), mw.getMouseY()
			
			if not self.scrolling :
					self.lastMouseX, self.lastMouseY = x, y
					self.scrolling = True
			
			if self.lastMouseX is not None:
				
				dx, dy = x - self.lastMouseX, y - self.lastMouseY

			else:
				dx, dy = 0, 0

			self.lastMouseX, self.lastMouseY = x, y
			
		else:
			x, y, dx, dy, self.lastMouseX, self.lastMouseY = 0, 0, 0, 0, 0, 0
			self.scrolling = False
		
		if self.detached and self.scrolling :
			self.rotateX += dx * 10 * self.mouseMagnitude
			self.rotateY -= dy * 10 * self.mouseMagnitude

			self.camera.setH(self.rotateX)
			self.camera.setP(self.rotateY)
		elif not self.detached and self.scrolling :
			self.rotateX += dx * 10 * self.mouseMagnitude
			self.rotateY -= dy * 10 * self.mouseMagnitude

			self.cameraNode.setH(self.rotateX)
			self.cameraNode.setP(self.rotateY)
		return Task.cont

	def draw(self):
		
		lines = LineSegs()
		
		NodePath(self.gNode).detachNode()
		
		self.gNode = lines.create()
		
		m = Material()
		m.setEmission((1,1,1,1))
		#NodePath(self.gNode).setMaterial(m)
		
		NodePath(self.gNode).reparentTo(render)
		for o in self.bodies:
			
			lines.setColor(o.trlClr)
			
			for wp in o.wayPoints:
					lines.drawTo(wp)
			self.gNode = lines.create(self.gNode)
		
		#return Task.again
                
	
	def incScale(self) : 
		factor = 3
		global scale 
		scale*= factor
		self.scaleText.setText('scale : {0} [Z/X]'.format(scale))
		
		pos = camera.getPos(render)
		
		for b in self.bodies :
			b.node.setScale(b.node.getScale()[0]*factor)
			
		camera.setPos(render, pos)
		
		
	def decScale(self) : 
		factor = 3
		global scale 
		if scale >= factor :
			scale//= factor

			
			pos = camera.getPos(render)
			
			for b in self.bodies :
				b.node.setScale(b.node.getScale()[0]//factor)
			self.scaleText.setText('scale : {0} [Z/X]'.format(scale))
			
			pos = camera.getPos(render)
			for b in self.bodies :
				b.node.setScale(b.node.getScale()[0]//factor)
			self.scaleText.setText('scale : {0} [Z/X]'.format(scale))

			camera.setPos(render, pos)
	
	def addPlanet(self, name):
		planet = loader.loadModel('models/planet_sphere')
		planet.setTexture(loader.loadTexture('textures/' + name + '.jpg'))
		r = values.values[name]['r']*scale
		planet.setScale(r)
		planet.reparentTo(render)
		
		trlClr = (random.random(), random.random(), random.random(), 1.0)
		
		body = Body(planet, values.values[name]['m'], numpy.array(values.values[name]['p']), numpy.array(values.values[name]['v']), numpy.array(values.values[name]['av']), trlClr)
		
		
		
		self.bodies.append(body)
		

test = Test()
test.run()
