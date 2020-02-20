import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import math
import random
import bisect
import copy
from scipy.spatial import Voronoi, voronoi_plot_2d
from itertools import accumulate

from randomScatter import RandomScatter
from direction import Direction
from vertex import VertexBase, VertexOrigin, VertexLayer


if __name__ =="__main__":

    ERROR_MESSAGE = '----------------------'
    IMAGE_INPUT_PATH = './image_input/scatter_rate.jpg'
    IMAGE_OUTPUT_PATH = './image_output/'
    ROADMAP_RECTANGLE = ['./image_input/roadMapRectangle_00.jpg']
    ROADMAP_CIRCLE = ['./image_input/roadMapCircle_00.jpg',
                        './image_input/roadMapCircle_01.jpg',
                        './image_input/roadMapCircle_02.jpg',
                        './image_input/roadMapCircle_03.jpg']

    if not os.path.exists(IMAGE_OUTPUT_PATH):
        os.mkdir(IMAGE_OUTPUT_PATH)

    randomScatterInstance = RandomScatter(IMAGE_INPUT_PATH, 200, 0, reverse=True, squared=True)
    randomScatterInstance.readImage()
    randomScatterInstance.randomDots()
    randomScatterInstance.makePoints()

    #run improvePoints twice to refine points' locations
    randomScatterInstance.improvePoints(randomScatterInstance.points)
    randomScatterInstance.improvePoints(randomScatterInstance.improvedPoints) * 1

    directionInstance = Direction(ROADMAP_RECTANGLE, ROADMAP_CIRCLE)

    vertexLayertInstance = VertexLayer(randomScatterInstance, directionInstance)
    
    plt.ion()
    plt.ioff()
    plt.show()
    fig = plt.figure(figsize=(10,10))
    ax = plt.gca()
    ax.set_xlim(left=0, right=randomScatterInstance.shape[1])
    ax.set_ylim(top=0, bottom=randomScatterInstance.shape[0])

    
    for i in range(20):
        vertexLayertInstance.getNextVertices()
        vertexLayertInstance.mergeNextVertices(5)
        vertexLayertInstance.mergeToAll(3)
        vertexLayertInstance.plotLines(vertexLayertInstance.verticesNext, True)
        if len(vertexLayertInstance.verticesNext)<=3:
            break
        vertexLayertInstance.changeNextVertices()


    #vertexLayertInstance.plotLines(vertexLayertInstance.verticesAll+vertexLayertInstance.verticesOrigin)
    #vertexLayertInstance.plotVertices(vertexLayertInstance.verticesOrigin)

    plt.savefig(IMAGE_OUTPUT_PATH+'output.png')
    plt.pause(0)
