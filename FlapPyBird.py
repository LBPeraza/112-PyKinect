from PyKinectGame import *
import random

PIPEGAP = 180
PIPEWIDTH = 100

class Pipe(object):
	def __init__(self, width, height):
		self.x = width 
		self.y = random.randint(PIPEGAP / 2, height - PIPEGAP / 2)
		self.speed = 100

	def pointIsSafe(self, x, y):
		if self.x - PIPEWIDTH/2 <= x <= self.x + PIPEWIDTH/2:
			return self.y - PIPEGAP/2 <= y <= self.y + PIPEGAP/2
		return True

	def draw(self, screen):
		pygame.draw.rect(screen, (0, 255, 0), (self.x - PIPEWIDTH/2, 0, PIPEWIDTH, self.y - PIPEGAP/2))
		pygame.draw.rect(screen, (0, 255, 0), (self.x - PIPEWIDTH/2, self.y + PIPEGAP/2, PIPEWIDTH, 1000))

	def update(self, dt):
		self.x -= self.speed * dt

class FlapPyKinect(PyKinectGame): #lol

	def __init__(self, width, height):
		super(FlapPyKinect, self).__init__(color=True, body=True, width=width, height=height)

	def onInit(self):
		self.birdHeight = self.height / 2
		self.prevRightHandHeight = None
		self.prevLeftHandHeight = None
		self.pipes = []
		self.timeSinceLastPipe = 0.0
		self.timePerPipe = 3.0

	def flap(self, body, dt):
		jointPositions = self.jointPositions(body)

		if not(self.jointIsTracked(body, Joints.rightHand) and
			   self.jointIsTracked(body, Joints.leftHand)): return

		rhY = jointPositions[Joints.rightHand].y
		lhY = jointPositions[Joints.leftHand].y

		yd = 0
		if self.prevRightHandHeight != None:
			rightHandFlap = max(0, rhY - self.prevRightHandHeight)
			leftHandFlap = max(0, lhY - self.prevLeftHandHeight)
			yd = dt * 40 * min(rightHandFlap, leftHandFlap)
			self.birdHeight -= yd
			self.birdHeight = min(self.height, max(self.birdHeight, 0))
		self.prevRightHandHeight = rhY
		self.prevLeftHandHeight = lhY
		return yd

	def onStep(self, dt):
		self.timeSinceLastPipe += dt
		self.bgColor = (0, 0, 0)
		for pipe in self.pipes:
			pipe.update(dt)
			if not pipe.pointIsSafe(self.width/3, self.birdHeight):
				self.bgColor = (255, 0, 0)

		if self.timeSinceLastPipe >= self.timePerPipe:
			self.timeSinceLastPipe = 0.0
			self.pipes.append(Pipe(self.width, self.height))

		bodies = self.getActiveBodies()
		movedown = True
		if len(bodies) > 0:
			if self.flap(bodies[0][0], dt) != 0:
				movedown = False
		if movedown:
			self.birdHeight += 7
			self.birdHeight = min(self.height, self.birdHeight)


	def onDraw(self, screen):
		for pipe in self.pipes: pipe.draw(screen)
		pygame.draw.circle(screen, (0, 0, 255), map(int,(self.width/3, self.birdHeight)), 30)


FlapPyKinect(800, 600).run()