import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import sys

import importPanda

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
from direct.filter.CommonFilters import CommonFilters
from panda3d.bullet import BulletWorld, BulletSphereShape, BulletRigidBodyNode
from math import pi, sin, cos, copysign
import numpy
from body import Body
import simulations
import random

import argparse

import pickle
t = 10000
G = 0

fov = 100
tick = 1/100
scale = 1

parser = argparse.ArgumentParser(description='Load simulation.')
parser.add_argument('--geoms', metavar='wpts', type=int,
                   help='number of trajectory points', default=1500)
parser.add_argument('--sim', dest='simulation',
                   help='name of simulation to load', default='sim1')
parser.add_argument('--igeoms', dest='igeoms', type=int,
                   help='number of trajectory points to calculate before simulation', default=1500)
				   
args = parser.parse_args()
igeoms = args.igeoms
geoms = args.geoms
simulation = args.simulation

def getImpulse (o2, o1) :
	k = o1.rbnode.getMass()*o2.rbnode.getMass()*G
	
	r = o1.node.getPos() - o2.node.getPos()
	
	d = k/(VBase3(r).length())**3
	
	x, y, z = r.getX(), r.getY(), r.getZ()
	
	return Vec3(-x*t*d,-y*t*d,-z*t*d)
	
	
	return numpy.multiply(d, numpy.subtract(o2.pos,o1.pos))
	
