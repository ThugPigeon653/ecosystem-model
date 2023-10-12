from PIL import Image, ImageDraw
import random
import math

def draw_ocean(self):
    for i in range(3):
        width, height = 1600, 1200
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # Draw chaotic ocean wave-like shapes
        for _ in range(4000):  # Increase the number of waves for chaos
            x = random.randint(0, width)
            y = random.randint(0, height)  # Allow waves at any height
            wave_size = random.randint(10, 60)  # Vary the size of the waves
            wave_color = (0, 0, random.randint(150, 255))  # Vary the shade of blue
            draw.ellipse((x, y, x + wave_size, y + wave_size), fill=wave_color)

        # Create a larger wavy distortion
        wavy_image = Image.new('RGB', (width, height))

        for x in range(width):
            for y in range(height):
                angle = math.sin(2 * math.pi * x / 60)  # Adjust the frequency and amplitude
                new_x = int(x + 20 * angle)
                if 0 <= new_x < width:
                    pixel = image.getpixel((new_x, y))
                    wavy_image.putpixel((x, y), pixel)

        # Create a larger distortion pattern
        def create_distortion_pattern(width, height):
            distortion_image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(distortion_image)

            for x in range(width):
                for y in range(height):
                    offset_x = int(10 * math.sin(2 * math.pi * x / 40))
                    offset_y = int(10 * math.sin(2 * math.pi * y / 40))
                    if 0 <= x + offset_x < width and 0 <= y + offset_y < height:
                        pixel = wavy_image.getpixel((x + offset_x, y + offset_y))
                        distortion_image.putpixel((x, y), pixel)

            return distortion_image

        # Create the larger distortion pattern
        distortion_pattern = create_distortion_pattern(width, height)

        # Overlay the distortion pattern on the larger wavy image
        result_image = Image.blend(wavy_image, distortion_pattern, alpha=0.5)

        # Save or display the final image
        result_image.save("img/ocean/"+i+'.png')
        result_image.show()

draw_ocean("1")
draw_ocean("2")
draw_ocean("3")