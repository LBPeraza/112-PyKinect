"""
PyKinectGame.py

implements the PyKinectGame class
a framework for games using Pygame with a Kinect Sensor

(c) Lukas Peraza, 2015
Created for 15-112 at Carnegie Mellon University
Use without permission, with citation
Modify to your liking
"""

import PyKinectRuntime
import PyKinectV2
import pygame
import ctypes, _ctypes

class Struct: pass
class JointPosition(Struct):
	def __init__(self, x, y): self.x, self.y = x, y
	def __getitem__(self, index):
		if index == 0: return self.x
		elif index == 1: return self.y
		else: assert(False)
	def __setitem__(self, index, value):
		if index == 0: self.x = value
		elif index == 1: self.y = value
		else: assert(False)
	def __len__(self): return 2

Joints = Struct()

Joints.head = PyKinectV2.JointType_Head
Joints.neck = PyKinectV2.JointType_Neck
Joints.spineTop = PyKinectV2.JointType_SpineShoulder
Joints.spineMid = PyKinectV2.JointType_SpineMid
Joints.spineLow = PyKinectV2.JointType_SpineBase

Joints.leftShoulder = PyKinectV2.JointType_ShoulderLeft
Joints.rightShoulder = PyKinectV2.JointType_ShoulderRight

Joints.leftWrist = PyKinectV2.JointType_WristLeft
Joints.rightWrist = PyKinectV2.JointType_WristRight

Joints.leftHip = PyKinectV2.JointType_HipLeft
Joints.rightHip = PyKinectV2.JointType_HipRight

Joints.rightElbow = PyKinectV2.JointType_ElbowRight
Joints.leftElbow = PyKinectV2.JointType_ElbowLeft

Joints.leftHand = PyKinectV2.JointType_HandLeft
Joints.rightHand = PyKinectV2.JointType_HandRight

Joints.leftHandTip = PyKinectV2.JointType_HandTipLeft
Joints.rightHandTip = PyKinectV2.JointType_HandTipRight

Joints.leftThumb = PyKinectV2.JointType_ThumbLeft
Joints.rightThumb = PyKinectV2.JointType_ThumbRight

Joints.leftKnee = PyKinectV2.JointType_KneeLeft
Joints.rightKnee = PyKinectV2.JointType_KneeRight

Joints.leftAnkle = PyKinectV2.JointType_AnkleLeft
Joints.rightAnkle = PyKinectV2.JointType_AnkleRight

Joints.leftFoot = PyKinectV2.JointType_FootLeft
Joints.rightFoot = PyKinectV2.JointType_FootRight

COLOR = 0
DEPTH = 1
BODYINDEX = 2
BODY = 3

