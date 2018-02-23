import numpy
import math
from panda3d.core import Geom, Vec4, Material
class Body :
	def __init__ (self, n, m, p = numpy.array([0,0,0]), v = numpy.array([0,0,0]), av = numpy.array([0,0,0]), trlClr = (1, 1, 1, 1), t = 0):
		self.mass = m
		self.node = n
		self.v = v
		self.av = av
		self.setPos(p)
		self.wayPoints = []
		self.trlClr = trlClr
		self.setTemperature(t)
	
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
		
	def setPos (self, p, move = True) :
		self.pos = p
		if move : self.node.setPos(p[0],p[1],p[2])
	def getPos (self) :
		return self.node.getPos()
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