import numpy
from panda3d.core import Geom, Vec4
class Body :
	def __init__ (self, n, m, p = numpy.array([0,0,0]), v = numpy.array([0,0,0]), av = numpy.array([0,0,0]), trlClr = (1, 1, 1, 1) ):
		self.mass = m
		self.node = n
		self.v = v
		self.av = av
		self.setPos(p)
		self.wayPoints = []
		self.trlClr = trlClr
	
	def setPos (self, p, move = True) :
		self.pos = p
		if move : self.node.setPos(p[0],p[1],p[2])
	def getPos (self) :
		return self.node.getPos()
	