class PyKinectGame(object):
    def __init__(self, color=False, depth=False, bodyIndex=False, body=False, **kwargs):
        self.width = 800
        self.height = 600
        self.__dict__.update(kwargs)
        flags = 0
        flags |= (color and PyKinectV2.FrameSourceTypes_Color)
        flags |= (depth and PyKinectV2.FrameSourceTypes_Depth)
        flags |= (bodyIndex and PyKinectV2.FrameSourceTypes_BodyIndex)
        flags |= (body and PyKinectV2.FrameSourceTypes_Body)
        if flags == 0:
            raise Exception("Kinect game initialized with no frame readers")
        self.kinect = PyKinectRuntime.PyKinectRuntime(flags)
        self._validFrames = []
        if color: self._validFrames += [COLOR]
        if depth: self._validFrames += [DEPTH]
        if bodyIndex: self._validFrames += [BODYINDEX]
        if body: self._validFrames += [BODY]
        self._validFrameSizes = filter(lambda f: f != BODY, self._validFrames)
        self._frames = dict()
        self._frameSizes = dict()

    def getFrame(self, frameIndex):
        """Get last updated frame from Kinect Sensor

        Called with frame index, which is one of:
        - PyKinectGame.COLOR
        - PyKinectGame.DEPTH
        - PyKinectGame.BODYINDEX
        - PyKinectGame.BODY

        I suggest not using this for getting the body frame - \
        use getActiveBodies instead
        """
        if frameIndex not in self._validFrames:
            raise Exception("invalid frame for getFrame")
        frame = self._frames.get(frameIndex)
        if frameIndex == COLOR and self.kinect.has_new_color_frame():
            frame = self.kinect.get_last_color_frame()
        elif frameIndex == DEPTH and self.kinect.has_new_depth_frame():
            frame = self.kinect.get_last_depth_frame()
        elif frameIndex == BODYINDEX and self.kinect.has_new_body_index_frame():
            frame = self.kinect.get_last_body_index_frame()
        elif frameIndex == BODY and self.kinect.has_new_body_frame():
            frame = self.kinect.get_last_body_frame()

        # if frame is None: raise Exception("could not get frame")
        self._frames[frameIndex] = frame
        return frame

    def frameSize(self, frameIndex):
        """Get the size (width*height) of a pixel frame

        Called with frame index, which is one of:
        - PyKinectGame.COLOR
        - PyKinectGame.DEPTH
        - PyKinectGame.BODYINDEX

        PyKinectGame.BODY will not work - it is not a pixel frame
        """
        if frameIndex not in self._validFrameSizes:
            raise Exception("invalid frame for frameSize")
        size = self._frameSizes.get(frameIndex)
        if size is None:
            if frameIndex == COLOR:
                width = self.kinect.color_frame_desc.Width
                height = self.kinect.color_frame_desc.Height
            elif frameIndex == DEPTH:
                width = self.kinect.depth_frame_desc.Width 
                height = self.kinect.depth_frame_desc.Height
            elif frameIndex == BODYINDEX:
                width = self.kinect.body_index_frame_desc.Width
                height = self.kinect.body_index_frame_desc.Height 
            self._frameSizes[frameIndex] = (width, height)
        else: width, height = size
        return (width, height)

    def frameToSurface(self, frame, targetSurface):
        """Converts a frame to a pygame Surface

        useful for drawing a surface to the screen
        """
        if frame is None: return
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()

    def getActiveBodies(self):
        """Get all tracked bodies

        returns a list of (Body, index) pairs
        """
        bodies = self.getFrame(BODY)
        active = []
        if bodies is not None:
	        for i in xrange(self.kinect.max_body_count):
	            body = bodies.bodies[i]
	            if body.is_tracked:
	                active.append((body, i))
        return active

    def jointIsTracked(self, body, joint):
    	joints = body.joints
    	return True
    	return joints[joint].tracking_state == PyKinectV2.TrackingState_Tracked

    def jointPositions(self, body, screen=True):
        """Get positions of all joints in a body

        @param screen: convert to screen coordinates from 3d world coordinates
        """
        joints = body.joints 
        if screen:
            joints = self.kinect.body_joints_to_color_space(joints)
            fw, fh = self.frameSize(COLOR)
            w, h = self.width, self.height
            joints = map(lambda p:JointPosition(p.x / fw * w, p.y / fh * h), joints)
        return joints

    def onInit(self): pass
    def onStep(self, dt): pass
    def onDraw(self, screen): pass
    def onKey(self, key): pass
    def onKeyUp(self, key): pass
    def onMouse(self, x, y): pass
    def onMouseMotion(self, x, y): pass
    def onMouseDrag(self, x, y): pass

    def run(self):
        self.fps = 30
        self.title = "PyKinectGame"
        self.onInit()
        self.bgColor = (0,0,0)

        pygame.init()
        clock = pygame.time.Clock()

        pygame.display.set_caption(self.title)
        screen = pygame.display.set_mode((self.width, self.height))

        self.running = True
        while self.running:

            dt = clock.tick(self.fps)/1000.0

            screen.fill(self.bgColor)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            self.onStep(dt)

            self.onDraw(screen)
            pygame.display.flip()

        pygame.quit()



# EXAMPLE GAME
if __name__ == "__main__":
	class ExGame(PyKinectGame):
		def __init__(self):
			super(ExGame, self).__init__(color=True, body=True,
				width=500, height=300)

		def onInit(self):
			self.title = "PyKinectGame Example"
			self.colorSurface = pygame.Surface(self.frameSize(COLOR))
			self.bodyColors = [
				(255, 0, 0), (0, 255, 0), (0, 0, 255),
				(255, 255, 0), (255, 0, 255), (0, 255, 255)]

		def onStep(self, dt):
			self.colorFrame = self.getFrame(COLOR)
			self.bodies = self.getActiveBodies()

		def onDraw(self, screen):
			self.frameToSurface(self.colorFrame, self.colorSurface)
			cf = pygame.transform.scale(self.colorSurface, (self.width, self.height))
			screen.blit(cf, (0, 0))
			for body, i in self.bodies:
				self.drawBody(screen, self.jointPositions(body), self.bodyColors[i])

		def drawBone(self, screen, joints, color, joint1, joint2):
			p1 = joints[joint1]
			p2 = joints[joint2]
			pygame.draw.line(screen, color, p1, p2, 8)

		def drawBody(self, screen, joints, color):
			self.drawBone(screen, joints, color, Joints.spineTop, Joints.spineMid)
			self.drawBone(screen, joints, color, Joints.spineMid, Joints.spineLow)
			self.drawBone(screen, joints, color, Joints.leftElbow, Joints.leftWrist)
			self.drawBone(screen, joints, color, Joints.rightElbow, Joints.rightWrist)

	ExGame().run()