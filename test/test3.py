import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import importPanda

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, Shader
from panda3d.core import PandaNode, NodePath
from panda3d.core import AmbientLight, PointLight, VBase4
from panda3d.core import TextNode, LPoint3
from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from panda3d.core import Material
from pandac.PandaModules import *
from direct.task import Task
import math
import sys
import os

	
class Test(ShowBase) :
	def __init__(self):
		
		ShowBase.__init__(self)

		base.disableMouse()
	
		self.sun1 = loader.loadModel("models/planet_sphere")
		self.sun2 = loader.loadModel("models/planet_sphere")
		#self.sun1.setTexture(loader.loadTexture('textures/tex5.png'))
		# self.sun1.setColorScale((0,0,0,0.9))
		# m = Material()
		# m.setEmission(c)
		#self.sun1.setMaterial(m)
		self.sun1.setPos(-1,0,0)
		self.sun2.setPos(1,0,0)
		self.sun1.reparentTo(render)
		self.sun2.reparentTo(render)
		camera.reparentTo(render)
		camera.setPos(0, -10, 0)
		camera.setCompass(render)
		
		
		
		# ts = TextureStage('ts')
		# ts.setMode(TextureStage.MModulate)
		# tex = loader.loadTexture('textures/tex5.png')
		# tex.setWrapU(Texture.WM_clamp)
		# tex.setWrapV(Texture.WM_clamp)
		# self.ts = ts
		np = NodePath(self.sun1)
		# np.setTexture(ts, tex)
		# self.sun1.setTexScale(ts, 2, 2)
	
		proj = render.attachNewNode(LensNode('proj'))
		lens = PerspectiveLens()
		proj.node().setLens(lens)
		proj.node().showFrustum()
		proj.find('frustum').setColor(1, 0, 0, 1)
		proj.reparentTo(self.sun1)
		proj.setPos(0, -2, 0)
		self.sun1.setP(-45)
		
		i = proj.posInterval(5, VBase3(-1, 0, 0))
		#i.loop()
		
		tex = loader.loadTexture('textures/tex6.png')
		tex.setWrapU(Texture.WMBorderColor)
		tex.setWrapV(Texture.WMBorderColor)
		tex.setBorderColor(VBase4(1, 1, 1, 0))
		ts = TextureStage('ts')
		ts.setSort(1)
		ts.setMode(TextureStage.MModulate)
		self.sun1.projectTexture(ts, tex, proj)
		 
		base.disableMouse()
	
		
		self.counter = 1
		
		ts2 = TextureStage('ts2')
		ts2.setMode(TextureStage.MModulate)
		tex2 = loader.loadTexture('textures/tex5.png')
		
		self.sun2.setTexture(ts2, tex2)
		#self.sun2.setTexScale(ts2, 2, 1)
        
        
		self.isRunning = False
		
	
		self.accept("escape", sys.exit, [0])
		
		render.setShaderAuto()
		
		self.sun1.setShaderAuto()
		
		
		self.taskMgr.doMethodLater(0.2, self.spinTask, 'PhysTask')
		
		self.accept('i', self.log)

	def spinTask(self, task):
		self.sun1.setH(self.sun1, 0)
		self.sun2.setH(self.sun2, 0)
		# self.sun1.setTexScale(self.ts, self.counter, self.counter)
		# self.sun1.setTexOffset(self.ts, 1 - self.counter, 1 - self.counter)
		# self.counter*=1.005
		return Task.cont
	
	def log(self):
		log.info(self.counter)


test = Test()
test.run()