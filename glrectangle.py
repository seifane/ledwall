# author: Kaan Eraslan
import math

import OpenGL.GL as gl
import PySide6
from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QColor, Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.buffer = None

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QPoint()

        self.backgroundColor = QColor.fromRgb(0, 0, 0, 255)

    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )

        return info

    def minimumSizeHint(self):
        return QSize(50, 50)

    def maximumSize(self) -> PySide6.QtCore.QSize:
        return QSize(400, 200)

    def sizeHint(self):
        return QSize(400, 200)

    def setBuffer(self, buffer):
        if buffer is None:
            return
        self.buffer = buffer
        # self.object = self.makeObject()
        self.update()
        # self.paintGL()

    def initializeGL(self):
        print(self.getOpenglInfo())

        self.setClearColor(self.backgroundColor)
        self.object = self.makeObject()
        gl.glShadeModel(gl.GL_FLAT)
        # gl.glEnable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -10.0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.object = self.makeObject()
        gl.glCallList(self.object)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                      side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 1, 0, 4.0, 15.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeObject(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        # self.setColorRGBA((0, 0, 0, 255))
        # self.drawRect(
        #     (0.0, 0.0),
        #     (1.0, 0.0),
        #     (1.0, 1.0),
        #     (0.0, 1.0)
        # )

        if self.buffer is not None:
            self.draw_preview()

        gl.glEnd()
        gl.glEndList()

        return genList

    def draw_preview(self):
        squareSize = int(self.height() / 16)
        for x in range(32):
            for y in range(16):
                color = self.buffer[x][y]
                self.setColorRGBA(color)
                pos1 = (self.to_sp((x * squareSize, y * squareSize)))
                pos2 = (self.to_sp((x * squareSize + squareSize, y * squareSize)))
                pos3 = (self.to_sp((x * squareSize + squareSize, y * squareSize + squareSize)))
                pos4 = (self.to_sp((x * squareSize, y * squareSize + squareSize)))
                self.drawRect(pos1, pos2, pos3, pos4)

    def to_sp(self, p: tuple[int, int]) -> tuple[float, float]:
        return (p[0] / 400, p[1] / 200)

    def drawRect(self,
             pos1: tuple[float, float],
             pos2: tuple[float, float],
             pos3: tuple[float, float],
             pos4: tuple[float, float]):
        gl.glVertex3d(pos1[0], pos1[1], 0)
        gl.glVertex3d(pos2[0], pos2[1], 0)
        gl.glVertex3d(pos3[0], pos3[1], 0)
        gl.glVertex3d(pos4[0], pos4[1], 0)

        gl.glVertex3d(pos4[0], pos4[1], 0)
        gl.glVertex3d(pos3[0], pos3[1], 0)
        gl.glVertex3d(pos2[0], pos2[1], 0)
        gl.glVertex3d(pos1[0], pos1[1], 0)

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.setColor(self.trolltechGreen)

        gl.glVertex3d(x1, y1, 0)
        gl.glVertex3d(x2, y2, 0)
        gl.glVertex3d(x3, y3, 0)
        gl.glVertex3d(x4, y4, 0)

        gl.glVertex3d(x4, y4, 0)
        gl.glVertex3d(x3, y3, 0)
        gl.glVertex3d(x2, y2, 0)
        gl.glVertex3d(x1, y1, 0)

    def extrude(self, x1, y1, x2, y2):
        self.setColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        gl.glVertex3d(x1, y1, +0.05)
        gl.glVertex3d(x2, y2, +0.05)
        gl.glVertex3d(x2, y2, -0.05)
        gl.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColorRGBA(self, color: tuple[int, int, int, int]):
        gl.glColor4f(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())
