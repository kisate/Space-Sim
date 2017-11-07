import numpy
from panda3d.core import Geom
class Body :
	def __init__ (self, n,  pNode, m, p = numpy.array([0,0,0]), v = numpy.array([0,0,0]), av = numpy.array([0,0,0])) :
		self.mass = m
		self.node = n
		self.v = v
		self.av = av
		self.pNode = pNode
		self.setPos(p)
	
	def setPos (self, p) :
		self.pos = p
		self.pNode.setPos(p[0],p[1],p[2])
	def getPos (self) :
		return self.pNode.getPos()
	
	def setTrail(self, ls, gn) : 
		self.lines = ls
		self.gNode = gn
