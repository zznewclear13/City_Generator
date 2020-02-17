import matplotlib.pyplot as plt
import numpy as np
import cv2
import math
import random
import bisect
import copy
from scipy.spatial import Voronoi, voronoi_plot_2d
from itertools import accumulate

from randomScatter import randomScatter


RANGE = 5

class VertexBase():

    totalIndex = 0

    def __init__(self, position):
        self.position = np.array(position)
        self.neighborInfo = []

    def getDistance(self, vertex):
        distance = np.linalg.norm(self.position-vertex.position)
        return distance    

    def findNeighbor(self, Vertices, DISTANCE_NEIGHBOR=2):
        self.neighborInfo = []
        for vertex in Vertices:
            distance = self.getDistance(vertex)
            if distance <= DISTANCE_NEIGHBOR:
                self.neighborInfo += [[vertex, distance]]
        return np.array(self.neighborInfo)

    def randomizePosition(self, RANGE=1):
        moveDirection = np.random.random_sample((2,))*RANGE*2 - np.array([RANGE,RANGE])
        return self.position + moveDirection 

    def plot(self,alpha=0.2, color='#ff0000'):
        plt.scatter(self.position[1], self.position[0],alpha=alpha, c=color)

class VertexOrigin(VertexBase):

    def __init__(self, position, comesFrom=[]):
        VertexBase.__init__(self, position)
        self.index = VertexBase.totalIndex
        VertexBase.totalIndex += 1

        if comesFrom == []:
            self.comesFrom = []
        else:
            self.comesFrom = comesFrom
            for comesFromVertex in comesFrom:
                comesFromVertex.goesTo += [self]    

        self.goesTo = []


    def addNextVertex(self, DISTANCE=5):
        if self.comesFrom != []:
            for comesFromVertex in self.comesFrom:
                direction = (self.position - comesFromVertex.position)/self.getDistance(comesFromVertex)
                nextPosition = self.position + direction * DISTANCE
                nextVertex = VertexOrigin(nextPosition, comesFrom=[self])
                nextVertex.position = nextVertex.randomizePosition()
            return nextVertex
        else:
            nextPosition = self.randomizePosition()
            nextVertex = VertexOrigin(nextPosition, comesFrom=[self])
            nextVertex.position = nextVertex.randomizePosition()
            return nextVertex

    def removeVertex(self):
        VertexBase.totalIndex -= 1
        print('Total index now is: '+ str(VertexBase.totalIndex))
    
        if self.comesFrom != []:
            for comesFromVertex in self.comesFrom:
                comesFromVertex.goesTo.remove(self)

        if self.goesTo != []:
            for goesToVertex in self.goesTo:
                goesToVertex.comesFrom.remove(self) 

    def plotComesFrom(self, alpha=0.2, color='#ff0000'):
        if self.comesFrom != []:
            for comesFromVertex in self.comesFrom:
                plt.plot([self.position[1],comesFromVertex.position[1]],[self.position[0], comesFromVertex.position[0]], alpha=alpha, c=color)


class VertexLayer():

    def __init__(self, randomScatterInstance):
        self.verticesOrigin = []
        for point in randomScatterInstance.improvedPoints:
            if point[0] >=0 and point[0] <= randomScatterInstance.shape[0] and point[1] >=0 and point[1] <= randomScatterInstance.shape[1]:
                self.verticesOrigin += [VertexOrigin(point)]       
        self.verticesCurrent = copy.copy(self.verticesOrigin)
        self.verticesAll = copy.copy(self.verticesCurrent)
        self.verticesNext = []

    def getNextVertices(self, DISTANCE_NEXT=5):
        self.verticesNext = []
        for vertex in self.verticesCurrent:
            vertexNext = vertex.addNextVertex(DISTANCE_NEXT)
            self.verticesNext += [vertexNext]

    def changeNextVertices(self):
        self.verticesCurrent = self.verticesNext
        self.verticesAll += self.verticesNext
        self.verticesNext = []

    def nonDuplicate(self, inputList):
        outputList = []
        for item in inputList:
            if item not in outputList:
                outputList.append(item)
        return outputList        

    def getAveragePosition(self, vertices):
        try:
            posX = 0
            posY = 0
            for vertex in vertices:
                posX += vertex.position[0]
                posY += vertex.position[1]
            return [posX/len(vertices), posY/len(vertices)]
        except:
            print('vertices is empty') 
            return None  

    def mergeNextVertices(self, DISTANCE_MERGE=2):
        newVertices = []
        for vertex in self.verticesNext:
            neighborInfo = vertex.findNeighbor(self.verticesNext, DISTANCE_MERGE)
            if len(neighborInfo) >= 2:
                newPosition = self.getAveragePosition(neighborInfo[:-1,0])

                comesFromList = np.array([vertexNeighbor.comesFrom for vertexNeighbor in neighborInfo[:,0]]).flatten()
                comesFromList = self.nonDuplicate(comesFromList)

                newVertex = VertexOrigin(newPosition, comesFrom=comesFromList)
                newVertices += [newVertex]
                for neighbor in neighborInfo[:,0]:
                    self.verticesNext.remove(neighbor)
        self.verticesNext += newVertices    

    def plotVertices(self, vertices,alpha=0.2, color='#ff0000'):
        for vertex in vertices:
            vertex.plot(alpha, color)

    def plotLines(self, vertices, alpha=0.2, color='#ff0000'):
        for vertex in vertices:
            vertex.plotComesFrom(alpha, color)        



'''
vex1 = VertexOrigin([1, 2])
vex2 = VertexOrigin([2, 4], vex1)

vex3 = vex2.addNextVertex(5)
print(vex3.comesFrom[0].position)
vex2.removeVertex()
'''

IMAGE_INPUT_PATH = './image_input/scatter_rate.jpg'


randomScatterInstance = randomScatter(IMAGE_INPUT_PATH, 200, 0, reverse=True, squared=True)
randomScatterInstance.readImage()
randomScatterInstance.randomDots()
randomScatterInstance.makePoints()

#run improvePoints twice to refine points' locations
randomScatterInstance.improvePoints(randomScatterInstance.points)
randomScatterInstance.improvePoints(randomScatterInstance.improvedPoints) * 1

vertexLayertInstance = VertexLayer(randomScatterInstance)
for i in range(6):
    vertexLayertInstance.getNextVertices()
    vertexLayertInstance.mergeNextVertices(5)
    vertexLayertInstance.changeNextVertices()

fig = plt.figure()
ax = plt.gca()
ax.set_xlim(left=0, right=randomScatterInstance.shape[1])
ax.set_ylim(top=0, bottom=randomScatterInstance.shape[0])

vertexLayertInstance.plotLines(vertexLayertInstance.verticesAll)
print(len(vertexLayertInstance.verticesOrigin))
vertexLayertInstance.plotVertices(vertexLayertInstance.verticesOrigin)
plt.show()
