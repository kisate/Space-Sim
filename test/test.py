import argparse
import logging
import pickle
import random
import sys
from math import copysign, cos, pi, sin

import numpy

import importPanda
import simulations
from body import Body
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.interval.LerpInterval import LerpPosInterval
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape, BulletWorld, BulletGhostNode
from panda3d.core import *
from panda3d.core import (AmbientLight, DirectionalLight, Geom, GeomLinestrips,
                          GeomNode, GeomVertexData, GeomVertexFormat,
                          LightAttrib, LVector3, Material, MouseButton,
                          WindowProperties)
from pandac.PandaModules import loadPrcFileData

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)








loadPrcFileData('', 'bullet-enable-contact-events true')
loadPrcFileData('', 'bullet-filter-algorithm groups-mask')

t = 10000
G = 6.67408e-20

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
	
	
class Test(ShowBase) :
	def __init__ (self):
		log.info('Loading started')
		log.info('Initiallizing engine')
		ShowBase.__init__(self)
		
		self.accept('bullet-contact-added', self.onContactAdded)
		self.accept('bullet-contact-destroyed', self.onContactDestroyed)
		
		self.gNode = GeomNode('gnode')
		n = render.attachNewNode(self.gNode)
		self.bodies = []
		self.pullers = []
		
		
		self.massScale = 1e25
		self.minMass = 1e10
		
		global G
		G*=self.massScale
		
		
		
		self.loadModels(simulations.simulations[simulation])
		
		log.info("Counting {} waypoints".format(geoms))
		
		self.counter = 0
		
		for i in range(igeoms):
			for o in self.bodies :			
				for o2 in self.pullers :
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

		self.counters = {"Expanding" : 0, "Growing" : 0, "Absorbing" : 0, "Misc" : 0}
		
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

		
		self.cameraNode.reparentTo(self.bodies[0].node)
		self.cameraNode.setScale(self.bodies[0].radius)
		self.cameraNode.lookAt(self.bodies[0].node)
		
		camera.setY(-5)
		
		self.cameraNode.setP(-90)
		self.rotateY = -90
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

		vel = o.rbnode.getAngularVelocity()

		Ex = 0.2*mass*self.massScale*o.radius**2*abs(vel[0])**2
		Ey = 0.2*mass*self.massScale*o.radius**2*abs(vel[1])**2
		Ez = 0.2*mass*self.massScale*o.radius**2*abs(vel[2])**2

		Er = Ex + Ey + Ez
		return El + Er

	def physTask(self, task) :
	
		for o in self.bodies :			
			for o2 in self.pullers :
				if o2 != o :
					imp = getImpulse(o2, o)
					o.rbnode.applyCentralImpulse(imp)

			self.processTemperature(o)
			
		#self.bodies[0].setTemperature(self.bodies[0].temperature*1.005)
		
		
		self.world.doPhysics(t, 10, t/10)
		
		for o in self.bodies : 
			wps = o.wayPoints
            
			wps.append(o.node.getPos())
			
			if(len(wps) > geoms) : wps.pop(0)
		
		self.draw()
		
		return Task.cont
	
	def processTemperature(self, body):

		if body.temperature < body.shiningTemp : 
			body.isCooling = False
			
			if body.isShining : 
				body.isShining = False
				render.clearLight(NodePath(body.light))
				self.lights.remove(body.light)

		elif not body.isShining : 
			body.isShining = True
			render.setLight(NodePath(body.light))
			self.lights.append(body.light)
		
		if body.isCooling : body.setTemperature(body.temperature*(1-0.001*t))

		if len(self.lights) == 0 and not self.hasFarLight : self.addFarLight()
		if len(self.lights) > 0 and self.hasFarLight : self.removeFarLight()
		
	def addFarLight(self) :
		self.farLight = PointLight('far_light')
		self.farLight.setColor(VBase4( 3, 3, 3, 1))
		lnp = render.attachNewNode(self.farLight)
		lnp.setPos(1e5, 0, 0)
		render.setLight(NodePath(self.farLight))
		self.hasFarLight = True

	def removeFarLight(self) : 
		render.clearLight(NodePath(self.farLight))
		self.hasFarLight = False
	
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
			t*=self.accFactor
			self.accFactor*=1.001
			self.speedText.setText('{0} seconds per tick [+/-]'.format(round(t, 2)))
		
		if self.keys['incSpeed'] == 0 :
			self.accFactor = 1.01
		
		if self.keys['decSpeed'] == 1:
			t/=self.decFactor
			self.decFactor*=1.001
			self.speedText.setText('{0} seconds per tick [+/-]'.format(round(t, 2)))
			
		if self.keys['decSpeed'] == 0 :
			self.decFactor = 1.01

		return Task.cont
	
	def loadModels(self, simulation) : 
	
		self.world = BulletWorld()
		self.world.setGroupCollisionFlag(0, 0, True)
		self.world.setGroupCollisionFlag(0, 1, False)
		
		self.world.setGroupCollisionFlag(1, 1, False)
		
		self.lights = []
		
		for x in simulation['objects'].keys() :
			self.addPlanet(x, simulation)		
		global t 
		t = simulation['time']
		log.info("Loaded models")
		
	def setUpLights(self) : 
		
		self.hasFarLight = False

		if len(self.lights) == 0 :
			self.addFarLight()

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

		self.attachCamera(self.bodies[self.curPlanet])

	
	def attachCamera(self, body) :

		if self.detached : 
		
			self.detached = False
			
			self.cameraNode.wrtReparentTo(render)
			camera.wrtReparentTo(self.cameraNode)
			
			hpr = camera.getHpr()
			
			camera.setHpr(0,0,0)
			
			self.cameraNode.wrtReparentTo(body.node)
			self.cameraNode.setHpr(hpr)
			
			self.rotateX = self.cameraNode.getH()
			self.rotateY = self.cameraNode.getP()
			
			
			self.cameraNode.setScale(body.radius)
			self.cameraNode.setPos(0,0,0)
		
			self.cameraNode.setScale(body.radius)
		
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
			self.attachCamera(self.bodies[self.curPlanet])

			
	def prevPlanet(self) :
		if self.curPlanet > 0 :
			self.curPlanet -= 1
			self.detachCamera()
			self.attachCamera(self.bodies[self.curPlanet])
			
	def setUpMouse(self) :

		self.disableMouse()

		self.mouseMagnitude = 3

		self.rotateX, self.rotateY, self.rotateXd, self.rotateYd = 0, 0, 0, 0

		self.lastMouseX, self.lastMouseY = None, None

		self.taskMgr.add(self.mouseTask, "Mouse Task")
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

		self.cameraNode.setScale(b.model.getScale()[0])
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
			
			
			self.cameraNode.setScale(b.model.getScale()[0])
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
		        
		rbnode = BulletRigidBodyNode(name + 'rbn')
		rbnode.setMass(mass/self.massScale)
		#rbnode.setRestitution(0.5)
		ghost = BulletGhostNode(name + 'gn')
		ghost.addShape(shape)
		
		if vel == [0,0,0] :
			rbnode.setDeactivationEnabled(False)
		
		rbnode.setLinearVelocity(Vec3(*vel))
		rbnode.setAngularVelocity(Vec3(*avel))
		

		
		node = render.attachNewNode(rbnode)
		ghostNP = NodePath(ghost)
		ghostNP.reparentTo(node)
		self.world.attachRigidBody(rbnode)
		self.world.attachGhost(ghost)
		ghostNP.setCollideMask(BitMask32.bit(0))
		model.reparentTo(node)
		
		node.setPos(*pos)
		NodePath(ghost).node().notifyCollisions(True)
		
		trlClr = (random.random(), random.random(), random.random(), 1.0)

		isCooling = False

		if temperature > 7000 : isCooling = True
 		

		body = Body(model, node, rbnode, ghost, r, name, trlClr, temperature, isCooling=isCooling)


		light = PointLight('light_' + name)
		light.setColor(VBase4( 3, 3, 3, 1))
		lnp = render.attachNewNode(light)
		lnp.reparentTo(node)
		
		body.light = light

		if temperature >= body.shiningTemp : 

			body.isShining = True
			
			render.setLight(lnp)
			self.lights.append(light)

		
		if mass >= self.minMass :
			self.pullers.append(body)
		self.bodies.append(body)
	
	def loadSimulation(self, n) :
		file = open("simulations/{}.sim".format(n), 'r')
		sim = pickle.load(file)
		
	def logSomething(self):
		for o in self.bodies :
			log.info(o.rbnode.getInertia())

	def debugFunction(self):		
		log.info('debug1')

	def debugFunction2(self):

		s = Vec3(0,0,0)

		for o in self.bodies :
			#log.info(o.rbnode.getAngularVelocity())
			s += o.rbnode.getLinearVelocity()*o.rbnode.getMass()
		
		log.info(s)
			
	def onContactAdded(self, node1, node2):

		parent1 = NodePath(node1).parent
		parent2 = NodePath(node2).parent
		
		body1 = next(x for x in self.bodies if x.name == node1.getName()[:-2])
		body2 = next(x for x in self.bodies if x.name == node2.getName()[:-2])

		rbnode1 = parent1.node()
		rbnode2 = parent2.node()
		
		if rbnode1.getMass() > rbnode2.getMass() : 
			rbnode2.setLinearFactor(Vec3(1, 1, 1))
			rbnode2.setLinearVelocity(parent2.node().getLinearVelocity()*0)
			mass = (rbnode1.getMass() - rbnode2.getMass()*0.001)
			density = rbnode1.getMass()/body1.radius
			body1.realRadius = mass/density
			step = 0.001

			#parent2.reparentTo(parent1)

			self.world.removeGhost(node2)

			body2.dead = True

			self.taskMgr.add(self.growingTask, 'Grow{}'.format(self.counters["Growing"]), extraArgs=[body1, step], appendTask = True)
			self.counters["Growing"] += 1
			
		#log.debug(NodePath(node1).getCollideMask())
		
		#NodePath(node1).setCollideMask(BitMask32.bit(1))
		#NodePath(node2).setCollideMask(BitMask32.bit(2))
		#deltaMass = (node1.getMass()+node2.getMass())*1e-6
		#node1.setMass(node1.getMass() - deltaMass*0.5)
		#node2.setMass(node2.getMass() - deltaMass*0.5)

		

		#self.world.removeRigidBody(paren1.find('**/rbnode/**').node())
		#NodePath(node2).removeNode()

		#body = next(x for x in self.bodies if x.name == node2.getName[:-3]())

		#self.bodies.remove(body)
		#if body in self.pullers : self.pullers.remove(body)

		#log.info(body)

		if (node2 not in body1.collidesWith) : self.addCollision(NodePath(node1).parent, NodePath(node2).parent)
		
		body1.collidesWith.append(node2)
	
	def growingTask(self, body, step, task) :
	
		scale = body.radius
		
		new = min(scale*(1 + step*t), body.realRadius) if body.realRadius >= body.radius else max(scale*(1 - step*t), body.realRadius)

		body.radius = new
		body.model.setScale(new)
		body.ghost.removeShape(body.ghost.getShape(0))
		body.ghost.addShape(BulletSphereShape(new))
		if NodePath(body.rbnode) == self.cameraNode.parent : self.cameraNode.setScale(new)

		if (new == body.realRadius) :
			return Task.done
		return Task.cont
	
	def onContactDestroyed(self, node1, node2):
		
		body1 = next(x for x in self.bodies if x.name == node1.getName()[:-2])
		body2 = next(x for x in self.bodies if x.name == node2.getName()[:-2])
		
		body1.collidesWith.remove(node2)

		if body2.dead : 
			self.world.removeRigidBody(body2.rbnode)
			#self.world.removeGhost(body2.ghost)
			NodePath(body2.rbnode).wrtReparentTo(body1.node)
			body2.rbnode.setLinearFactor(Vec3(0,0,0))
			body2.rbnode.setLinearVelocity(Vec3(0,0,0))
			self.bodies.remove(body2)
			if body2 in self.pullers : self.pullers.remove(body2)
				
			self.taskMgr.add(self.absorbingTask, 'Abs{}'.format(self.counters["Absorbing"]), extraArgs=[body2, body1])
			self.counters["Absorbing"] += 1

		return		
	
	def absorbingTask(self, obj, absorber) :
		#TODO:reparent not model but rbnode
		
		if (obj.node.getDistance(absorber.node) < absorber.realRadius - obj.realRadius) :
			
			#log.debug("{} {}".format(obj.node.getDistance(absorber.node), absorber.realRadius - obj.realRadius))
			obj.node.removeNode()
			return Task.done

		obj.node.setPos(obj.node.getPos()*0.999)
		return Task.cont

	def addCollision(self, node1, node2):
		
		log.debug(node1.getName())
		
		model = node1.find("**/planet_sphere.egg")

		base = model.attachNewNode('base')
		base.lookAt(node2)
		
		proj = render.attachNewNode(LensNode('proj'))
		lens = PerspectiveLens()
		lens.setFov(5)
		self.lens = lens
		proj.node().setLens(lens)
		#proj.node().showFrustum()
		#proj.find('frustum').setColor(1, 0, 0, 1)
		proj.reparentTo(base)
		proj.setPos(0,-1,0)
		
		# tex = loader.loadTexture('textures/tex6.png')
		# tex.setWrapU(Texture.WMBorderColor)
		# tex.setWrapV(Texture.WMBorderColor)
		# tex.setBorderColor(VBase4(1, 1, 1, 0))
		
		tex2 = loader.loadTexture('textures/tex7.png')
		tex2.setWrapU(Texture.WMBorderColor)
		tex2.setWrapV(Texture.WMBorderColor)
		tex2.setBorderColor(VBase4(1, 1, 1, 0))
		
		# ts = TextureStage('colts{}1'.format(self.counter))
		# #ts.setSort(1)
		# ts.setMode(TextureStage.MGlow)
		
		
		ts = TextureStage('ts_{}'.format(self.counters["Expanding"]))
		ts.setSort(1)
		ts.setMode(TextureStage.MDecal)
		
		
		log.debug('projected')
		
		#self.model.projectTexture(self.ts, tex, proj)
		model.projectTexture(ts, tex2, proj)

		self.taskMgr.add(self.expandingTask, 'Exp{}'.format(self.counters["Expanding"]), extraArgs=[proj, 40, ts, model], appendTask = True)

		self.counters["Expanding"]+=1
	
	
	#def 

	def expandingTask(self, proj, max, ts, node, task) :
	
		lens = proj.node().getLens()
		lens.setFov(lens.getFov() * (1+t/2000))
		if (lens.getFov() >= max) :
			node.clearProjectTexture(ts)
			proj.parent.removeNode()
			return Task.done
		return Task.cont
		

test = Test()
test.run()
