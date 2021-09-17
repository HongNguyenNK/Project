from PyQt5 import QtWidgets, uic, QtGui
import sys, os, math
import numpy as np


dir_path = os.path.dirname(os.path.realpath(__file__))
UIfile = my_file = os.path.join(dir_path, 'reflect_refract.ui')


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        #self.setWindowTitle("aaaaaa")
        self.ui = uic.loadUi(UIfile, self)
        self.label = self.ui.gui
        self.length = 378 # in pixel which is converted from 10 cm as requirements
        self.thick = 76 # ~ 2.1 cm 
        self.index = 65
        self.rect_plate = [[400, 400]]
        self.coor_beam = [300,150]
        self.angle_of_beam = 45
        self.angle_of_palte = 0
        self.show()
        self.ui.btn_simulate.clicked.connect(self.simulate)

    #draw plate
    def plate(self,degree=0):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(7)
        pen.setColor(QtGui.QColor('darkGray'))
        painter.setPen(pen)
        rad = math.radians(90 - degree)

        painter.setFont(QtGui.QFont("Arial", 14));
        painter.drawText(self.rect_plate[0][0], self.rect_plate[0][1] + 105, "Plate  x: {} y: {}".format(self.rect_plate[0][0],self.rect_plate[0][1]))
        painter.drawLine(self.rect_plate[0][0], self.rect_plate[0][1], self.rect_plate[0][0] + self.length*math.sin(rad),self.rect_plate[0][1] + self.length*math.cos(rad))
        if len(self.rect_plate) > 1:
            self.rect_plate[1] = [self.rect_plate[0][0] + self.length*math.sin(rad), self.rect_plate[0][1] + self.length*math.cos(rad)]
        else:
            self.rect_plate.append([self.rect_plate[0][0] + self.length*math.sin(rad), self.rect_plate[0][1] + self.length*math.cos(rad)])
        rad = rad - math.pi/2
        painter.drawLine(self.rect_plate[1][0], self.rect_plate[1][1], self.rect_plate[1][0] + self.thick*math.sin(rad),self.rect_plate[1][1] + self.thick*math.cos(rad))
        if len(self.rect_plate) > 2:
            self.rect_plate[2] = [self.rect_plate[1][0] + self.thick*math.sin(rad),self.rect_plate[1][1] + self.thick*math.cos(rad)]
        else:
            self.rect_plate.append([self.rect_plate[1][0] + self.thick*math.sin(rad),self.rect_plate[1][1] + self.thick*math.cos(rad)])
        rad = rad - math.pi/2

        painter.drawLine(self.rect_plate[2][0], self.rect_plate[2][1], self.rect_plate[2][0] + self.length*math.sin(rad),self.rect_plate[2][1] + self.length*math.cos(rad))
        if len(self.rect_plate) > 3:
            self.rect_plate[3] = [self.rect_plate[2][0] + self.length*math.sin(rad),self.rect_plate[2][1] + self.length*math.cos(rad)]
        else:
            self.rect_plate.append([self.rect_plate[2][0] + self.length*math.sin(rad),self.rect_plate[2][1] + self.length*math.cos(rad)])
        rad = rad - math.pi/2

        painter.drawLine(self.rect_plate[3][0], self.rect_plate[3][1], self.rect_plate[3][0] + self.thick*math.sin(rad),self.rect_plate[3][1] + self.thick*math.cos(rad))

        painter.end()
        self.label.repaint()

    # draw beam
    def beam(self, X, Y):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(20)
        #pen.setColor(QtGui.QColor('blue'))
        pen.setColor(QtGui.QColor(0, 0, 255, 127))
        painter.setPen(pen)
        painter.drawEllipse(X, Y, 6, 6)
        pen.setColor(QtGui.QColor('black'))
        painter.setPen(pen)
        painter.setFont(QtGui.QFont("Arial", 14))
        painter.drawText(X, Y, "Beam  x: {}, y: {}".format(X,Y))
        painter.end()
        self.label.repaint()
    # simulate button clicked
    def simulate(self):
        self.ui.lbl_error.setText("")
        canvas = QtGui.QPixmap(self.gui.size())
        canvas.fill(QtGui.QColor("white"))
        self.label.setPixmap(canvas)

        self.get_parameters()

        self.beam(self.coor_beam[0][0], self.coor_beam[0][1])

        if len(self.ui.angle_plate.toPlainText()) > 1:
            self.angle_of_palte = int(self.ui.angle_plate.toPlainText())
            # self.plate(int(self.ui.angle_plate.toPlainText()))
        else:
            self.angle_of_palte = 0
        self.plate(self.angle_of_palte)

        coefficient_y1,m1,c1 = self.lineFromPoints(self.rect_plate[0], self.rect_plate[1])
        coefficient_y2,m2,c2 = self.lineFromPoints(self.rect_plate[2], self.rect_plate[3])
        disc1 = self.distance(self.coor_beam[0][0], self.coor_beam[0][1], -m1, coefficient_y1, -c1)
        disc2 = self.distance(self.coor_beam[0][0], self.coor_beam[0][1], -m2, coefficient_y2, -c2)
        if disc1 > disc2:
            self.coefficient_y, self.m, c = coefficient_y2,m2,c2
            self.disc = disc2
            self.pointA = self.rect_plate[2]
            self.pointB = self.rect_plate[3]
        else:
            self.coefficient_y, self.m, c = coefficient_y1,m1,c1
            self.disc = disc1
            self.pointA = self.rect_plate[0]
            self.pointB = self.rect_plate[1]
        self.posX_perpendicular,self.posY_perpendicular = self.perpendicular_intersection(self.coor_beam[0][0], self.coor_beam[0][1],self.coefficient_y, self.m, c)
        self.draw_incidentray(self.angle_of_beam)
    # get parameters from GUI (what user enter)
    def get_parameters(self):
        #plate
        if len(self.ui.posX_plate.toPlainText()) > 1 and len(self.ui.posY_plate.toPlainText()) > 1:
            if not self.rect_plate:
                self.rect_plate.append([int(self.ui.posX_plate.toPlainText()),int(self.ui.posY_plate.toPlainText())])
            else:
                self.rect_plate[0] = [int(self.ui.posX_plate.toPlainText()),int(self.ui.posY_plate.toPlainText())]
        #beam
            self.coor_beam[0] = [int(self.ui.posX_beam.toPlainText()),int(self.ui.posY_beam.toPlainText())]
        #beam angle
        self.angle_of_beam = int(self.ui.angle_beam.toPlainText())
    # find y = mx +c line equation
    def lineFromPoints(self, point1, point2):
        points = [tuple(point1), tuple(point2)]
        if points[0][0] != points[1][0]:
            coefficient_y = 1
            x_coords, y_coords = zip(*points)
            A = np.vstack([x_coords,np.ones(len(x_coords))]).T
            m, c = np.linalg.lstsq(A, y_coords)[0]
            # print("Line Solution is y = {m}x + {c}".format(m=m,c=c))
        else:
            coefficient_y = 0
            m = 1
            c = points[0][0]
        #y = mx + c
        return coefficient_y,m,c
    # distance ?? from x1,y1 to linear equation 
    def distance(self, x1, y1, a, b, c):
        #ax + by +c = 0
        a = float(a)
        b = float(b)
        c = float(c)
        d = abs((a * x1 + b * y1 + c)) / (math.sqrt(a * a + b * b))
        return d
    # intersection of perpendicular to plate which pass over beam 
    def perpendicular_intersection(self,  x1, y1,coefficient_y, m, c):
        if coefficient_y == 1:
            if m != 0:
                c2 = y1 + (1/m)*x1
                root = np.linalg.solve(np.array([[1/m, 1],[-m,1]]), np.array([c2,c]))
                # self.beam(int(root[0]), int(root[1]))
                return int(root[0]), int(root[1])
            else:
                # self.beam(x1, int(m*x1 + c))
                return x1, int(m*x1 + c)
        else:
            # self.beam(c, y1)
            return c, y1

    def draw_incidentray(self, beam_angle):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(7)
        pen.setColor(QtGui.QColor('blue'))
        painter.setPen(pen)
        D = abs(self.disc * math.tan(self.d2r(90 - beam_angle)))
        # check if incident ray inside the plate or not 
        if self.is_between(self.pointA, [self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)), self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte))], self.pointB):
            # drawing incident ray
            painter.drawLine(self.coor_beam[0][0], self.coor_beam[0][1],self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)), self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)))
            pen.setWidth(1)
            pen.setColor(QtGui.QColor('black'))
            painter.setPen(pen)
            # normal line
            painter.drawLine(self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)), self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)),self.coor_beam[0][0] + D * math.cos(self.d2r(self.angle_of_palte)), self.coor_beam[0][1] + D * math.sin(self.d2r(self.angle_of_palte)))
            pen.setWidth(3.5)
            pen.setColor(QtGui.QColor('red'))
            #pen.setOpacity(0.5)
            painter.setPen(pen)
            # drawing reflected ray
            painter.drawLine(self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)), self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)),self.coor_beam[0][0] + 2 * D * math.cos(self.d2r(self.angle_of_palte)), self.coor_beam[0][1] + 2 * D * math.sin(self.d2r(self.angle_of_palte)))
            pen.setWidth(3.5)
            pen.setColor(QtGui.QColor('green'))
            painter.setPen(pen)
            # drawing refracted ray, which is not working well!! :(
            if (self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) < self.coor_beam[0][0] + 2 * D * math.cos(self.d2r(self.angle_of_palte))) and (self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) > self.coor_beam[0][1] + 2 * D * math.sin(self.d2r(self.angle_of_palte))):
                painter.drawLine(self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)),
                                 self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) + self.thick * math.cos(self.d2r(90 - self.angle_of_beam + self.angle_of_palte)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) + self.thick * math.sin(self.d2r(90 - self.angle_of_beam + self.angle_of_palte))
                                 )
                # print('hi')


            elif (self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) < self.coor_beam[0][0] + 2 * D * math.cos(self.d2r(self.angle_of_palte))) and (self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) < self.coor_beam[0][1] + 2 * D * math.sin(self.d2r(self.angle_of_palte))):
                painter.drawLine(self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)),
                                 self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) - self.thick * math.sin(self.d2r(self.angle_of_palte - self.angle_of_beam)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) + self.thick * math.cos(self.d2r(self.angle_of_palte - self.angle_of_beam))
                                 )
                # print('hii')

            elif (self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) > self.coor_beam[0][0] + 2 * D * math.cos(self.d2r(self.angle_of_palte))) and (self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) < self.coor_beam[0][1] + 2 * D * math.sin(self.d2r(self.angle_of_palte))):
                painter.drawLine(self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)),
                                 self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) - self.thick * math.sin(self.d2r(90 - self.angle_of_palte - self.angle_of_beam)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) - self.thick * math.cos(self.d2r(90 - self.angle_of_palte - self.angle_of_beam))
                                 )
                # print('hiii')

            elif (self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) > self.coor_beam[0][0] + 2 * D * math.cos(self.d2r(self.angle_of_palte))) and (self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) > self.coor_beam[0][1] + 2 * D * math.sin(self.d2r(self.angle_of_palte))):
                painter.drawLine(self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)),
                                 self.posX_perpendicular + D * math.cos(self.d2r(self.angle_of_palte)) + self.thick * math.cos(self.d2r(self.angle_of_beam)),
                                 self.posY_perpendicular + D * math.sin(self.d2r(self.angle_of_palte)) + self.thick * math.sin(self.d2r(self.angle_of_beam))
                                 )
                # print('hiiii')

            painter.end()
            self.label.repaint()
        else:
            self.ui.lbl_error.setText("INVALID INPUT Parameters:(")
    #convert degree to radian
    def d2r(self, degree):
        return degree*math.pi/180

    #calculate distance between 2 points
    def distance_2ponints(self, a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    # check c is between a and b or not
    def is_between(self, a, c, b):
        return int(self.distance_2ponints(a, c)) + int(self.distance_2ponints(c, b)) == int(self.distance_2ponints(a, b))


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()
