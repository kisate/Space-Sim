import numpy
import math

import importPanda

from panda3d.core import Geom, Vec4, Material
class Body :
	def __init__ (self, model, node, rbnode, ghost, r, name, trlClr = (1, 1, 1, 1), t = 0, isCooling = False):
		self.model = model
		self.node = node
		self.rbnode = rbnode
		self.ghost = ghost
		self.radius = r
		self.realRadius = r
		self.name = name
		self.isCooling = isCooling

		self.wayPoints = []
		self.collidesWith = []
		self.trlClr = trlClr
		self.setTemperature(t)
		self.dead = False
		
	
	def setTemperature(self, t):
		self.temperature = t
		
		if t >= 500 :
			c = self.getColor()
			m = Material()
			m.setEmission(c)
			self.model.setMaterial(m)
			self.model.setShaderOff()
		else :
			self.model.setColorScale((1,1,1,1))
			self.model.clearMaterial()
			self.model.setShaderAuto()
		
	
	
	
	def getColor(self):
		temp = self.temperature/100
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