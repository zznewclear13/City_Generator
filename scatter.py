import matplotlib.pyplot as plt
import numpy as np
import cv2
import math
import random
import bisect

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

    def drawScatter(self, alpha):
        self.ax = plt.scatter(self.col, self.row, alpha=alpha)
        plt.show()    

ERROR_MESSAGE = '----------------------'

if __name__ == "__main__":
    IMAGE_INPUT_PATH = './image_input/scatter_rate.jpg'

    randomScatterInstance = randomScatter(IMAGE_INPUT_PATH, 20000, 0, reverse=True, squared=True)
    randomScatterInstance.readImage()
    randomScatterInstance.randomDots()
    randomScatterInstance.initialise_figure()
    randomScatterInstance.drawScatter(0.1)
