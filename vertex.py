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

    def __init__(self, position, rangeLimit, comesFrom, connectionInt):
        self.position = np.array(position)
        self.neighborInfo = []
        self.rangeLimit = rangeLimit
        self.connectionInt = connectionInt

        if comesFrom == [[]]:
            self.comesFrom = [[]]
        else:
            self.comesFrom = comesFrom
            for comesFromVertex in self.comesFrom:
                if comesFromVertex[1] == 0:
                    print(comesFromVertex, 'aaaaaaaaaaaa')
                comesFromVertex[0].goesTo += [[self, -comesFromVertex[1]]]

        self.goesTo = []
        self.isActive = True
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
            self.isActive = False
        return self.inRange    

    def findNeighbor(self, Vertices, distance_neighbor=2):
        self.neighborInfo = []
        for vertex in Vertices:
            distance = self.getDistance(vertex)
            if distance <= distance_neighbor:
                self.neighborInfo += [[vertex, distance]]
        return np.array(self.neighborInfo)

    def randomizePosition(self, randomRange=0.5):
        moveDirection = np.random.random_sample((2,))*randomRange*2 - np.array([randomRange,randomRange])
        self.position += moveDirection
        self.isInRange()

    def addNextVertex(self, directionInstance, distance=5):
        nextVertices = []
        directions = directionInstance.getDirection(self)
        if directions != None:
            for direction in directions:
                nextPosition = self.position + direction[0] * distance
                connectionInt = -direction[1]
                nextVertex = VertexDescendant(nextPosition, self.rangeLimit, comesFrom=[[self, connectionInt]]) 
                nextVertex.randomizePosition()
                nextVertices += [nextVertex]            
            return nextVertices
        else:
            print('No vertex was added!')
            return None    

    '''
    def mapConnectionInt(self, goesToIntList):
        outputList = np.array(goesToIntList) * -1
        return outputList
    '''

    def plot(self, alpha=0.2, color='#ff0000'):
        plt.scatter(self.position[1], self.position[0],alpha=alpha, c=color)

    def plotComesFrom(self, alpha=0.2, color='#ff0000'):
        if self.comesFrom != []:
            for comesFromVertex in self.comesFrom:
                plt.plot([self.position[1],comesFromVertex[0].position[1]],[self.position[0], comesFromVertex[0].position[0]], alpha=alpha, c=color)
    
    def plotGoesTo(self, alpha=0.2, color='#ff0000'):
        if self.goesTo != []:
            for goesToVertex in self.goesTo:
                plt.plot([self.position[1],goesToVertex[0].position[1]],[self.position[0], goesToVertex[0].position[0]], alpha=alpha, c=color)

class VertexOrigin(VertexBase):

    def __init__(self, position, rangeLimit, comesFrom=[[]], connectionInt=[]):
        VertexBase.__init__(self, position, rangeLimit, comesFrom, connectionInt)
        self.index = VertexBase.totalIndex
        VertexBase.totalIndex += 1

class VertexDescendant(VertexBase):

    def __init__(self, position, rangeLimit, comesFrom=[[]], connectionInt=[]):
        VertexBase.__init__(self, position, rangeLimit, comesFrom, connectionInt)
        self.index = VertexBase.totalIndex
        VertexBase.totalIndex += 1

    def removeVertex(self):
        VertexBase.totalIndex -= 1
        #print('Total index now is: '+ str(VertexBase.totalIndex))
    
        if self.comesFrom != [[]]:
            for comesFromVertex in self.comesFrom:
                np.delete(comesFromVertex[0].goesTo, np.where(comesFromVertex[0].goesTo[0]==self))

        if self.goesTo != []:
            for goesToVertex in self.goesTo:
                np.delete(goesToVertex[0].comesFrom, np.where(goesToVertex[0].comesFrom[0]==self))
                #goesToVertex.comesFrom.remove(self) 

class VertexLayer():

    def __init__(self, randomScatterInstance, directionInstance):
        self.verticesOrigin = []
        self.rangeLimit = randomScatterInstance.shape
        for point in randomScatterInstance.improvedPoints:
            if point[0] >=0 and point[0] <= randomScatterInstance.shape[0] and point[1] >=0 and point[1] <= randomScatterInstance.shape[1]:
                self.verticesOrigin += [VertexOrigin(point, self.rangeLimit)]       
        self.verticesCurrent = copy.copy(self.verticesOrigin)
        self.verticesAll = []
        #self.verticesAll = copy.copy(self.verticesCurrent)
        self.verticesNext = []
        self.directionInstance = directionInstance

    def getNextVertices(self, distance_next=5):
        self.verticesNext = []
        for vertex in self.verticesCurrent:
            if vertex.inRange:
                vertexNext = vertex.addNextVertex(self.directionInstance, distance_next)
                if vertexNext != None:
                    self.verticesNext += vertexNext                

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

    def mergeNextVertices(self, distance_merge=2):
        newVertices = []
        for vertex in self.verticesNext:
            neighborInfo = vertex.findNeighbor(self.verticesNext, distance_merge)
            comesFromList = []
            if len(neighborInfo) >= 2:
                newPosition = self.getAveragePosition(neighborInfo[:-1,0])
                for vertexNeighbor in neighborInfo[:,0]:
                    comesFromList += vertexNeighbor.comesFrom
                    self.verticesNext.remove(vertexNeighbor)
                    vertexNeighbor.removeVertex()
                #comesFromList = np.array([vertexNeighbor.comesFrom for vertexNeighbor in neighborInfo[:,0]]).flatten()
                #comesFromList = self.nonDuplicate(comesFromList)
                newVertex = VertexDescendant(newPosition, self.rangeLimit, comesFrom=comesFromList)
                newVertex.isInRange()
                newVertices += [newVertex]

        self.verticesNext += newVertices                

    def mergeToAll(self, distance_merge=2):
        for vertex in self.verticesNext:
            neighborInfo = vertex.findNeighbor(self.verticesAll, distance_merge)
            if len(neighborInfo) >= 1:
                neighborInfo = neighborInfo[neighborInfo[:,1].argsort()]
                mergeVertex = neighborInfo[0][0]
                mergeVertex.comesFrom = vertex.comesFrom
                for comesFromVertex in vertex.comesFrom:
                    comesFromVertex[0].goesTo += [[mergeVertex, comesFromVertex[1]]]
                self.verticesNext.remove(vertex)
                vertex.removeVertex()
                self.verticesNext += [mergeVertex]
                self.verticesAll.remove(mergeVertex)
                mergeVertex.isActive = True
                mergeVertex.isInRange()
        
    def plotVertices(self, vertices, alpha=0.2, color='#ff0000'):
        for vertex in vertices:
            vertex.plot(alpha, color)
        plt.draw()
        plt.pause(0.01)    

    def plotLines(self, vertices, comesFrom=True, alpha=0.2, color='#ff0000'):
        if comesFrom:
            for vertex in vertices:
                vertex.plotComesFrom(alpha, color) 
        else:
            for vertex in vertices:
                vertex.plotGoesTo(alpha, color)              
        plt.draw()
        plt.pause(0.01)     



'''
vex1 = VertexOrigin([1, 2])
vex2 = VertexOrigin([2, 4], vex1)

vex3 = vex2.addNextVertex(5)
print(vex3.comesFrom[0].position)
vex2.removeVertex()
'''
