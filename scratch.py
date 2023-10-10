# Refactor needed - aim to reduce the number of functions, and calls to convert between image and np

import turtle
import math
import random
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi
from scipy import ndimage
import cv2
import os

class Island():
    __map_path:str=None
    __outline=None
    def __init__(self) -> None:
        self.__map_path="img/map"
        turtle.setup(1100,1100)
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
        cv = turtle.getcanvas()
        cv.postscript(file=self.map_path(False), colormode='color')
        self.convert_to_png(self.map_path(False), self.map_path())
        self.flood_fill_centre()
        self.color_outer_green_to_yellow()
        self.color_white_to_blue()
        self.generate_voronoi_noise()
        self.replace_green_with_noise()
        self.save_color_blocks()
        self.split_color_block_by_color()

    def map_path(self, is_bmp=True):
        map_temp=self.__map_path
        if(is_bmp):
            map_temp+=".png"
        else:
            map_temp+=".ps"
        return map_temp

    

    @staticmethod
    def convert_to_png(ps_path, output_path):
        with open(ps_path, 'r') as ps_file:
            lines = ps_file.readlines()
        points = []
        for line in lines:
            if "lineto" in line:
                coordinates = line.split()[:2]
                if len(coordinates) == 2:
                    try:
                        x, y = map(float, coordinates)
                        points.append((x, y))
                    except ValueError:
                        pass

        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)-100
        max_y = max(point[1] for point in points)+100

        width = int(max_x - min_x) + 1
        height = int(max_y - min_y) + 1
        canvas = np.zeros((height, width, 3), dtype=np.uint8) + 255  # Initialize with white (255, 255, 255)
        draw = ImageDraw.Draw(Image.fromarray(canvas))
        current_x, current_y = None, None
        transformed_coordinates = []
        for x, y in points:
            transformed_x = int(x - min_x)
            transformed_y = int(y - min_y)
            transformed_coordinates.append((transformed_x, transformed_y))
        line_image = Image.new('RGB', (width, height), (255, 255, 255))
        draw_lines = ImageDraw.Draw(line_image)
        for i in range(1, len(transformed_coordinates) - 1): 
            x, y = transformed_coordinates[i]
            x_offset = 80  # Adjust this value as needed
            y_offset = -20  # Adjust this value as needed
            x -= x_offset
            y -= y_offset
            if current_x is not None and current_y is not None and abs(x - current_x) < 2 and abs(y - current_y) < 2:
                draw_lines.line(
                    [(current_x, current_y), (x, y)],
                    fill=(0, 255, 0), width=2
                )
            current_x, current_y = x, y
        canvas_image = Image.fromarray(canvas)
        canvas_image.paste(line_image, (0, 0))
        x_offset = (width - canvas_image.width) // 2
        y_offset = (height - canvas_image.height) // 2
        centered_canvas = np.zeros((height, width, 3), dtype=np.uint8) + 255  # Initialize with white (255, 255, 255)
        centered_canvas[y_offset:y_offset + canvas_image.height, x_offset:x_offset + canvas_image.width] = canvas_image
        final_canvas_image = Image.fromarray(centered_canvas)
        final_canvas_image.save(output_path, 'PNG')
        
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

    def flood_fill_centre(self):
        image_blob = None
        with Image.open(self.map_path()) as image:
            image_blob = np.array(image)
        self.__outline=np.copy(image_blob)
        x, y, _ = image_blob.shape
        
        x_center, y_center = x // 2, y // 2
        unfilled_pixels = [(x_center, y_center)]
        target_color = [255, 255, 255]
        replacement_color = [0, 255, 0]
        while unfilled_pixels:
            pixel = unfilled_pixels.pop()
            xpix, ypix = pixel
            if (xpix >= 0 and xpix < x) and (ypix >= 0 and ypix < y) and not np.array_equal(image_blob[xpix, ypix], replacement_color):
                if np.array_equal(image_blob[xpix, ypix], target_color):
                    image_blob[xpix, ypix] = replacement_color
                    unfilled_pixels.extend([(xpix - 1, ypix), (xpix + 1, ypix), (xpix, ypix - 1), (xpix, ypix + 1)])
        modified_image = Image.fromarray(image_blob)
        modified_image.save(self.map_path())
        return None

    def color_outer_green_to_yellow(self):
        path = self.map_path()
        with Image.open(path) as im:
            image_blob = np.array(im)

        target_color = [0, 255, 0]  # Green
        outline_color = [255, 255, 0]  # Yellow (outline color)

        # Iterate through the pixels of the outline image
        for xpix in range(image_blob.shape[0]):
            for ypix in range(image_blob.shape[1]):
                if np.array_equal(self.__outline[xpix, ypix], target_color):
                    # If the pixel in the outline is green, draw a yellow pixel in the original image
                    image_blob[xpix, ypix] = outline_color

        modified_image = Image.fromarray(image_blob)
        modified_image.save(path)
        return None

    def color_white_to_blue(self):
        path = self.map_path()
        with Image.open(path) as im:
            image_blob = np.array(im)

        white_color = [255, 255, 255]  # White
        blue_color = [0, 0, 255]  # Blue

        # Iterate through the pixels of the image
        for xpix in range(image_blob.shape[0]):
            for ypix in range(image_blob.shape[1]):
                if np.array_equal(image_blob[xpix, ypix], white_color):
                    # If the pixel is white, change it to blue
                    image_blob[xpix, ypix] = blue_color

        modified_image = Image.fromarray(image_blob)
        modified_image.save(path)
        return None

    def generate_voronoi_noise(self):
        if self.__outline is None:
            # Load the outline image if it hasn't been loaded yet
            with Image.open(self.map_path()) as im:
                self.__outline = np.array(im)

        width, height, _ = self.__outline.shape

        # Generate a larger number of random colors
        num_colors = 6  # Adjust the number of colors as needed
        colors = np.random.randint(0, 256, size=(num_colors, 3), dtype=np.uint8)
        # Generate random points as Voronoi sites
        num_points = width * height // 10000  # Adjust the density as needed
        points = np.random.randint(0, max(width, height), size=(num_points, 2))

        # Create Voronoi diagram
        vor = Voronoi(points)

        voronoi_image = np.zeros((width, height, 3), dtype=np.uint8)
        for region_idx, region in enumerate(vor.regions):
            if not -1 in region and len(region) > 0:
                polygon = [vor.vertices[i] for i in region]
                polygon = np.array(polygon, dtype=int)
                
                # Assign a random color from the list of colors to each region
                color = tuple(map(int, colors[region_idx % num_colors]))
                
                cv2.fillPoly(voronoi_image, [polygon], color)

        # Save the Voronoi noise image
        modified_image = Image.fromarray(voronoi_image)
        modified_image.save("img/noise.png")

    def replace_green_with_noise(self):
        img_path = self.map_path()
        
        # Load the original image
        with Image.open(img_path) as im:
            original_image = np.array(im)
        
        # Load the Voronoi noise image
        noise_image_path = "img/noise.png"
        with Image.open(noise_image_path) as im:
            noise_image = np.array(im)

        green_color = [0, 255, 0]  # Green
        land_mask:list[(int,int)]=[]
        # Iterate through the pixels of the original image
        for xpix in range(original_image.shape[0]):
            for ypix in range(original_image.shape[1]):
                if np.array_equal(original_image[xpix, ypix], green_color):
                    land_mask.append((xpix,ypix))
                    # If the pixel in the original image is green
                    # Mix the Voronoi color with the green color
                    voronoi_color = noise_image[xpix, ypix]
                    
                    # Adjust the Voronoi color to make it more green
                    # You can change the values here to make it more green
                    voronoi_color[1] = min(255, voronoi_color[1] + 80)  # Increase green channel
                    
                    mixed_color = ((original_image[xpix, ypix]*2) + (voronoi_color)) // 2
                    original_image[xpix, ypix] = mixed_color
        self.__outline=list.copy(land_mask)
        # Save the modified image to the original path
        modified_image = Image.fromarray(original_image)
        modified_image.save(img_path)
        
    def save_color_blocks(self):
        img_path = self.map_path()

        # Load the original image
        with Image.open(img_path) as im:
            original_image = np.array(im)

        # Create a mask for non-black/white pixels
        non_bw_mask = np.any((original_image != 0) & (original_image != 255), axis=-1)

        # Label connected components in the mask
        labeled_mask, num_features = ndimage.label(non_bw_mask)

        # Create a directory to save the color blocks
        os.makedirs("color_blocks", exist_ok=True)

        # Iterate through each labeled feature
        for i in range(1, num_features + 1):
            # Create a mask for the current feature
            feature_mask = labeled_mask == i

            # Apply the feature mask to the original image
            color_block = np.zeros_like(original_image)
            color_block[feature_mask] = original_image[feature_mask]

            # Create an image from the color block
            color_block_image = Image.fromarray(color_block)

            # Save the color block image to a file
            block_path = os.path.join("color_blocks", f"color_block_{i}.png")
            color_block_image.save(block_path)

    def split_color_block_by_color(self, image_path="color_blocks/color_block_1.png"):
        with Image.open(image_path) as im:
            color_block_image = np.array(im)

        unique_colors = np.unique(color_block_image.reshape(-1, color_block_image.shape[2]), axis=0)
        split_blocks_dir = "split_color_blocks"
        os.makedirs(split_blocks_dir, exist_ok=True)

        for i, color in enumerate(unique_colors):
            color_mask = np.all(color_block_image == color, axis=-1)
            labeled_mask, num_features = ndimage.label(color_mask)

            for j in range(1, num_features + 1):
                feature_mask = labeled_mask == j
                if np.sum(feature_mask) < 200:  # Check if the area is less than 200 pixels
                    continue
                
                split_color_area = np.zeros((color_block_image.shape[0], color_block_image.shape[1], 4), dtype=np.uint8)

                # Set the RGB values
                split_color_area[feature_mask, :3] = color_block_image[feature_mask]
                
                # Set the alpha channel to 255 for the colored region
                split_color_area[feature_mask, 3] = 255
                
                split_area_image = Image.fromarray(split_color_area)

                block_path = os.path.join(split_blocks_dir, f"split_block_{i}_area_{j}.png")
                split_area_image.save(block_path)


    """
    # Superceeded flood-fill
    def flood_fill_centre(self):
        image_blob = None
        with Image.open(self.map_path()) as image:
            image_blob = np.array(image)
        
        x, y, _ = image_blob.shape
        x_center, y_center = x // 2, y // 2
        i=0
        unfilled_pixels:list[int,int]=[]
        unfilled_pixels.append((x_center, y_center))
        while(len(unfilled_pixels)>0):
            print(len(unfilled_pixels))
            # first, iterate through all nearest-neighbours, and add any that arent green
            pixels_to_add:list[int,int]=[]
            for pixel in unfilled_pixels:
                xpix,ypix=pixel
                expressions=[(xpix-1,ypix),(xpix+1,ypix),(xpix,ypix-1),(xpix,ypix+1)]
                for expression in expressions:
                    xex,yex=expression
                    if ((xex,yex) not in unfilled_pixels):
                        if((xex >= 0 and xex<x) and (yex >= 0 and yex<y)):
                            if(not np.array_equal(image_blob[(xex,yex)],[0,255,0])):
                                pixels_to_add.append(expression)
            unfilled_pixels.extend(pixels_to_add)
            a=len(pixels_to_add)
            pixels_to_add.clear()
            modified_image = Image.fromarray(image_blob)
            if(i%200==0):
                modified_image.save("img/output_image"+str(i)+".png")
            i+=1
            print(f"{len(pixels_to_add)} {a}")
            if len(unfilled_pixels) != 0:
                for pixel in unfilled_pixels:
                    xpix, ypix = pixel
                    image_blob[(xpix, ypix)] = [0, 255, 0]
                    unfilled_pixels.remove((xpix, ypix))

        # Optionally, you can save the modified image
        modified_image = Image.fromarray(image_blob)
        modified_image.save("output_image.png")"""

Island()