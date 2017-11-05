import numpy
from panda3d.core import Geom
class Body :
	def __init__ (self, n, m, p = numpy.array([0,0,0]), v = numpy.array([0,0,0]), av = numpy.array([0,0,0])) :
		self.mass = m
		self.node = n
		self.v = v
		self.pos = p
		self.av = av
	
	def setPos (self, p) :
		self.pos = p
		self.node.setPos(p[0],p[1],p[2])
		
	def setTrail(self, ls, gn) : 
		self.lines = ls
		self.gNode = gn
