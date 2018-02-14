import numpy
import math
from panda3d.core import Geom, Vec4, Material
class Body :
	def __init__ (self, node, rbnode, trailColor = (1, 1, 1, 1), temperature = 0):
		self.node = node
		self.rbnode = rbnode
		self.wayPoints = []
		self.trlClr = trailColor
		self.setTemperature(temperature)
	
	def setTemperature(self, t):
		self.temperature = t
		
		if t >= 100 :
			c = self.getColor()
			self.node.setColorScale((0,0,0,1))
			m = Material()
			m.setEmission(c)
			self.node.setMaterial(m)
		else :
			self.node.setColorScale((1,1,1,1))
			self.node.clearMaterial()
			
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
