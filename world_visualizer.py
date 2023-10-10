import sqlite3
import json
import matplotlib.pyplot as plt
from db_connection import Connection
import turtle
import math
import random
from tkinter import PhotoImage


class Island():
    def __init__(self) -> None:
        turtle.setup(1000,1000)
        turtle.title("Random Island Generator - PythonTurtle.Academy")
        turtle.speed(0)
        turtle.hideturtle()
        turtle.tracer(0,0)    
        turtle.bgcolor('royal blue')
        turtle.pencolor('green')
        turtle.fillcolor('forest green')
        turtle.begin_fill()
        self.shoreline(-300,0,300,0,0.55) # call recursion
        self.shoreline(300,0,-300,0,0.55) # call recursion
        turtle.end_fill()
        turtle.update()
        turtle.done()

    @staticmethod
    def draw_line(x1,y1,x2,y2): # function to draw line
        turtle.up()
        turtle.goto(x1,y1)
        turtle.down()
        turtle.goto(x2,y2)

    @staticmethod
    def dist(p1,p2): # Euclidean distance betwen p1 and p2
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

    def shoreline(self,x1,y1,x2,y2,ratio): # recurisve function to draw the shoreline
        L = self.dist((x1,y1),(x2,y2))
        if L <= 1: # distance is short enough, directly draw the line
            self.draw_line(x1,y1,x2,y2)
            return
        rs = ratio + random.uniform(-0.1,0.1) # let ratio flucuate slightly around the chosen value
        rs = max(0.5,rs) # make sure ratio stays at least half of the length
        midx = (x1+x2)/2 # center of ellipse
        midy = (y1+y2)/2    
        rx = L/2 + (2*rs-1)/2*L # width of ellipse
        ry = ((L*rs)**2 - (L/2)**2)**0.5 # height of ellipse
        theta = math.atan2(y2-y1,x2-x1) # the tilt angle of ellipse
        alpha = random.uniform(math.pi*0.3,math.pi*0.7) # flucuate around math.pi/2
        x3 = rx*math.cos(alpha)*math.cos(theta) - ry*math.sin(alpha)*math.sin(theta) + midx # parametric equation for ellipse
        y3 = rx*math.cos(alpha)*math.sin(theta) + ry*math.sin(alpha)*math.cos(theta) + midy
        self.shoreline(x1,y1,x3,y3,ratio) # do this recursively on each segment
        self.shoreline(x3,y3,x2,y2,ratio)

def load_json_data(path):
    with open(path, "r") as json_data:
        data=json.load(json_data)
        return data

def get_animals_by_region():
    try:
        animal_data=load_json_data('animals.json')
        animal_names = []  
        for animal_name, animal_attributes in animal_data.items():
            animal_names.append(animal_name)

        conn = Connection.get_connection()
        
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Terrain')
        results = cursor.fetchall()
        for result in results:
            result=result[0]
            print(result)
            if result:
                for animal in animal_data:
                    cursor.execute('SELECT COUNT(*) FROM animals WHERE terrain_id = ? AND name = ?',(str(result), animal))
                    inner_result=cursor.fetchone()[0]
                    print(f"There are {inner_result} {animal}")
            else:
                print("Query returned no results.")
        
    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        conn.close()
        print("Database connection closed.")

def visualize_terrain(terrain_data):
    plt.figure(figsize=(8, 8))
    
    for terrain_name, terrain_attributes in terrain_data.items():
        area = terrain_attributes.get("area", 0)
        color = terrain_attributes.get("color")
        size = int(area ** 0.5)
        plt.gca().add_patch(plt.Rectangle((0, 0), size/10, size/10, color=color, label=terrain_name))
    
    plt.legend()
    plt.axis('off') 
    plt.show()

    
if __name__ == "__main__":
    terrain_data = load_json_data("terrain.json")
    get_animals_by_region()
    #visualize_terrain(terrain_data)