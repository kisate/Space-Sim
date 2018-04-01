import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import importPanda
from body import Body
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, Shader
from panda3d.core import PandaNode, NodePath
from panda3d.core import AmbientLight, PointLight, VBase4
from panda3d.core import TextNode, LPoint3
from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.bullet import BulletWorld, BulletSphereShape, BulletRigidBodyNode
from direct.actor.Actor import Actor
from panda3d.core import Material
from pandac.PandaModules import *
from direct.task import Task
import math
import sys
import os

from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'bullet-enable-contact-events true')

t = 30

class Test(ShowBase) :
	def __init__(self):
		
		ShowBase.__init__(self)

		
		self.accept('bullet-contact-added', self.onContactAdded)
		self.accept('bullet-contact-destroyed', self.onContactDestroyed)

		
		
		base.disableMouse()
		
		self.world = BulletWorld()
		
		self.massScale = 1e19
		self.g = 6.67408e-20
		self.g*=self.massScale
		
		self.model = loader.loadModel('models/planet_sphere')
		self.model.setTexture(loader.loadTexture('textures/earth.jpg'))
		
		r = 6371
		self.r = r 
		mass = 5.97e+24
		
		self.model.setScale(r)
		
		shape = BulletSphereShape(r)
		        
		rbnode = BulletRigidBodyNode("Model")
		rbnode.addShape(shape)
		rbnode.setMass(mass/self.massScale)
		rbnode.setDeactivationEnabled(False)
		rbnode.setAngularVelocity((0,0,0.0005))
		#rbnode.setRestitution(0.5)
		
		
		node = render.attachNewNode(rbnode)
		
		node.node().notifyCollisions(True)
		
		self.world.attachRigidBody(rbnode)
		
		self.model.reparentTo(node)
		
		self.body = Body(self.model, node, rbnode, r, (1,1,1,1), 2000)
		
		self.filters = CommonFilters(base.win, base.cam)
		filterok = self.filters.setBloom(
			blend=(0, 0, 0, 1), desat=-0.5, intensity=3.0, size=1)
		
		
		
		
		
		# ts = TextureStage('ts')
		# ts.setMode(TextureStage.MModulate)
		# tex = loader.loadTexture('textures/tex5.png')
		# tex.setWrapU(Texture.WM_clamp)
		# tex.setWrapV(Texture.WM_clamp)
		# self.ts = ts
		# np.setTexture(ts, tex)
		# self.sun1.setTexScale(ts, 2, 2)
	
		# proj = render.attachNewNode(LensNode('proj'))
		# lens = PerspectiveLens()
		# self.counter = 10
		# lens.setFov(self.counter)
		# self.lens = lens
		# proj.node().setLens(lens)
		# #proj.node().showFrustum()
		# #proj.find('frustum').setColor(1, 0, 0, 1)
		# proj.reparentTo(self.sun1)
		# proj.setPos(0, 1, 0)
		
		
		# tex = loader.loadTexture('textures/tex6.png')
		# tex.setWrapU(Texture.WMBorderColor)
		# tex.setWrapV(Texture.WMBorderColor)
		# tex.setBorderColor(VBase4(1, 1, 1, 0))
		# tex2 = loader.loadTexture('textures/tex7.png')
		# tex2.setWrapU(Texture.WMBorderColor)
		# tex2.setWrapV(Texture.WMBorderColor)
		# tex2.setBorderColor(VBase4(1, 1, 1, 0))
		# ts = TextureStage('ts')
		# ts.setSort(1)
		# ts.setMode(TextureStage.MGlow)
		# ts2 = TextureStage('ts')
		# ts2.setSort(1)
		# ts2.setMode(TextureStage.MDecal)
		# self.sun1.projectTexture(ts, tex, proj)
		# self.sun1.projectTexture(ts2, tex2, proj)

		base.disableMouse()
	
		
		
		
		
		
		plight = PointLight('pligth')
		plight.setColor(VBase4( 3, 3, 3, 1))
		plnp = render.attachNewNode(plight)
		plnp.reparentTo(self.model)
		render.setLight(plnp)
		
		#self.sun2.setTexScale(ts2, 2, 1)
        
        
		self.isRunning = False
		
	
		self.accept("escape", sys.exit, [0])
		
		render.setShaderAuto()
		
		# self.base = self.model.attachNewNode('base')
		
		# proj = render.attachNewNode(LensNode('proj'))
		# lens = PerspectiveLens()
		# lens.setFov(10)
		# self.lens = lens
		# proj.node().setLens(lens)
		# #proj.node().showFrustum()
		# #proj.find('frustum').setColor(1, 0, 0, 1)
		# proj.reparentTo(self.base)
		# proj.setPos(0,1,0)
		
		# tex = loader.loadTexture('textures/tex6.png')
		# tex.setWrapU(Texture.WMBorderColor)
		# tex.setWrapV(Texture.WMBorderColor)
		# tex.setBorderColor(VBase4(1, 1, 1, 0))
		
		# tex2 = loader.loadTexture('textures/tex7.png')
		# tex2.setWrapU(Texture.WMBorderColor)
		# tex2.setWrapV(Texture.WMBorderColor)
		# tex2.setBorderColor(VBase4(1, 1, 1, 0))
		
		# ts = TextureStage('ts')
		# ts.setSort(1)
		# ts.setMode(TextureStage.MGlow)
		
		# ts2 = TextureStage('ts2')
		# ts2.setSort(1)
		# ts2.setMode(TextureStage.MDecal)
		
		# self.model.projectTexture(ts, tex, proj)
		# self.model.projectTexture(ts2, tex2, proj)
		
		# self.taskMgr.doMethodLater(0.2, self.spinTask, 'PhysTask')
		
		self.counter = 1
		
		# self.ts = TextureStage('colts{}1'.format(self.counter))
		# #ts.setSort(1)
		# self.ts.setMode(TextureStage.MModulateGlow)
		
		self.bodies = []
		
		
		self.addObjects()
		
		self.taskMgr.add(self.physTask, 'physTask')
		
		
		self.accept('i', self.log)

		
	def onContactAdded(self, node1, node2):
		self.addCollision(NodePath(node2))
		self.world.removeRigidBody(node2)
		NodePath(node2).removeNode()
		
	def onContactDestroyed(self, node1, node2):
		return
	
	def addObjects(self) :
		for i in range(3):
			model = loader.loadModel('models/planet_sphere')
			model.setColorScale(0,0,0,1)
			
			r = 100
			mass = 5.97e+20
			
			model.setScale(r)
			
			shape = BulletSphereShape(r)
					
			rbnode = BulletRigidBodyNode("object{}".format(i))
			rbnode.addShape(shape)
			rbnode.setMass(mass/self.massScale)
			rbnode.setDeactivationEnabled(False)
			#rbnode.setRestitution(0.5)
			
			
			node = render.attachNewNode(rbnode)
			self.world.attachRigidBody(rbnode)
			
			node.setPos(self.r*(3-i), -self.r*5, 0)
			
			body = Body(model, node, rbnode, r, (1,1,1,1), 100)
			
			self.bodies.append(body)
			
			model.reparentTo(node)
		camera.reparentTo(self.bodies[0].model)
		camera.setScale(1)
		camera.setPos(0, -15, 0)
		camera.lookAt(self.model)
		camera.setCompass(render)
	def spinTask(self, task):
		
		#self.base.setP(self.base, 1)
		
		# self.sun1.setH(self.sun1, 0)
		# self.lens.setFov(self.counter)
		# self.counter*=1.01
		# self.sun1.setTexScale(self.ts, self.counter, self.counter)
		# self.sun1.setTexOffset(self.ts, 1 - self.counter, 1 - self.counter)
		# self.counter*=1.005
		return Task.cont
	def getColor(self):
		temp = self.t/100
		r, g, b = 0, 0, 0
		if temp <= 66 :
			r = 255
			g = temp
			g = 99.4708025861 * math.log(g) - 161.1195681661
			if temp <= 19:
				b = 0
			else :
				b = temp - 10
				b = 138.5177312231 * math.log(b) - 305.0447927307
		else :
			r = temp -60
			r = 329.698727446 * r**(-0.1332047592)
			
			g = temp - 60
			g = 288.1221695283 * g**(-0.0755148492 )
			b = 255
		return (r/255.0, g/255.0, b/255.0, 1)
	
	def addCollision(self, obj):
		
		base = self.model.attachNewNode('base')
		base.lookAt(obj)
		
		proj = render.attachNewNode(LensNode('proj'))
		lens = PerspectiveLens()
		lens.setFov(5)
		self.lens = lens
		proj.node().setLens(lens)
		#proj.node().showFrustum()
		#proj.find('frustum').setColor(1, 0, 0, 1)
		proj.reparentTo(base)
		proj.setPos(0,-1,0)
		log.info(proj.getPos(self.model))
		
		tex = loader.loadTexture('textures/tex6.png')
		tex.setWrapU(Texture.WMBorderColor)
		tex.setWrapV(Texture.WMBorderColor)
		tex.setBorderColor(VBase4(1, 1, 1, 0))
		
		tex2 = loader.loadTexture('textures/tex7.png')
		tex2.setWrapU(Texture.WMBorderColor)
		tex2.setWrapV(Texture.WMBorderColor)
		tex2.setBorderColor(VBase4(1, 1, 1, 0))
		
		ts = TextureStage('colts{}1'.format(self.counter))
		#ts.setSort(1)
		ts.setMode(TextureStage.MGlow)
		
		ts2 = TextureStage('colts{}2'.format(self.counter))
		#ts2.setSort(1)
		ts2.setMode(TextureStage.MDecal)
		
		self.counter+=1
		
		#self.model.projectTexture(self.ts, tex, proj)
		self.model.projectTexture(ts2, tex2, proj)
		

		self.taskMgr.add(self.expandingTask, 'Exp{}'.format(self.counter), extraArgs=[proj, 20, ts2])

		
		
	def log(self):
		log.info(self.bodies[0].node.getDistance(self.model))
		
	def expandingTask(self, proj, max, ts) :
	
		lens = proj.node().getLens()
		lens.setFov(lens.getFov()*(1+t/1000))
		if (lens.getFov() >= max) :
			self.model.clearProjectTexture(ts)
			proj.parent.removeNode()
			return Task.done
		return Task.cont
	
	def physTask(self, task):
		for o in self.bodies :			
			imp = self.getImpulse(self.body, o)
			o.rbnode.applyCentralImpulse(imp)
			
		
		self.world.doPhysics(t, 10, t/10)
		return Task.cont
	def getImpulse (self, o2, o1) :
		k = o1.rbnode.getMass()*o2.rbnode.getMass()*self.g
		
		r = o1.node.getPos() - o2.node.getPos()
		
		d = k/(VBase3(r).length())**3
		
		x, y, z = r.getX(), r.getY(), r.getZ()
		
		return Vec3(-x*t*d,-y*t*d,-z*t*d)


test = Test()
test.run()