import PyKinectV2 as pK2
import PyKinectRuntime as pKr

import ctypes, _ctypes

import pygame
import math

class Game(object):
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.width = 550
        self.height = 400

        self.screen = pygame.display.set_mode((self.width, self.height))

        self.hands = map(lambda f: pygame.image.load("images/"+f).convert(),
                ["hand_open.jpg", "hand_closed.jpg", "hand_point.jpg"])

        self.hands = map(lambda i: pygame.transform.scale(i, (100, 100)), self.hands)

        self.imwidth = self.imheight = 100

        self.hands[0] = pygame.transform.rotate(self.hands[0], 30)

        self.kinect = pKr.PyKinectRuntime(pK2.FrameSourceTypes_Color | pK2.FrameSourceTypes_Body)
        self.frameWidth = self.kinect.color_frame_desc.Width
        self.frameHeight = self.kinect.color_frame_desc.Height
        self.frame_surface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)

    def onInit(self):
        self.playing = True
        self.handX = self.width / 2
        self.handY = self.height / 2
        self.handTheta = 90

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self.kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def run(self):

        self.onInit()
        self.playing = True

        self._bodies = None
        frame = None

        while self.playing:
            time = self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False

            # if self.kinect.has_new_color_frame():
                # frame = self.kinect.get_last_color_frame()
                # self.draw_color_frame(frame, self.frame_surface)
                # frame = None

            if self.kinect.has_new_body_frame(): 
                self._bodies = self.kinect.get_last_body_frame()

            self.screen.fill((255, 255, 255))


            # surf_to_draw = pygame.transform.scale(self.frame_surface, (self.width, self.height))
            # self.screen.blit(surf_to_draw, (0, 0))

            if self._bodies is not None:
                for i in xrange(0, self.kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue

                    self.draw_hand(body.joints, body.hand_right_state)

            pygame.display.flip()

        pygame.quit()

    def jointToScreen(self, jointPoints, joint):
        location = jointPoints[joint]
        x = int(location.x / self.frameWidth * self.width)
        y = int(location.y / self.frameHeight * self.height)
        return x, y

    def draw_hand(self, joints, openness):
        jointPoints = self.kinect.body_joints_to_color_space(joints)

        wrist = self.jointToScreen(jointPoints, pK2.JointType_WristRight)
        tip = self.jointToScreen(jointPoints, pK2.JointType_HandTipRight)

        angle = math.degrees(math.atan2(tip[1] - wrist[1], tip[0] - wrist[0]))

        if openness == pK2.HandState_Closed:
        	h = 1
        elif openness == pK2.HandState_Lasso:
        	h = 2
        else:
        	h = 0

        handim = pygame.transform.rotate(self.hands[h], 270 - angle)
        width, height = handim.get_size()

        self.screen.blit(handim, (wrist[0] - width/2, wrist[1] - height/2))

Game().run()