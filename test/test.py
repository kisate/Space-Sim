from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import LVector3
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomNode, GeomLinestrips
from panda3d.core import Material
from math import pi, sin, cos
from scipy import constants
import numpy
from body import Body
import values
t = 1800
g = constants.value('Newtonian constant of gravitation')/1000**2
tick = 0.010
x = 40
def getforce (o2, o1) :
	k = o1.mass*o2.mass*g
	d = k/numpy.linalg.norm(numpy.subtract(o2.pos, o1.pos))**3
	return numpy.multiply(d, numpy.subtract(o2.pos,o1.pos))

scale = 10000
class Test(ShowBase) :
	def __init__ (self):
		ShowBase.__init__(self)
		b = OnscreenImage(parent=render2d, image="textures/sky.jpg")
		base.cam.node().getDisplayRegion(0).setSort(20)
		self.gNode = GeomNode('gnode')
		n = render.attachNewNode(self.gNode)
		self.bodies = []
		self.loadModels()
		camera.reparentTo(self.bodies[0].node)
		camera.lookAt(self.bodies[0].node)
		base.camLens.setFov(1000000000*100)
		self.setUpLights()
		m = Material()
		m.setEmission((1,1,1,1))
		self.bodies[0].node.setMaterial(m)
		self.taskMgr.doMethodLater(tick, self.physTask, 'PhysTask')
	
	def spinCameraTask(self, task):
		angleDegrees = task.time * 24.0
		self.camera.setHpr(angleDegrees, 0, 0)
		return Task.cont
		
	def physTask(self, task) :
		for o in self.bodies :
			vdata = o.vdata
			vertex = GeomVertexWriter(vdata, 'vertex')
			vertex.setRow(o.row)
			color = GeomVertexWriter(vdata, 'color')
			color.setRow(o.row)
			pos = o.node.getPos()
			vertex.addData3f(pos[0], pos[1], pos[2])
			color.addData4f(1, 0.5, 0.5, 1)
			o.prim.addVertex(o.row)
			vertex.setRow(-1)
			o.setPos(numpy.sum([o.pos, numpy.multiply(t, o.v)], axis = 0), scale)
			print(o.v)
			for o2 in self.bodies :
				if o2 != o :
					f = getforce(o2, o)
					a = numpy.divide(f, o.mass)
					o.v = numpy.sum([o.v, numpy.multiply(t, a)], axis = 0)
		return Task.again
	
	def loadModels(self) : 
		self.addPlanet('sun')
		self.addPlanet('mercury')
		self.bodies[-1].setPos(numpy.array([0,57909227,0]), scale)
		self.bodies[-1].v = numpy.array([50*x, 0 ,0])
		self.addPlanet('venus')
		self.bodies[-1].setPos(numpy.array([0, 108942109, 0]), scale)
		self.bodies[-1].v = numpy.array([35*x, 0 ,0])
		self.addPlanet('earth')
		self.bodies[-1].setPos(numpy.array([0, 150000000, 0]), scale)
		self.bodies[-1].v = numpy.array([30*x, 0 ,0])
		self.addPlanet('mars')
		self.bodies[-1].setPos(numpy.array([0, 2.3e+8, 0]), scale)
		self.bodies[-1].v = numpy.array([24*x, 0 ,0])
		self.addPlanet('jupiter')
		self.bodies[-1].setPos(numpy.array([0, 7.79e+8, 0]), scale)
		self.bodies[-1].v = numpy.array([13*x, 0 ,0])
		self.addPlanet('uranus')
		self.bodies[-1].setPos(numpy.array([0, 2.9e+10, 0]), scale)
		self.bodies[-1].v = numpy.array([6.8*x, 0 ,0])
		self.addPlanet('neptune')
		self.bodies[-1].setPos(numpy.array([0, 4.5e+10, 0]), scale)
		self.bodies[-1].v = numpy.array([5.4*x, 0 ,0])
		
	def setUpLights(self) : 
		plight = PointLight('plight')
		plight.setColor(VBase4(3, 3, 3, 1))
		plnp = render.attachNewNode(plight)
		plnp.setPos(0, 0, 0)
		render.setLight(plnp)

		# Important! Enable the shader generator.
		render.setShaderAuto()

		# default values
		self.cameraSelection = 0
		self.lightSelection = 0
		
	def addPlanet(self, name):
		planet = loader.loadModel('models/sphere')
		planet.setTexture(loader.loadTexture('textures/' + name + '.jpg'))
		r = values.values[name]['r']/scale*300
		planet.setSx(r)
		planet.setSy(r)
		planet.setSz(r)
		body = Body(planet, values.values[name]['m'])
		vdata = GeomVertexData(name, GeomVertexFormat.getV3c4(), Geom.UHDynamic)
		vdata.setNumRows(10000)
		prim = GeomLinestrips(Geom.UHDynamic)
		geom = Geom(vdata)
		geom.addPrimitive(prim)
		body.setGeom(geom, vdata, prim)
		self.gNode.addGeom(geom)
		planet.reparentTo(render)
		self.bodies.append(body)
		
		
test = Test()
test.run()