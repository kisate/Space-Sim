import importPanda
import test
from direct.task import Task
from panda3d.core import WindowProperties

class Controller() : 
    def __init__(self, sim) :

        self.sim = sim

        self.keys = {'zoomIn' : 0, 'zoomOut' : 0, 'fwd' : 0, 'bwd' : 0, 'lft' : 0, 'rt' : 0, 'incSpeed' : 0, 'decSpeed' : 0}
		self.accept("escape", sys.exit)
		self.accept("z", self.incScale)
		self.accept("x", self.decScale)
		self.accept('r', self.resetCamera)
		self.accept('y', self.detachCamera)
		self.accept('i', self.logCamera)
		self.accept('u', self.logSomething)
		self.accept('1', self.debugFunction)
		self.accept('2', self.debugFunction2)

		self.accept('arrow_up', self.setKey, ['zoomIn', 1])
		self.accept('arrow_up-up', self.setKey, ['zoomIn', 0])
		self.accept('arrow_down', self.setKey, ['zoomOut', 1])
		self.accept('arrow_down-up', self.setKey, ['zoomOut', 0])
		
		self.accept("+", self.setKey, ['incSpeed', 1])
		self.accept("+-up", self.setKey, ['incSpeed', 0])
		self.accept("-", self.setKey, ['decSpeed', 1])
		self.accept("--up", self.setKey, ['decSpeed', 0])

		
		self.accept('w', self.setKey, ['fwd', 1])
		self.accept('w-up', self.setKey, ['fwd', 0])
		self.accept('s', self.setKey, ['bwd', 1])
		self.accept('s-up', self.setKey, ['bwd', 0])
		self.accept('d', self.setKey, ['rt', 1])
		self.accept('d-up', self.setKey, ['rt', 0])
		self.accept('a', self.setKey, ['lft', 1])
		self.accept('a-up', self.setKey, ['lft', 0])
		self.accept('o', self.sim.prevPlanet)
		self.accept('p', self.sim.nextPlanet)
		
		self.accFactor = 1.01
		self.decFactor = 1.01
		
		self.fwdStep = 0.1
		self.bwdStep = 0.1
		self.lftStep = 0.1
		self.rtStep = 0.1
		
        self.scale = 1
		self.factor = 3

		self.zoomSpeed = 0.03
		self.setUpMouse()

    def setUpMouse(self) :

		self.disableMouse()

		self.mouseMagnitude = 3

		self.rotateX, self.rotateY, self.rotateXd, self.rotateYd = 0, 0, 0, 0

		self.lastMouseX, self.lastMouseY = None, None

		self.sim.taskMgr.add(self.mouseTask, "Mouse Task")
		self.scrolling = False
		self.detached = False

    def incScale(self) : 
		self.scale*= self.factor
		self.sim.scaleText.setText('scale : {0} [Z/X]'.format(scale))
		
		pos = self.sim.camera.getPos(self.sim.render)
		
		for b in self.sim.bodies :
			b.model.setScale(b.model.getScale()[0]*factor)

		self.sim.cameraNode.setScale(b.model.getScale()[0])
		self.sim.camera.setPos(self.sim.render, pos)

		
		
	def decScale(self) : 
		if self.scale >= self.factor :
			self.scale//= self.factor
		
			pos = self.sim.camera.getPos(self.sim.render)
			for b in self.sim.bodies :
				b.model.setScale(b.model.getScale()[0]//factor)
			self.sim.scaleText.setText('scale : {0} [Z/X]'.format(scale))
			
			
			self.sim.cameraNode.setScale(b.model.getScale()[0])
			self.sim.camera.setPos(self.sim.render, pos)

    def mouseTask (self, task):
		mw = self.sim.base.mouseWatcherNode
		wp = WindowProperties()

		hasMouse = mw.hasMouse() 
		if hasMouse and mw.is_button_down(MouseButton.one()):
			x, y = mw.getMouseX(), mw.getMouseY()
			
			if not self.scrolling :
					self.lastMouseX, self.lastMouseY = x, y
					self.scrolling = True
			
			if self.lastMouseX is not None:
				
				dx, dy = x - self.lastMouseX, y - self.lastMouseY

			else:
				dx, dy = 0, 0

			self.lastMouseX, self.lastMouseY = x, y
			
		else:
			x, y, dx, dy, self.lastMouseX, self.lastMouseY = 0, 0, 0, 0, 0, 0
			self.scrolling = False
		
		if self.detached and self.scrolling :
			self.rotateX += dx * 10 * self.mouseMagnitude
			self.rotateY -= dy * 10 * self.mouseMagnitude

			self.camera.setH(self.rotateX)
			self.camera.setP(self.rotateY)
		elif not self.detached and self.scrolling :
			self.rotateX += dx * 10 * self.mouseMagnitude
			self.rotateY -= dy * 10 * self.mouseMagnitude

			self.sim.cameraNode.setH(self.rotateX)
			self.sim.cameraNode.setP(self.rotateY)
		return Task.cont

    def controllTask(self, task) :
	
		d = self.sim.camera.getDistance(self.sim.cameraNode.parent)
		
		if self.keys['zoomIn'] :
			self.sim.camera.setY(min(self.sim.camera.getY()*(1-self.zoomSpeed), -1.1))
		if self.keys['zoomOut']:
			
			self.sim.camera.setY(self.sim.camera.getY()*(1+self.zoomSpeed))
		parent = self.sim.cameraNode.getParent()
		
		if self.keys['fwd'] == 1:
		
			self.detachCamera()
			self.sim.camera.setY(camera, self.fwdStep)
			
			self.fwdStep *= 1.01
		
		else : self.fwdStep = 0.1
		
		if self.keys['bwd'] == 1:
		
			self.detachCamera()
			self.sim.camera.setY(camera, -self.bwdStep)
			
			self.bwdStep *= 1.01
		
		else : self.bwdStep = 0.1
			
		if self.keys['lft'] == 1:
		
			self.detachCamera()
			self.sim.camera.setX(camera, -self.lftStep)
			self.lftStep *= 1.01
		
		else : self.lftStep = 0.1
			
		if self.keys['rt'] == 1:
		
			self.detachCamera()
			self.sim.camera.setX(camera, self.rtStep)
			self.rtStep *= 1.01
		
		else : self.rtStep = 0.1
		
		if self.keys['lft'] == 1:
		
			self.detachCamera()
			self.sim.camera.setX(camera, -self.lftStep)
			self.lftStep *= 1.01
		
		else : self.lftStep = 0.1
		
		t = 		
		
		if self.keys['incSpeed'] == 1:
			t*=self.accFactor
			self.accFactor*=1.001
			self.sim.speedText.setText('{0} seconds per tick [+/-]'.format(round(t, 2)))
		
		if self.keys['incSpeed'] == 0 :
			self.accFactor = 1.01
		
		if self.keys['decSpeed'] == 1:
			t/=self.decFactor
			self.decFactor*=1.001
			self.sim.speedText.setText('{0} seconds per tick [+/-]'.format(round(t, 2)))
			
		if self.keys['decSpeed'] == 0 :
			self.decFactor = 1.01

		return Task.cont

    def resetCamera(self) :

		self.attachCamera(self.sim.bodies[self.curPlanet])

	
	def attachCamera(self, body) :

		if self.detached : 
		
			self.detached = False
			
			self.sim.cameraNode.wrtReparentTo(render)
			self.sim.camera.wrtReparentTo(self.sim.cameraNode)
			
			hpr = self.sim.camera.getHpr()
			
			self.sim.camera.setHpr(0,0,0)
			
			self.sim.cameraNode.wrtReparentTo(body.node)
			self.sim.cameraNode.setHpr(hpr)
			
			self.rotateX = self.sim.cameraNode.getH()
			self.rotateY = self.sim.cameraNode.getP()
			
			
			self.sim.cameraNode.setScale(body.radius)
			self.sim.cameraNode.setPos(0,0,0)
		
			self.sim.cameraNode.setScale(body.radius)
		
	def logCamera(self):
		log.info('camera')
		log.info(self.sim.camera.getPos())
		log.info(self.sim.camera.getHpr())
		log.info('node')
		log.info(self.sim.cameraNode.getPos(render))
		log.info(self.sim.cameraNode.getHpr())
		log.info('skybox')
		log.info(self.skybox.getPos())
		log.info(self.skybox.getHpr())

		
	def nextPlanet(self) :
		if self.curPlanet < len(self.bodies) - 1 :
			self.curPlanet += 1
			self.detachCamera()
			self.attachCamera(self.bodies[self.curPlanet])

			
	def prevPlanet(self) :
		if self.curPlanet > 0 :
			self.curPlanet -= 1
			self.detachCamera()
			self.attachCamera(self.bodies[self.curPlanet])
			
	def setUpMouse(self) :

		self.disableMouse()

		self.mouseMagnitude = 3

		self.rotateX, self.rotateY, self.rotateXd, self.rotateYd = 0, 0, 0, 0

		self.lastMouseX, self.lastMouseY = None, None

		self.taskMgr.add(self.mouseTask, "Mouse Task")
		self.scrolling = False
		self.detached = False
	
	def detachCamera(self):
		if not self.detached : 
			self.detached = True
			self.sim.self.sim.camera.wrtReparentTo(render)
			self.sim.cameraNode.wrtReparentTo(camera)
    