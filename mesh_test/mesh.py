

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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

# Function to put instructions on the screen.
def addInstructions(pos, msg):
	return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1),
						parent=base.a2dTopLeft, align=TextNode.ALeft,
						pos=(0.08, -pos - 0.04), scale=.05)

# Function to put title on the screen.
def addTitle(text):
	return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1),
						parent=base.a2dBottomRight, align=TextNode.ARight,
						pos=(-1, 1), scale=.08)


class GlowDemo(ShowBase):
	def __init__(self):
		# Initialize the ShowBase class from which we inherit, which will
		# create a window and set up everything we need for rendering into it.
		ShowBase.__init__(self)

		base.disableMouse()
		#base.setBackgroundColor(1, 1, 1)
		camera.setPos(0, -50, 0)
		# Check video card capabilities.
		if not base.win.getGsg().getSupportsBasicShaders():
			addTitle(
				"Glow Filter: Video driver reports that Cg shaders are not supported.")
			return
		
		
		
		# Use class 'CommonFilters' to enable a bloom filter.
		# The brightness of a pixel is measured using a weighted average
		# of R,G,B,A.  We put all the weight on Alpha, meaning that for
		# us, the framebuffer's alpha channel alpha controls bloom.

		self.filters = CommonFilters(base.win, base.cam)
		filterok = self.filters.setBloom(
			blend=(0, 0, 0, 1), desat=-0.5, intensity=3.0, size=1)
		if (filterok == False):
			addTitle(
				"Toon Shader: Video card not powerful enough to do image postprocessing")
			return
		self.glowSize = 1

		
		self.t = 1000
		c = self.getColor()
		
		
		
		
		self.sun1 = Actor()
		self.sun1.loadModel("models/planet_sphere")
		self.sun1.setTexture(loader.loadTexture('textures/sun.jpg'))
		self.sun1.setColorScale((0,0,0,1))
		m = Material()
		m.setEmission(c)
		self.sun1.setMaterial(m)
		self.sun1.setPos(2,0,0)
		self.sun1.reparentTo(render)
		
		self.sun2 = loader.loadModel("models/planet_sphere")
		self.sun2.setTexture(loader.loadTexture('textures/sun.jpg'))
		self.sun2.setColorScale((0,0,0,1))
		m = Material()
		m.setEmission((0,0,1,1))
		self.sun2.setMaterial(m)
		self.sun2.reparentTo(self.sun1)
		self.sun2.setPos(-2,0,0)
		
		camera.reparentTo(self.sun2)
		camera.setY(-50)
		
		self.skybox = loader.loadModel("models/planet_sphere")
		self.skybox.setTexture(loader.loadTexture("textures/sky.jpg"))
		self.skybox.reparentTo(camera)
		self.skybox.setShaderOff()
		self.skybox.setTwoSided(True)
		self.skybox.setBin('background', 1)
		self.skybox.setDepthWrite(0)
		self.skybox.setLightOff()
		self.skybox.setScale(2)
		self.skybox.setCompass()
		m = Material()
		m.setEmission((1,1,1,0))
		self.skybox.setMaterial(m)
		self.isRunning = False

		
		addTitle("My hopes")
		
		self.accept("space", self.toggleGlow)
		self.accept("enter", self.toggleDisplay)
		self.accept("+", self.incTemp)
		self.accept("-", self.decTemp)
		self.accept("escape", sys.exit, [0])
		
		render.setShaderAuto()
		
		self.sun1.setShaderOff()
		self.sun2.setShaderOff()
		
		
		self.taskMgr.doMethodLater(0.05, self.spinTask, 'PhysTask')
	
	def incTemp(self):
		self.t*=1.05
		c = self.getColor()
		
		log.info(self.t)
		log.info(c)
		
		#self.sun1.setColorScale(c)
		self.sun1.getMaterial().setEmission(c)
		
	def decTemp(self):
		self.t/=1.05
		c = self.getColor()
		
		log.info(self.t)
		log.info(c)
		
		#self.sun1.setColorScale(c)
		self.sun1.getMaterial().setEmission(c)
		
		
		   
	def toggleGlow(self):
		self.glowSize = self.glowSize + 1
		if self.glowSize == 4:
			self.glowSize = 0
		self.filters.setBloom(blend=(0, 0, 0, 1), desat=-0.5, intensity=10.0,
							  size=self.glowSize)

	def toggleDisplay(self):
		self.isRunning = not self.isRunning
		if not self.isRunning:
			camera.setPos(0, -50, 0)
			self.tron.stop("running")
			self.tron.pose("running", 0)
			self.interval.loop()
		else:
			camera.setPos(0, -170, 3)
			self.interval.finish()
			self.tron.setHpr(0, 0, 0)
			self.tron.loop("running")
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
	def spinTask(self, task):
		camera.setH(camera, 0)
		return Task.again

demo = GlowDemo()
demo.run()
