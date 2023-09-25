import sqlite3
import json
import random
import os

if os.path.exists('animal_database.db'):
    os.remove('animal_database.db')
conn = sqlite3.connect('animal_database.db')


class Terrain:
    def __init__(self):
        self.cursor = conn.cursor()
        self.cursor.execute('''
            CREATE TABLE terrain (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                temperature REAL,
                precipitation REAL,
                vegetation_density REAL,
                terrain_type TEXT,
                animal_population TEXT,
                area REAL
            )
        ''')
        conn.commit()

    def create_new_terrain(self, name, temperature, precipitation, vegetation_density, terrain_type, animal_population, area):
        animal_population_json = json.dumps(animal_population) if animal_population is not None else None
        self.cursor.execute('''
            INSERT INTO terrain (name, temperature, precipitation, vegetation_density, terrain_type, animal_population, area)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, temperature, precipitation, vegetation_density, terrain_type, animal_population_json, area))
        conn.commit()
        return self.cursor.lastrowid

    def get_terrain_attributes(self, terrain_id):
        self.cursor.execute('SELECT * FROM terrain WHERE id = ?', (terrain_id,))
        terrain_data = self.cursor.fetchone()
        if terrain_data:
            id, name, temperature, precipitation, vegetation_density, terrain_type, animal_population_json, area = terrain_data

            animal_population = json.loads(animal_population_json) if animal_population_json else None

            return {
                'id': id,
                'name': name,
                'temperature': temperature,
                'precipitation': precipitation,
                'vegetation_density': vegetation_density,
                'terrain_type': terrain_type,
                'animal_population': animal_population
            }
        else:
            return None

class Animals:

    __this_year:int=0

    def __init__(self):
        self.cursor = conn.cursor()
        self.cursor.execute('''
            CREATE TABLE animals (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                num_legs INTEGER,
                eye_size REAL,
                mouth_size REAL,
                weight REAL,
                energy_capacity REAL,
                endurance REAL,
                num_teeth INTEGER,
                avg_old_age REAL,
                old_age REAL,
                breeding_lifecycle REAL,
                eye_injury INTEGER,
                leg_injury INTEGER,
                mouth_injury INTEGER,
                general_injury INTEGER,
                prey_relationships TEXT,
                terrain_id INTEGER,
                birth_rate REAL,
                litter_size INTEGER,
                born INTEGER,
                ear_size REAL,
                ear_injury INTEGER
            )
        ''')
        conn.commit()

    @property
    def this_year(self):
        return self.__this_year
    
    @this_year.setter
    def this_year(self, year):
        self.__this_year=year


    def create_new_animal(self, name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance,
                          num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships,
                          terrain_id, birth_rate, litter_size, born, ear_size, ear_injury):
        self.cursor.execute('''
            INSERT INTO animals (name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance,
            num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ear_injury)
        ''', (name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age,
              old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, json.dumps(prey_relationships), terrain_id, birth_rate, litter_size, born, ear_size, ear_injury))

        conn.commit()
        return self.cursor.lastrowid

    def get_animal_attributes(self, animal_id):
        self.cursor.execute('SELECT * FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        if animal_data:
            id, name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships_json, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury = animal_data

            prey_relationships = json.loads(prey_relationships_json) if prey_relationships_json else None

            return {
                'id': id,
                'name': name,
                'num_legs': num_legs,
                'eye_size': eye_size,
                'mouth_size': mouth_size,
                'weight': weight,
                'energy_capacity': energy_capacity,
                'endurance': endurance,
                'num_teeth': num_teeth,
                'avg_old_age': avg_old_age,
                'old_age': old_age,
                'breeding_lifecycle': breeding_lifecycle,
                'injuries': {
                    'eye_injury': eye_injury,
                    'leg_injury': leg_injury,
                    'mouth_injury': mouth_injury,
                    'general_injury': general_injury
                },
                'prey_relationships': prey_relationships,
                'terrain_id': terrain_id,
                'birth_rate': birth_rate,
                'litter_size': litter_size,
                'born':born,
                'ear_size':ear_size,
                'ear_injury':ear_injury
            }
        else:
            return None
    
    def combine_prey_relationships(self, prey1, prey2):
        combined_prey = list(set(prey1) | set(prey2))
        return combined_prey
    
    @staticmethod
    def average(parent1_attr, parent2_attr):
        total = float(parent1_attr) + float(parent2_attr)
        total = total / 2
        if total % 1 == 0.5:
            if random.randint(0, 1) == 1:
                total = total + 0.5
            else:
                total = total - 0.5
        return total
    
    def create_child_animal(self, parent1_id, parent2_id):
        parent1_attributes = self.get_animal_attributes(parent1_id)
        parent2_attributes = self.get_animal_attributes(parent2_id)

        if parent1_attributes and parent2_attributes:
            child_attributes = {
                'name': f"Child of {parent1_attributes['name']} and {parent2_attributes['name']}",
                'num_legs': Animals.average(parent1_attributes['num_legs'], parent2_attributes['num_legs']),
                'eye_size': Animals.average(parent1_attributes['eye_size'] , parent2_attributes['eye_size']),
                'mouth_size': Animals.average(parent1_attributes['mouth_size'] , parent2_attributes['mouth_size']),
                'weight': Animals.average(parent1_attributes['weight'] , parent2_attributes['weight']),
                'energy_capacity': Animals.average(parent1_attributes['energy_capacity'] , parent2_attributes['energy_capacity']),
                'endurance': Animals.average(parent1_attributes['endurance'] + parent2_attributes['endurance']),
                'num_teeth': int(Animals.average(parent1_attributes['num_teeth'] , parent2_attributes['num_teeth'])),
                'avg_old_age': Animals.average(parent1_attributes['avg_old_age'] , parent2_attributes['avg_old_age']),
                'old_age': Animals.average(parent1_attributes['old_age'] , parent2_attributes['old_age']),
                'breeding_lifecycle': Animals.average(parent1_attributes['breeding_lifecycle'] , parent2_attributes['breeding_lifecycle']),
                'injuries': None, 
                'prey_relationships': self.combine_prey_relationships(parent1_attributes['prey_relationships'], parent2_attributes['prey_relationships']),
                'terrain_id': parent1_attributes['terrain_id'],
                'birth_rate': Animals.average(parent1_attributes['birth_rate'] , parent1_attributes['birth_rate']),
                'litter_size': Animals.average(parent1_attributes['litter_size'] , parent2_attributes['litter_size']),
                'born':self.this_year,
                'ear_size':Animals.average(parent1_attr=['ear_size'],parent2_attr=['ear_size']),
            }

            self.create_new_animal(**child_attributes)

            return f"Child animal created with ID {self.cursor.lastrowid}"
        else:
            return "Failed to create child animal: Parent animals not found"
    
    def get_all_animals(self):
        self.cursor.execute('SELECT * FROM animals')
        all_animals = self.cursor.fetchall()

        animals_list = []
        for animal_data in all_animals:
            id, name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships_json, terrain_id, birth_rate, litter_size, born, ear_size = animal_data

            prey_relationships = json.loads(prey_relationships_json) if prey_relationships_json else None

            animal = {
                'id': id,
                'name': name,
                'num_legs': num_legs,
                'eye_size': eye_size,
                'mouth_size': mouth_size,
                'weight': weight,
                'energy_capacity': energy_capacity,
                'endurance': endurance,
                'num_teeth': num_teeth,
                'avg_old_age': avg_old_age,
                'old_age': old_age,
                'breeding_lifecycle': breeding_lifecycle,
                'injuries': {
                    'eye_injury': eye_injury,
                    'leg_injury': leg_injury,
                    'mouth_injury': mouth_injury,
                    'general_injury': general_injury
                },
                'prey_relationships': prey_relationships,
                'terrain_id': terrain_id,
                'birth_rate': birth_rate,
                'litter_size': litter_size,
                'born':born,
                'ear_size':ear_size
            }
            animals_list.append(animal)

        return animals_list

    def get_age_modifier(self, animal_id)->float:
        self.cursor.execute('SELECT old_age, born FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        old_age, born = animal_data
        mid_age=old_age/2
        current_age=self.this_year-born
        # if theyre younger...
        if(self.this_year<=(old_age/2)+born):
            modifier:float=current_age/mid_age
        else:
            modifier:float=(old_age-current_age)/mid_age
        # This buffer has been added to flatten each end of the double-gradient. This is because young animals
        # still have partial capabilities due to their parents. Older animals will become as ineffective as 
        # an infant, but have learned enough by now to partially compensate for their physical incapabilities.
        # Without this modifier, infants and elderly would be guaranteed death. 
        if modifier<0.15:
            modifier=0.15
        return modifier

    def get_distance_travelled_in_day(self, animal_id)->float:
        self.cursor.execute('SELECT eye_size, weight, endurance, terrain_id FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        eye_size, weight, endurance, terrain_id = animal_data
        self.cursor.execute('SELECT vegetation_density from terrain WHERE id = ?', terrain_id)
        vegetation=self.cursor.fetchone()[0]
        distance=weight*endurance*0.4*eye_size*self.get_age_modifier(animal_id)/(1+vegetation)
        return distance
    
    def get_species(self, animal_id):
        self.cursor.execute('SELECT name FROM Animals WHERE id = ?', (animal_id,))
        return self.cursor.fetchone()[0]

    def get_land_covered_in_day(self, animal_id)->float:
        self.cursor.execute('SELECT eye_size, ear_size from Animals WHERE id = ?', (animal_id,))
        eye_size, eye_injury, ear_size, ear_injury=self.cursor.fetchone()
        distance:float=self.get_distance_travelled_in_day(animal_id)
        search_radius=max(ear_size/((1-ear_injury)/10), eye_size((1-eye_injury)/10))
        return distance*search_radius

    def get_encounter_odds_in_day(self, animal_id) -> float:
        self.cursor.execute('SELECT terrain_id FROM Animals WHERE id = ?', (animal_id,))
        terrain_id = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT area FROM Terrain WHERE id = ?', (terrain_id,))
        terrain_area = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT count(*) FROM Animals WHERE terrain_id = ?', (terrain_id,))
        animal_count = self.cursor.fetchone()[0]
        population_density = animal_count / terrain_area
        land_covered = self.get_land_covered_in_day(animal_id)
        return population_density*land_covered

    def get_encounters_in_day(self, animal_id:int)->list[int]:
        self.cursor.execute('SELECT terrain_id FROM Animals WHERE id = ?', (animal_id,))
        terrain_id=self.cursor.fetchone()[0]
        odds=self.get_encounter_odds_in_day(animal_id)
        luck_factor=random.uniform(0.10, 1.90)
        odds=odds*luck_factor
        discreet_encounters:int=int(odds)
        self.cursor.execute('SELECT id from Animals WHERE terrain_id = ? AND id != ? ORDER BY RANDOM() LIMIT ?',(terrain_id, animal_id, discreet_encounters))
        animals_encountered:list[int]=self.cursor.fetchall()
        return animals_encountered

    def does_see_animal(self, predator_id:int, prey_id:int)->(bool, bool):
        self.cursor.execute('SELECT eye_size, weight, old_age, eye_injury, leg_injury, mouth_injury, general_injury, terrain_id, born, ear_size from Animals WHERE id = ?', predator_id)
        predator_eye_size, predator_weight, predator_old_age, predator_eye_injury, predator_leg_injury, general_injury, terrain_id, born, ear_size=self.cursor.fetchone()

## EXAMPLE USAGE ##

# Creating a Terrain
terrain_manager = Terrain()
terrain_manager.create_new_terrain(
    name="Forest",
    temperature=25.0,
    precipitation=100.0,
    vegetation_density=0.8,
    terrain_type="Forest",
    animal_population=["Deer", "Bear", "Wolf"],
    area=250
)

# Creating Animals in the Forest
animal_manager = Animals()

# Creating a Deer in the Forest
animal_manager.create_new_animal(
    name="Deer",
    num_legs=4,
    eye_size=5.0,
    mouth_size=3.0,
    weight=150.0,
    energy_capacity=800.0,
    endurance=50.0,
    num_teeth=32,
    avg_old_age=8.0,
    old_age=10.0,
    breeding_lifecycle=2.0,
    eye_injury=0,  # 0 indicates no eye injury
    leg_injury=0,  # 0 indicates no leg injury
    mouth_injury=0,  # 0 indicates no mouth injury
    general_injury=0,  # 0 indicates no general injury
    prey_relationships=["Grass"],
    terrain_id=1, 
    birth_rate=1,
    litter_size=4,
    born=0,
    ear_size=4,
    ear_injury=0
)

# Creating a Wolf in the Forest
wolf_bear_id=animal_manager.create_new_animal(
    name="Wolf",
    num_legs=4,
    eye_size=6.0,
    mouth_size=4.0,
    weight=80.0,
    energy_capacity=1000.0,
    endurance=60.0,
    num_teeth=42,
    avg_old_age=7.0,
    old_age=9.0,
    breeding_lifecycle=3.0,
    eye_injury=0,  # 0 indicates no eye injury
    leg_injury=0,  # 0 indicates no leg injury
    mouth_injury=0,  # 0 indicates no mouth injury
    general_injury=0,  # 0 indicates no general injury
    prey_relationships=["Deer"],
    terrain_id=1, 
    birth_rate=0.5,
    litter_size=2,
    born=0,
    ear_size=4,
    ear_injury=0
)

# Creating a Bear in the Forest
animal_manager.create_new_animal(
    name="Bear",
    num_legs=4,
    eye_size=7.0,
    mouth_size=5.0,
    weight=250.0,
    energy_capacity=1200.0,
    endurance=70.0,
    num_teeth=38,
    avg_old_age=12.0,
    old_age=15.0,
    breeding_lifecycle=5.0,
    eye_injury=0,  # 0 indicates no eye injury
    leg_injury=0,  # 0 indicates no leg injury
    mouth_injury=0,  # 0 indicates no mouth injury
    general_injury=0,  # 0 indicates no general injury
    prey_relationships=["Deer"],
    terrain_id=1, 
    birth_rate=0.2,
    litter_size=1,
    born=0,
    ear_size=4,
    ear_injury=0
)

# Creating a Child Animal in the Forest (Hybrid of Wolf and Bear)
animal_manager.create_child_animal(parent1_id=3, parent2_id=4)  

# Retrieving Animal Attributes
deer_attributes = animal_manager.get_animal_attributes(1)
wolf_attributes = animal_manager.get_animal_attributes(2)
bear_attributes = animal_manager.get_animal_attributes(3)
child_attributes = animal_manager.get_animal_attributes(5)  

# Retrieving Terrain Attributes
forest_attributes = terrain_manager.get_terrain_attributes(1)

print(animal_manager.get_encounter_odds_in_day(wolf_bear_id))
enconters_for_animal=animal_manager.get_encounters_in_day(wolf_bear_id)
for encounter in enconters_for_animal:
    print(animal_manager.get_species(encounter[0]))