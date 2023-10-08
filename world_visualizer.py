import sqlite3
import json
import matplotlib.pyplot as plt

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

        print(animal_names)
        conn = sqlite3.connect('animal_database.db')
        print("Database connection established successfully.")
        
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Terrain')
        results = cursor.fetchall()
        for result in results:
            result=result[0]
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
    # Create a single figure for all terrains
    plt.figure(figsize=(8, 8))  # Adjust the figure size as needed
    
    for terrain_name, terrain_attributes in terrain_data.items():
        area = terrain_attributes.get("area", 0)
        color = terrain_attributes.get("color")
        
        # Create a square with an area proportional to the terrain's area
        size = int(area ** 0.5)
        
        # Plot the terrain on the same graph
        plt.gca().add_patch(plt.Rectangle((0, 0), size/10, size/10, color=color, label=terrain_name))
    
    # Set the legend for terrain names
    plt.legend()
    plt.axis('off')  # Turn off axis labels
    plt.show()

    
if __name__ == "__main__":
    terrain_data = load_json_data("terrain.json")
    visualize_terrain(terrain_data)