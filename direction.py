import matplotlib.pyplot as plt
import numpy as np
import cv2
import math
import random

from vertex import VertexBase, VertexOrigin

class RoadMapBase():
    def __init__(self, path, mapType, reverse=False):
        try:
            self.mapInfo = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            self.shape = self.mapInfo.shape
        except AttributeError:
            print(ERROR_MESSAGE)
            print("Input map path is '" + path + "', is it correct?")
            print(ERROR_MESSAGE)
        self.mapInfo = (np.ones(self.shape)*255 - self.mapInfo, self.mapInfo)[reverse] #(False, True)[True] 
        self.mapType = mapType

    def getProbability(self, position):
        probability = self.mapInfo[int(position[0])][int(position[1])]/255
        return [probability, self]

    #return [[main,1][reverseMain,-1]] ...
    def getOriginalDirection(self, vertex):
        childMainDirection = getattr(self, 'getMainDirection')
        mainDirection = childMainDirection(vertex.position)
        verticalDirection= [-mainDirection[1], mainDirection[0]]
        randomDecision = random.random()
        if randomDecision <0.33:
            return [[np.array(mainDirection),1], [-np.array(mainDirection),-1]]
        elif randomDecision <0.66:
            return [[np.array(mainDirection),1], [np.array(verticalDirection),2], [-np.array(mainDirection),-1], [-np.array(verticalDirection),-2]]
        else:
            return [[np.array(verticalDirection),2], [-np.array(verticalDirection),-2]]
    
    #return [[mainDirection, 1]] ...
    def getDirection(self, vertex):
        childMainDirection = getattr(self, 'getMainDirection')
        mainDirection = childMainDirection(vertex.position)
        vectorList = []
        connectionIntList = []
        for comesFromVertex in vertex.comesFrom:
            vectorList += [vertex.position - comesFromVertex[0].position]
            connectionIntList += [comesFromVertex[1]]
        vector = sum(vectorList)/len(vectorList)

        suggestions = self.correctDirection(vector, mainDirection)
        for i, suggestion in enumerate(suggestions):
            if suggestion[1] not in connectionIntList:
                return [suggestion]
                
        return None        
        '''
        returnDirection = self.correctDirection(vector, mainDirection)[0]
        return [returnDirection]   
        ''' 

    # return [mainDirection, 1][reverseMainDirection, -1][verticalDirection, 2][reverseVerticalDirection, -2]
    def correctDirection(self, direction, mainDirection):
        verticalDirection= [-mainDirection[1], mainDirection[0]]
        dotProduct01 = np.dot(direction,mainDirection)  
        dotProduct02 = np.dot(direction, verticalDirection)
        if(abs(dotProduct01) >= abs(dotProduct02)):
            return [np.array(mainDirection) * np.sign(dotProduct01), np.sign(dotProduct01)], [np.array(verticalDirection) * np.sign(dotProduct02), np.sign(dotProduct02)*2]
        else:
            return [np.array(verticalDirection) * np.sign(dotProduct02), np.sign(dotProduct02)*2], [np.array(mainDirection) * np.sign(dotProduct01), np.sign(dotProduct01)]

class RoadMapRectangle(RoadMapBase):
    def __init__(self, path):
        RoadMapBase.__init__(self, path, 'rectangle')
        self.mainDirection = [math.cos(math.radians(random.randint(0,359))), math.sin(math.radians(random.randint(0,359)))]

    def getMainDirection(self, position):
        return self.mainDirection

class RoadMapCircle(RoadMapBase):

    def __init__(self, path, center=[]):
        RoadMapBase.__init__(self, path, 'circle')
        self.center = center

        if len(self.center) != 2:
            self.initCenter()

    def initCenter(self):
        rowSum = np.sum(self.mapInfo, axis=1)
        columnSum = np.sum(self.mapInfo, axis=0)
        rowIndexList = np.where(columnSum==np.max(columnSum))[0]
        columnIndexList = np.where(rowSum==np.max(rowSum))[0]
        centerX = rowIndexList[len(rowIndexList)//2]
        centerY = columnIndexList[len(columnIndexList)//2]
        self.center = [centerX, centerY]
        return self.center

    def getMainDirection(self, position):
        mainDirection = (self.center - position)/np.linalg.norm(self.center-position)
        return mainDirection
                    
class Direction():
    def __init__(self, pathToRectangle, pathToCircle):
        self.pathToRectangle = pathToRectangle
        self.pathToCircle = pathToCircle

        self.roadMapList = []
        for path in self.pathToRectangle:
            roadMapRectangleInstance = RoadMapRectangle(path)
            self.roadMapList += [roadMapRectangleInstance]
        for path in self.pathToCircle:
            roadMapCircleInstance = RoadMapCircle(path)
            self.roadMapList += [roadMapCircleInstance]    

    def getDirection(self, vertex):
        probabilityList = []
        position = vertex.position
        for roadMap in self.roadMapList:
            try:
                probabilityList += [roadMap.getProbability(position)]  
            except IndexError:
                print('----------------------')  
                print(vertex.position)
                print(vertex.inRange)
                print(vertex.rangeLimit)
                print('----------------------') 
        probabilityList.sort(key = lambda x: x[0])    
        choosenMap = probabilityList[-1][1]

        if isinstance(vertex, VertexOrigin):
            return choosenMap.getOriginalDirection(vertex)
        else:
            return choosenMap.getDirection(vertex)    


if __name__ == "__main__":

    ERROR_MESSAGE = '----------------------'

    path01 = ['./image_input/roadMapRectangle_00.jpg']
    path02 = ['./image_input/roadMapCircle_00.jpg']
    path03 = ['./image_input/emptyMap_00.jpg']

    roadMapRectangle_00 = RoadMapRectangle(path01)
    roadMapCircle_00 = RoadMapCircle(path02)