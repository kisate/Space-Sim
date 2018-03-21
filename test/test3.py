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
		#self.sun1.setTexture(loader.loadTexture('textures/earth.jpg'))
		# self.sun1.setColorScale((0,0,0,0.9))
		# m = Material()
		# m.setEmission(c)
		#self.sun1.setMaterial(m)
		self.sun1.setPos(0,0,0)
		self.sun1.setScale(1)
		self.sun1.reparentTo(render)
		
		camera.reparentTo(self.sun1)
		camera.setY(-10)
		camera.setCompass(render)
		
		
		
		ts = TextureStage('ts')
		ts.setMode(TextureStage.MModulate)
		tex = loader.loadTexture('textures/tex.png')
		tex.setWrapU(Texture.WM_border_color)
		tex.setWrapV(Texture.WM_border_color)
		tex.setBorderColor(VBase4(0.4, 0.5, 1, 0))
		self.sun1.setTexture(ts, tex)
		self.sun1.setTexScale(ts, 1, 1)
		
		self.isRunning = False
		
	
		self.accept("escape", sys.exit, [0])
		
		render.setShaderAuto()
		
		self.sun1.setShaderAuto()
		
		
		self.taskMgr.doMethodLater(0.05, self.spinTask, 'PhysTask')

	def spinTask(self, task):
		self.sun1.setH(self.sun1, 1)
		return Task.cont



test = Test()
test.run()