class Test(ShowBase) :
	def __init__ (self):
		log.info('Loading started')
		log.info('Initiallizing engine')
		ShowBase.__init__(self)
		self.gNode = GeomNode('gnode')
		n = render.attachNewNode(self.gNode)
		self.bodies = []
		
		
		self.massScale = 1e19
		
		global G
		G*=self.massScale
		
		self.world = BulletWorld()
		
		self.loadModels(simulations.simulations[simulation])
		
		log.info("Counting {} waypoints".format(geoms))
		
		self.counter = 0
		
		for i in range(igeoms):
			for o in self.bodies :			
				for o2 in self.bodies :
					if o2 != o :
						imp = getImpulse(o2, o)
						o.rbnode.applyCentralImpulse(imp)
					self.counter+=1
			#self.bodies[0].setTemperature(self.bodies[0].temperature*1.005)
			self.world.doPhysics(t, 10, t/10)
			
			for o in self.bodies : 
				wps = o.wayPoints
				
				wps.append(o.node.getPos())
				
				#if(len(wps) > geoms) : wps.pop(0)
			if i % 50 == 0 :
				log.info("{0:.2f}%".format(i/igeoms*100))
		
		
		
		log.info("100.0%")
		
		#NodePath(self.gNode).setMaterial(m)
		self.taskMgr.add(self.physTask, 'PhysTask')
		self.taskMgr.add(self.controllTask, 'ControllTask')
		self.setUpKeys()
		self.setUpCamera()
		
		self.initText()

		self.counters = [0]
		
		self.gNode = GeomNode("Trails")
		NodePath(self.gNode).reparentTo(render)
		alight = AmbientLight('pathLight')
		alight.setColor(VBase4(1, 1, 1, 1))
		self.pathLight = render.attachNewNode(alight)
		NodePath(self.gNode).setLight(self.pathLight)
		NodePath(self.gNode).reparentTo(render)
		self.setUpLights()
		#self.taskMgr.doMethodLater(tick, self.drawTask, "DrawTask")
		
		#self.bodies[0].model.setShaderOff()
        
		log.info('Loading done')
	
	def setUpCamera(self) :
		self.cameraNode = render.attachNewNode('cameraNode')
		camera.reparentTo(self.cameraNode)
		base.camLens.setFov(106)
		base.camLens.setNearFar(0.1, 1e12)

		
		self.cameraNode.reparentTo(self.bodies[0].model)
		self.cameraNode.lookAt(self.bodies[0].model)
		
		camera.setY(-5);
		
		self.cameraNode.setP(-90);
		self.rotateY = -90;
		self.cameraNode.setCompass()
		self.curPlanet = 0
		
		log.info("Camera is set up")
		
		self.filters = CommonFilters(base.win, base.cam)
		filterok = self.filters.setBloom(
			blend=(0, 0, 0, 1), desat=-0.5, intensity=3.0, size=1)
		
		log.info("Filters are set up")
		
		self.setUpSkyBox()
		
		
	def setUpSkyBox(self):
		self.skybox = loader.loadModel("models/planet_sphere")
		self.skybox.setTexture(loader.loadTexture("textures/sky.jpg"))
		self.skybox.reparentTo(camera)
		self.skybox.setShaderOff()
		self.skybox.setLightOff()
		self.skybox.setTwoSided(True)
		self.skybox.setBin('background', 10)
		self.skybox.setDepthWrite(0)
		self.skybox.setScale(20000)
		self.skybox.setCompass()
		m = Material()
		m.setEmission((1,1,1,0))
		self.skybox.setMaterial(m)
		log.info("Skybox is set up")
	
	def countEnergy(self, o) :
		mass = o.rbnode.getMass()
		El = mass*self.massScale/2*o.rbnode.getLinearVelocity().length()**2
		Er = mass*0.2*self.massScale*o.radius**2*o.rbnode.getAngularVelocity().length()**2
		return El + Er
	def physTask(self, task) :
	
		for o in self.bodies :			
			for o2 in self.bodies :
				if o2 != o :
					imp = getImpulse(o2, o)
					o.rbnode.applyCentralImpulse(imp)
		#self.bodies[0].setTemperature(self.bodies[0].temperature*1.005)
		self.counters[0]+=1
		if self.counters[0] % 10 ==  0: 
			s = 0
			for o in self.bodies:
				s += self.countEnergy(o)
			log.info(s)
		
		self.world.doPhysics(t, 10, t/10)
		
		for o in self.bodies : 
			wps = o.wayPoints
            
			wps.append(o.node.getPos())
			
			if(len(wps) > geoms) : wps.pop(0)
		
		self.draw()
		
		return Task.cont
		
	def controllTask(self, task) :
	
		d = camera.getDistance(self.cameraNode.parent)
		
		if self.keys['zoomIn'] :
			camera.setY(min(camera.getY()*(1-self.zoomSpeed), -1.1))
		if self.keys['zoomOut']:
			
			camera.setY(camera.getY()*(1+self.zoomSpeed))
		parent = self.cameraNode.getParent()
		
		if self.keys['fwd'] == 1:
		
			self.detachCamera()
			camera.setY(camera, self.fwdStep)
			
			self.fwdStep *= 1.01
		
		else : self.fwdStep = 0.1
		
		if self.keys['bwd'] == 1:
		
			self.detachCamera()
			camera.setY(camera, -self.bwdStep)
			
			self.bwdStep *= 1.01
		
		else : self.bwdStep = 0.1
			
		if self.keys['lft'] == 1:
		
			self.detachCamera()
			camera.setX(camera, -self.lftStep)
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
	
	def loadModels(self, simulation) : 
		for x in simulation['objects'].keys() :
			self.addPlanet(x, simulation)		
		global t 
		t = simulation['time']
		log.info("Loaded models")
		
	def setUpLights(self) : 
		plight = PointLight('plight')
		plight.setColor(VBase4( 3, 3, 3, 1))
		plnp = render.attachNewNode(plight)
		plnp.reparentTo(self.bodies[0].model)
		render.setLight(plnp)

		# Important! Enable the shader generator.
		render.setShaderAuto()

		# default values
		self.cameraSelection = 0
		self.lightSelection = 0
		
		log.info("Lights are set up")
		
	def initText(self) :
		self.speedText = OnscreenText(text = str(t) + ' seconds per tick [+/-]', pos = (-0.9, 0.9), scale = 0.07, fg = (1,1,1,1))
		self.scaleText = OnscreenText(text = 'scale : 1 [Z/X]', pos = (-0.9, 0.8), scale = 0.07, fg = (1,1,1,1))
		
	def setUpKeys(self) :
	
		self.keys = {'zoomIn' : 0, 'zoomOut' : 0, 'fwd' : 0, 'bwd' : 0, 'lft' : 0, 'rt' : 0, 'incSpeed' : 0, 'decSpeed' : 0}
		self.accept("escape", sys.exit)
		self.accept("z", self.incScale)
		self.accept("x", self.decScale)
		self.accept('r', self.resetCamera)
		self.accept('y', self.detachCamera)
		self.accept('i', self.logCamera)
		self.accept('u', self.logSomething)
		self.accept('1', self.debugFunction)
		self.accept('2', self.debugFunction2)

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
		
		self.zoomSpeed = 0.03
		self.setUpMouse()
		

		log.info("Controls are set up")
	def setKey(self, key, val) :
		self.keys[key] = val
	
	def resetCamera(self) :

		self.attachCamera(self.bodies[self.curPlanet].model)

	
	def attachCamera(self, model) :

		if self.detached : 
		
			self.detached = False
			
			self.cameraNode.wrtReparentTo(render)
			camera.wrtReparentTo(self.cameraNode)
			
			hpr = camera.getHpr()
			
			camera.setHpr(0,0,0)
			
			self.cameraNode.wrtReparentTo(model)
			self.cameraNode.setHpr(hpr)
			
			self.rotateX = self.cameraNode.getH()
			self.rotateY = self.cameraNode.getP()
			
			self.cameraNode.setScale(1)
			self.cameraNode.setPos(0,0,0)
			self.cameraNode.setScale(1)
		
	def logCamera(self):
		log.info('camera')
		log.info(camera.getPos())
		log.info(camera.getHpr())
		log.info('node')
		log.info(self.cameraNode.getPos(render))
		log.info(self.cameraNode.getHpr())
		log.info('skybox')
		log.info(self.skybox.getPos())
		log.info(self.skybox.getHpr())

		
	def nextPlanet(self) :
		if self.curPlanet < len(self.bodies) - 1 :
			self.curPlanet += 1
			self.detachCamera()
			self.attachCamera(self.bodies[self.curPlanet].model)

			
	def prevPlanet(self) :
		if self.curPlanet > 0 :
			self.curPlanet -= 1
			self.detachCamera()
			self.attachCamera(self.bodies[self.curPlanet].model)
			
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
		NodePath(self.gNode).setLight(self.pathLight)
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
			b.model.setScale(b.model.getScale()[0]*factor)

		self.cameraNode.setScale(1)
		camera.setPos(render, pos)

		
		
	def decScale(self) : 
		factor = 3
		global scale 
		if scale >= factor :
			scale//= factor
		
			pos = camera.getPos(render)
			for b in self.bodies :
				b.model.setScale(b.model.getScale()[0]//factor)
			self.scaleText.setText('scale : {0} [Z/X]'.format(scale))
			
			
			self.cameraNode.setScale(1)
			camera.setPos(render, pos)


	
	def addPlanet(self, name, simulation):
		
		objects = simulation['objects']
		
		mass = objects[name]['m']
		pos = objects[name]['p']
		vel = objects[name]['v']
		avel = objects[name]['av']
		temperature = objects[name]['temperature']
		r = objects[name]['r']*scale
		
		model = loader.loadModel('models/planet_sphere')
		model.setTexture(loader.loadTexture(objects[name]['texture']))
		
		model.setScale(r)
		
		shape = BulletSphereShape(r)
		        
		rbnode = BulletRigidBodyNode(name)
		rbnode.addShape(shape)
		rbnode.setMass(mass/self.massScale)
		#rbnode.setRestitution(0.5)
		
		rbnode.setLinearVelocity(Vec3(*vel))
		rbnode.setAngularVelocity(Vec3(*avel))
		
		node = render.attachNewNode(rbnode)
		self.world.attachRigidBody(rbnode)
		
		model.reparentTo(node)
		
		node.setPos(*pos)
		
		trlClr = (random.random(), random.random(), random.random(), 1.0)
		
		body = Body(model, node, rbnode, r, trlClr, temperature)
		
		self.bodies.append(body)
	
	def loadSimulation(self, n) :
		file = open("simulations/{}.sim".format(n), 'r')
		sim = pickle.load(file)
		
	def logSomething(self):
		for o in self.bodies :
			log.info(o.rbnode.getInertia())
	def debugFunction(self):
		for o in self.bodies :
			
			
			o.rbnode.setLinearVelocity(Vec3(0,0,0))
			log.info(o.rbnode.isActive())
			log.info('debug1')
	def debugFunction2(self):
		for o in self.bodies :
			log.info(o.rbnode.getLinearVelocity())
			o.rbnode.setDeactivationTime(10000)
			o.rbnode.setLinearVelocity(Vec3(1,0,0))
			log.info(o.rbnode.getLinearVelocity())
			log.info('debug2')
		

test = Test()
test.run()