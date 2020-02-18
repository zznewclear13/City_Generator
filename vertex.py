import matplotlib.pyplot as plt
import numpy as np
import cv2
import math
import random
import bisect
import copy
from scipy.spatial import Voronoi, voronoi_plot_2d
from itertools import accumulate

#from randomScatter import RandomScatter


class VertexBase():

    totalIndex = 0

    def __init__(self, position, rangeLimit):
        self.position = np.array(position)
        self.neighborInfo = []
        self.rangeLimit = rangeLimit
        self.isInRange()

    def getDistance(self, vertex):
        distance = np.linalg.norm(self.position-vertex.position)
        return distance    

    def isInRange(self):
        if self.position[0]>=0 and self.position[0]<=self.rangeLimit[0] \
            and self.position[1]>=0 and self.position[1]<=self.rangeLimit[1]:
            self.inRange = True
        else:
            self.inRange = False
        return self.inRange    

    def findNeighbor(self, Vertices, DISTANCE_NEIGHBOR=2):
        self.neighborInfo = []
        for vertex in Vertices:
            distance = self.getDistance(vertex)
            if distance <= DISTANCE_NEIGHBOR:
                self.neighborInfo += [[vertex, distance]]
        return np.array(self.neighborInfo)

    def randomPosition(self, randomRange=1):
        moveDirection = np.random.random_sample((2,))*randomRange*2 - np.array([randomRange,randomRange])
        return self.position + moveDirection 

    def randomizePosition(self, randomRange=1):
        self.position = self.randomPosition(randomRange)
        self.isInRange()

    def plot(self,alpha=0.2, color='#ff0000'):
        plt.scatter(self.position[1], self.position[0],alpha=alpha, c=color)

class VertexOrigin(VertexBase):

    def __init__(self, position, rangeLimit, comesFrom=[]):
        VertexBase.__init__(self, position, rangeLimit)
        self.index = VertexBase.totalIndex
        VertexBase.totalIndex += 1

        if comesFrom == []:
            self.comesFrom = []
        else:
            self.comesFrom = comesFrom
            for comesFromVertex in comesFrom:
                comesFromVertex.goesTo += [self]    

        self.goesTo = []

    def addNextVertex(self, directionInstance, distance=5):
        if self.comesFrom != []:
            directions = directionInstance.getDirection(self)
            for direction in directions:
                nextPosition = self.position + direction * distance
                nextVertex = VertexOrigin(nextPosition, self.rangeLimit, comesFrom=[self])
                nextVertex.randomizePosition()
            return nextVertex
        else:
            nextPosition = self.randomPosition()
            nextVertex = VertexOrigin(nextPosition, self.rangeLimit, comesFrom=[self])
            nextVertex.randomizePosition()
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

    def __init__(self, randomScatterInstance, directionInstance):
        self.verticesOrigin = []
        self.rangeLimit = randomScatterInstance.shape
        for point in randomScatterInstance.improvedPoints:
            if point[0] >=0 and point[0] <= randomScatterInstance.shape[0] and point[1] >=0 and point[1] <= randomScatterInstance.shape[1]:
                self.verticesOrigin += [VertexOrigin(point, self.rangeLimit)]       
        self.verticesCurrent = copy.copy(self.verticesOrigin)
        self.verticesAll = copy.copy(self.verticesCurrent)
        self.verticesNext = []
        self.directionInstance = directionInstance

    def getNextVertices(self, DISTANCE_NEXT=5):
        self.verticesNext = []
        for vertex in self.verticesCurrent:
            if vertex.inRange:
                vertexNext = vertex.addNextVertex(self.directionInstance, distance=5)
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

                newVertex = VertexOrigin(newPosition, self.rangeLimit, comesFrom=comesFromList)
                newVertex.isInRange()
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
