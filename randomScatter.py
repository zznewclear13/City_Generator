import matplotlib.pyplot as plt
import numpy as np
import cv2
import math
import random
import bisect
from scipy.spatial import Voronoi, voronoi_plot_2d

from itertools import accumulate

class randomScatter():

    def __init__(self, imagePath, dotsCount, randomBias, reverse=False, squared =False):
        self.imagePath = imagePath
        self.dotsCount = dotsCount
        self.randomBias = randomBias
        self.reverse = reverse
        self.squared = squared
        self.position = []
        self.row = []
        self.col = []
        self.points = []
        self.improvedPoints = []

    def plotRandomMat(self, shape, ax):
        x = np.random.rand(shape[0])
        y = np.random.rand(shape[0])
        ax = plt.scatter(x,y)
        plt.show()

    def initialise_figure(self):
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, figsize=(6,6))  
        self.ax.set_xlim(left=0, right=self.shape[1])
        self.ax.set_ylim(top=0, bottom=self.shape[0])

    def readImage(self):
        try:
            self.image = cv2.imread(self.imagePath)
            self.shape = self.image.shape
            try:
                if self.shape[2] == 3:
                    self.image = self.image[:,:,0]
                    self.shape = self.image.shape
            except:
                pass        
        except:
            print(ERROR_MESSAGE)
            print("Check IMAGE_INPUT_PATH! IMAGE_INPUT_PATH='"+ IMAGE_INPUT_PATH + "'.")
            print(ERROR_MESSAGE) 
        self.image = (self.image, np.ones(self.shape)*255 - self.image)[self.reverse] #(False, True)[True] 

    def randomDots(self):
        biasedImage = self.image.flatten() + np.ones(self.shape[0]*self.shape[1])*self.randomBias*255
        if self.squared:
            biasedImage = [item*item for item in biasedImage]  
        biasedList = list(accumulate(biasedImage))
        for _ in range(self.dotsCount):
            position = self.getRandomFromList(biasedList)
            self.col += [position % self.shape[0]]
            self.row += [position //self.shape[0]]

    def getRandomFromList(self, inputList):
        randomNumber = random.random()*inputList[-1]
        index = bisect.bisect_right(inputList, randomNumber)
        return index

    def makePoints(self):
        self.points = [list(pair) for pair in zip(self.row, self.col)]
        return self.points

    def improvePoints(self, points):
        self.improvedPoints = []
        vor = Voronoi(points)
        for region in vor.regions:
            if not -1 in region:
                regionPoints = np.array([vor.vertices[i] for i in region])
                np.sum(regionPoints, axis=0)
                if list(regionPoints.shape)[0] != 0:
                    newPosition = list(np.sum(regionPoints, axis=0)/list(regionPoints.shape)[0])
                    if newPosition[0] >=-self.shape[0] and newPosition[0] <= self.shape[0]*2 and newPosition[1] >=-self.shape[1] and newPosition[1] <= self.shape[1]*2:
                        self.improvedPoints += [newPosition]    
        return self.improvedPoints        

    def drawScatter(self, points, alpha, color='#000000'):
        points = np.array(points)
        self.ax = plt.scatter(points[:,1], points[:,0], alpha=alpha, c=color) #flip the diagram vertically
  

ERROR_MESSAGE = '----------------------'

if __name__ == "__main__":
    IMAGE_INPUT_PATH = './image_input/scatter_rate.jpg'

    randomScatterInstance = randomScatter(IMAGE_INPUT_PATH, 200, 0, reverse=True, squared=True)
    randomScatterInstance.readImage()
    randomScatterInstance.randomDots()
    randomScatterInstance.makePoints()
    randomScatterInstance.initialise_figure()

    #run improvePoints twice to refine points' locations
    randomScatterInstance.improvePoints(randomScatterInstance.points)
    newPoints = randomScatterInstance.improvePoints(randomScatterInstance.improvedPoints) * 1

    randomScatterInstance.drawScatter(randomScatterInstance.improvedPoints, 0.25, '#ff0000')
    plt.show()
