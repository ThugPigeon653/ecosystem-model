#TODO: 
# - vegetation reinforcement and supply
# - add current energy (as well as the existing max energy) to animals. 
# - reduce energy every day - increase for feeding - dont attack if not hungry
# - work in the effects of hunger

import json
import random
import os
from db_connection import Connection
import logger as log
from logger import logging 

logger=log.MyLogger('ecosystem.txt')

if os.path.exists('animal_database.db'):
    os.remove('animal_database.db')
conn = Connection.get_connection()

class Pregnancy:
    def __init__(self):
        self.cursor = conn.cursor()
        self.cursor.execute('DROP TABLE IF EXISTS pregnancy')
        self.cursor.execute('''
            CREATE TABLE pregnancy (
                mother_id INTEGER NOT NULL,
                father_id INTEGER NOT NULL,
                expiry INTEGER NOT NULL,
                PRIMARY KEY(mother_id)
            )
        ''')
        conn.commit()

    def insert_pregnancy(self, mother_id:int, father_id:int, today):
        self.cursor.execute('SELECT weight, birth_rate FROM animals WHERE id = ?', (mother_id,))
        weight, birth_rate=self.cursor.fetchone()
        expiry=int(((0.8*weight)+today)/(birth_rate))
        self.cursor.execute('''
            INSERT INTO pregnancy (mother_id, father_id, expiry)
            VALUES (?, ?, ?)
        ''', (mother_id, father_id, expiry))
        conn.commit()
        return self.cursor.lastrowid
    
    def is_able_to_conceive(self, animal_id:int, today:int):
        self.cursor.execute('SELECT breeding_lifecycle, old_age, born, is_male FROM Animals WHERE id = ?', (animal_id,))
        breeding_lifecycle, old_age, born, is_male=self.cursor.fetchone()
        can_breed:bool=False
        if(((breeding_lifecycle*old_age)+born)<=today):
            if(is_male):
                can_breed=True
            else:
                self.cursor.execute('SELECT expiry FROM pregnancy WHERE mother_id = ?', (animal_id,))
                exp=self.cursor.fetchone()
                if(exp!= None):
                    expiry:int=exp[0]
                else:
                    expiry=None
                if(expiry!=None):
                    if(expiry<today):
                        self.cursor.execute('DELETE FROM pregnancy WHERE mother_id = ?',(animal_id,))
                        can_breed=True
                else:
                    can_breed=True
        return can_breed
    
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
                area REAL,
                color TEXT
            )
        ''')
        conn.commit()

    def create_new_terrain(self, name, temperature, precipitation, vegetation_density, terrain_type, area, color):
        self.cursor.execute('''
            INSERT INTO terrain (name, temperature, precipitation, vegetation_density, terrain_type, area)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, temperature, precipitation, vegetation_density, terrain_type, area))
        conn.commit()
        return self.cursor.lastrowid

    def get_terrain_attributes(self, terrain_id):
        self.cursor.execute('SELECT * FROM terrain WHERE id = ?', (terrain_id,))
        terrain_data = self.cursor.fetchone()
        if terrain_data:
            id, name, temperature, precipitation, vegetation_density, terrain_type, area = terrain_data

            return {
                'id': id,
                'name': name,
                'temperature': temperature,
                'precipitation': precipitation,
                'vegetation_density': vegetation_density,
                'terrain_type': terrain_type,
                'area': area
            }
        else:
            return None

class Animals:
    __migration:float=1
    __savagery:int=10
    __birth_tuner:int=100 # percentage_value
    __today:int=0
    __pregnancy_manager:Pregnancy

    def __init__(self):
        self.cursor = conn.cursor()
        self.cursor.execute('''
            CREATE TABLE animals (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                relative_strength INTEGER,
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
                ear_injury INTEGER,
                survival_days INTEGER CHECK(survival_days!=0),
                food_intake INTEGER,
                energy REAL,
                is_male BOOL CHECK(is_male=True or is_male=False)
            )
        ''')
        conn.commit()

    @property
    def today(self):
        return self.__today
    @today.setter
    def today(self, year):
        self.__today=year

    @property
    def birth_tuner(self)->int:
        return self.__birth_tuner
    @birth_tuner.setter
    def birth_tuner(self, setting:int)->None:
        self.__birth_tuner=setting

    @property
    def migration(self)->float:
        return self.__migration
    @migration.setter
    def migration(self, setting:float)->None:
        self.__migration=setting

    @property
    def savagery(self)->int:
        return self.__savagery
    @savagery.setter
    def savagery(self, setting:int)->None:
        self.__savagery=setting

    @property
    def pregnancy_manager(self):
        return self.__pregnancy_manager
    @pregnancy_manager.setter
    def pregnancy_manager(self, pregnancy:Pregnancy):
        self.__pregnancy_manager=pregnancy

    def create_new_animal(self, name:str, relative_strength:int, eye_size:float, mouth_size:float, weight:float, energy_capacity:float, endurance:float,
                          num_teeth:int, avg_old_age:float, old_age:float, breeding_lifecycle:float, eye_injury:int, leg_injury:int, mouth_injury:int, general_injury:int, prey_relationships:list[str],
                          terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, survival_days:int, food_intake:int, energy:float, is_male:bool=None):
        if(is_male==None):
            is_male=random.choice([True, False])
        self.cursor.execute('''
            INSERT INTO animals (name, relative_strength, eye_size, mouth_size, weight, energy_capacity, endurance,
            num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, survival_days, food_intake, energy, is_male)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, relative_strength, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age,
              old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, json.dumps(prey_relationships), terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, survival_days,
               food_intake, energy, is_male))

        conn.commit()
        logger.log("Created "+name+" ("+str(self.cursor.lastrowid)+")\033[0m", logging.INFO)
        return self.cursor.lastrowid

    def get_animal_attributes(self, animal_id):
        self.cursor.execute('SELECT * FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        if animal_data:
            id, name, relative_strength, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships_json, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, survival_days, food_intake, energy, is_male = animal_data

            prey_relationships = json.loads(prey_relationships_json) if prey_relationships_json else None

            return {
                'id': id,
                'name': name,
                'relative_strength': relative_strength,
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
                'ear_injury':ear_injury,
                'survival_days':survival_days,
                'food_intake':food_intake,
                'energy':energy, 
                'is_male':is_male
            }
        else:
            return None
    
    def combine_prey_relationships(self, prey1, prey2):
        combined_prey = list(set(prey1) | set(prey2))
        return combined_prey
    
    @staticmethod
    def average(parent1_attr, parent2_attr):
        try:
            total:float = float(parent1_attr) + float(parent2_attr)
            total = total / 2.00
            if(type(parent1_attr)==float):
                return total
            else:
                return int(total)
        except:
            return None
    
    def delete_animal(self, animal_id:int):
        self.cursor.execute('DELETE FROM Animals WHERE id = ?', (animal_id,))

    def create_child_animal(self, parent1_id:int, parent2_id:int, is_parent1_male:bool):
        parent1_attributes = self.get_animal_attributes(parent1_id)
        parent2_attributes = self.get_animal_attributes(parent2_id)
        if(is_parent1_male):
            p1=parent2_id
            p2=parent1_id
        else:
            p1=parent1_id
            p2=parent2_id
        litter_size=parent1_attributes['litter_size']
        self.__pregnancy_manager.insert_pregnancy(p1, p2, self.__today)
        if parent1_attributes and parent2_attributes:
            while litter_size>0:
                is_male=random.choice([True, False])
                weight=Animals.average(parent1_attributes['weight'] , parent2_attributes['weight'])
                weight_offset=(random.uniform(0.001, 0.300)*weight)
                if(is_male):
                    weight+=weight_offset
                else:
                    weight-=weight_offset 
                    child_attributes = {
                        'name': parent1_attributes['name'],
                        'relative_strength': Animals.average(parent1_attributes['relative_strength'], parent2_attributes['relative_strength']),
                        'eye_size': Animals.average(parent1_attributes['eye_size'] , parent2_attributes['eye_size']),
                        'mouth_size': Animals.average(parent1_attributes['mouth_size'] , parent2_attributes['mouth_size']),
                        'weight': weight,
                        'energy_capacity': Animals.average(parent1_attributes['energy_capacity'] , parent2_attributes['energy_capacity']),
                        'endurance': Animals.average(parent1_attributes['endurance'] , parent2_attributes['endurance']),
                        'num_teeth': int(Animals.average(parent1_attributes['num_teeth'] , parent2_attributes['num_teeth'])),
                        'avg_old_age': Animals.average(parent1_attributes['avg_old_age'] , parent2_attributes['avg_old_age']),
                        'old_age': Animals.average(parent1_attributes['old_age'] , parent2_attributes['old_age']),
                        'breeding_lifecycle': Animals.average(parent1_attributes['breeding_lifecycle'] , parent2_attributes['breeding_lifecycle']),
                        'eye_injury': 0, 
                        'leg_injury':0,
                        'mouth_injury':0,
                        'general_injury':0,
                        'prey_relationships': self.combine_prey_relationships(parent1_attributes['prey_relationships'], parent2_attributes['prey_relationships']),
                        'terrain_id': parent1_attributes['terrain_id'],
                        'birth_rate': Animals.average(parent1_attributes['birth_rate'] , parent1_attributes['birth_rate']),
                        'litter_size': Animals.average(parent1_attributes['litter_size'] , parent2_attributes['litter_size']),
                        'born':self.today,
                        'ear_size':Animals.average(parent1_attributes['ear_size'],parent2_attributes['ear_size']),
                        'ear_injury':0,
                        'survival_days':Animals.average(parent1_attributes['survival_days'],parent1_attributes['survival_days']),
                        'food_intake':Animals.average(parent1_attributes['survival_days'],parent1_attributes['survival_days']),
                        'energy':100, 
                        'is_male':is_male
                    }
                    leg_mutation = eye_mutation = teeth_mutation = 0
                    mouth_mutation = weight_mutation = energy_mutation = endurance_mutation = ear_mutation = 1
                    if(random.randint(0,2000)==0):
                        if(random.randint(0,1000)!=0):
                            if(random.choice([True, False])):
                                leg_mutation=-1
                            else:
                                leg_mutation=1
                        else:
                            if(random.choice([True, False])):
                                leg_mutation=-2
                            else:
                                leg_mutation=2
                    if(random.randint(0,3000)==0):
                        if(random.randint(0,1000)!=0):
                            if(random.choice([True, False])):
                                eye_mutation=-1
                            else:
                                eye_mutation=1
                        else:
                            if(random.choice([True, False])):
                                eye_mutation=-2
                            else:
                                eye_mutation=2
                    if(random.randint(0,300)==0):
                        if(random.randint(0,200)!=0):
                            if(random.choice([True, False])):
                                mouth_mutation=0.9
                            else:
                                mouth_mutation=1.1
                        else:
                            delta:float=random.uniform(0.00, 1.00)
                            if(random.choice([True, False])):
                                mouth_mutation=1+delta
                            else:
                                mouth_mutation=1-delta  
                    if(random.randint(0,400)==0):
                        if(random.randint(0,400)!=0):
                            if(random.choice([True, False])):
                                weight_mutation=0.9
                            else:
                                weight_mutation=1.1
                        else:
                            delta:float=random.uniform(0.00, 0.41)
                            if(random.choice([True, False])):
                                weight_mutation=1+delta
                            else:
                                weight_mutation=1-delta
                    if(random.randint(0,550)==0):
                        if(random.randint(0,750)!=0):
                            if(random.choice([True, False])):
                                energy_mutation=0.98
                            else:
                                energy_mutation=1.02
                        else:
                            delta:float=random.uniform(0.00, 0.1)
                            if(random.choice([True, False])):
                                energy_mutation=1+delta
                            else:
                                energy_mutation=1-delta  
                    if(random.randint(0,550)==0):
                        if(random.randint(0,750)!=0):
                            if(random.choice([True, False])):
                                endurance_mutation=0.98
                            else:
                                endurance_mutation=1.02
                        else:
                            delta:float=random.uniform(0.00, 0.1)
                            if(random.choice([True, False])):
                                endurance_mutation=1+delta
                            else:
                                endurance_mutation=1-delta
                    if(random.randint(0,600)==0):
                        if(random.randint(0,1000)!=0):
                            if(random.choice([True, False])):
                                teeth_mutation=-1
                            else:
                                teeth_mutation=1
                        else:
                            if(random.choice([True, False])):
                                teeth_mutation=-2
                            else:
                                teeth_mutation=2
                    if(random.randint(0,950)==0):
                        if(random.randint(0,1050)!=0):
                            if(random.choice([True, False])):
                                ear_mutation=0.98
                            else:
                                ear_mutation=1.02
                        else:
                            delta:float=random.uniform(0.00, 0.1)
                            if(random.choice([True, False])):
                                ear_mutation=1+delta
                            else:
                                ear_mutation=1-delta
                    child_attributes['relative_strength']+=leg_mutation
                    child_attributes['eye_size']+=eye_mutation
                    child_attributes['mouth_size']*=mouth_mutation
                    child_attributes['weight']*=weight_mutation
                    child_attributes['energy_capacity']*=energy_mutation
                    child_attributes['endurance']*=endurance_mutation
                    child_attributes['num_teeth']+=teeth_mutation
                    child_attributes['ear_size']*=ear_mutation
                    self.create_new_animal(**child_attributes)
                litter_size-=1
    
    def get_all_animals(self):
        self.cursor.execute('SELECT * FROM animals')
        all_animals = self.cursor.fetchall()

        animals_list = []
        for animal_data in all_animals:
            id, name, relative_strength, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships_json, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, survival_days, food_intake, energy, is_male = animal_data

            prey_relationships = json.loads(prey_relationships_json) if prey_relationships_json else None

            animal = {
                'id': id,
                'name': name,
                'relative_strength': relative_strength,
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
                    'general_injury': general_injury,
                    'ear_injury':ear_injury
                },
                'prey_relationships': prey_relationships,
                'terrain_id': terrain_id,
                'birth_rate': birth_rate,
                'litter_size': litter_size,
                'born':born,
                'ear_size':ear_size,
                'is_male':is_male
            }
            animals_list.append(animal)

        return animals_list

    def get_age_modifier(self, animal_id)->float:
        self.cursor.execute('SELECT old_age, born FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        old_age, born = animal_data
        mid_age=old_age/2
        current_age=self.today-born
        # if theyre younger...
        if(self.today<=(old_age/2)+born):
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
        self.cursor.execute('SELECT vegetation_density from terrain WHERE id = ?', (terrain_id,))
        vegetation=self.cursor.fetchone()[0]
        distance=weight*endurance*0.4*eye_size*self.get_age_modifier(animal_id)/(1+vegetation)
        return distance
    
    def get_species(self, animal_id):
        self.cursor.execute('SELECT name FROM Animals WHERE id = ?', (animal_id,))
        return self.cursor.fetchone()[0]

    def get_land_covered_in_day(self, animal_id)->float:
        self.cursor.execute('SELECT eye_size, eye_injury, ear_size, ear_injury from Animals WHERE id = ?', (animal_id,))
        eye_size, eye_injury, ear_size, ear_injury=self.cursor.fetchone()
        distance:float=self.get_distance_travelled_in_day(animal_id)
        search_radius=max(ear_size/((1-ear_injury)/10), eye_size/((1-eye_injury)/10))
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
        terran_tuple=self.cursor.fetchone()
        animals_encountered:list[int]=[]
        if(terran_tuple!=None):
            terrain_id=terran_tuple[0]
            odds=self.get_encounter_odds_in_day(animal_id)
            luck_factor=random.uniform(0.10, 1.90)
            odds=odds*luck_factor
            discreet_encounters:int=int(odds)
            self.cursor.execute('SELECT id from Animals WHERE terrain_id = ? AND id != ? ORDER BY RANDOM() LIMIT ?',(terrain_id, animal_id, discreet_encounters))
            animals_encountered=self.cursor.fetchall()
        return animals_encountered

    def get_does_see_animal(self, predator_id:int, prey_id:int)->(bool, bool):
        self.cursor.execute('SELECT eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury from Animals WHERE id = ?', (predator_id,))
        eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury=self.cursor.fetchone()
        terrain_density=self.cursor.execute('SELECT vegetation_density from terrain WHERE id = ?', terrain_id)
        predator_defense_score:float=((((eye_size*((10-eye_injury)/10)+(ear_size*((10-ear_injury)/10)))-((10-leg_injury)/10)*1.1)-(weight/1000))/(1+terrain_density))
        predator_offense_score:float=predator_defense_score*((10-general_injury)/10)

        self.cursor.execute('SELECT eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury from Animals WHERE id = ?', (prey_id,))
        eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury=self.cursor.fetchone()
        prey_defense_score:float=(((eye_size*((10-eye_injury)/10)+(ear_size*((10-ear_injury)/10)))-((10-leg_injury)/10)*0.8)-(weight/1000))/(1+terrain_density)
        prey_offense_score:float=prey_defense_score*((10-general_injury)/10)
        predator_offense_score=random.uniform(0.000, predator_offense_score)
        prey_defense_score=random.uniform(0.000, prey_defense_score)
        if(predator_offense_score>prey_defense_score):
            prey_seen=True
        else:
            prey_seen=False
        predator_defense_score=random.uniform(0.000, predator_defense_score)
        prey_offense_score=random.uniform(0.000, prey_offense_score)
        if(prey_offense_score>predator_defense_score):
            predator_seen:bool=True
        else:
            predator_seen:bool=False
        return (prey_seen, predator_seen)

    def get_does_chase_animal(self, predator_id:int, prey_id:int)->bool:
        will_chase:bool=None
        if(predator_id!=None and prey_id!=None):
            self.cursor.execute('SELECT prey_relationships, weight FROM Animals WHERE id = ?', (predator_id,))
            result=self.cursor.fetchone()
            if(result!=None):
                prey_relationships, weight = result
                self.cursor.execute('SELECT name, weight FROM Animals WHERE id = ?', (prey_id,))
                animal_data=self.cursor.fetchone()
                if(animal_data!=None):
                    name,prey_weight=animal_data
                    if(name in prey_relationships.split(',')):
                        will_chase=True
                    else:
                        weight=random.uniform(0.000, weight)
                        prey_weight=random.uniform(0.000, prey_weight)
                        if(weight>prey_weight):
                            will_chase=True
                        else:
                            will_chase=False
        return will_chase

    def get_does_catch_animal(self, predator_id:int, prey_id:int)->bool:
        self.cursor.execute('SELECT relative_strength, weight, energy_capacity, endurance, leg_injury, general_injury, terrain_id FROM Animals WHERE id = ?', (predator_id,))
        relative_strength, weight, energy_capacity, endurance, leg_injury, general_injury, terrain_id=self.cursor.fetchone()
        self.cursor.execute('SELECT vegetation_density FROM terrain WHERE id = ?', (terrain_id,))
        vegetation_density=self.cursor.fetchone()[0]
        predator_score=((((relative_strength**0.5)*energy_capacity)/(weight*((22-leg_injury-general_injury)/20)))*endurance)/(1+vegetation_density)
        self.cursor.execute('SELECT relative_strength, weight, energy_capacity, endurance, leg_injury, general_injury FROM Animals WHERE id = ?', (prey_id,))
        relative_strength, weight, energy_capacity, endurance, leg_injury, general_injury = self.cursor.fetchone()
        try:
            prey_score=((((relative_strength**0.5)*energy_capacity)/(weight*((22-leg_injury-general_injury)/20)))*endurance)/(1+vegetation_density)
        except Exception as e:
            pass
        predator_score=random.uniform(predator_score/2.00, predator_score)
        prey_score=random.uniform(prey_score/2.00, prey_score)
        catches_prey:bool
        if(predator_score>prey_score):
            catches_prey=True
        else:
            catches_prey=False
        return catches_prey

    def list_prey(self, animal_id:str)->list[str]:
        self.cursor.execute('SELECT prey_relationships FROM Animals WHERE id = ?',(animal_id,))
        ans=self.cursor.fetchone()
        if ans!=None:
            return ans[0].replace(" ", "").split(',')
        else: 
            return None

    # some variables are accessed but not used here. They should be implemented fully
    def get_combat_outcome(self, predator_id:int, prey_id:int)->str:
        outcome:float=False
        return_value=None
        if(predator_id!=None and prey_id!=None):
            predator_age=self.get_age_modifier(predator_id)
            prey_age=self.get_age_modifier(prey_id)
            self.cursor.execute('SELECT name, relative_strength, mouth_size, weight, energy_capacity, endurance, num_teeth from Animals WHERE id = ?', (predator_id,))
            predator_name, relative_strength, mouth_size, weight, energy_capacity, endurance, num_teeth = self.cursor.fetchone()
            p_weight=weight
            predator_score:float = random.uniform(0.01, (relative_strength**0.5)*mouth_size*(num_teeth**1.1)*(endurance**0.9)*(energy_capacity**0.9)*(weight**0.5))
            self.cursor.execute('SELECT name, relative_strength, mouth_size, weight, energy_capacity, endurance, num_teeth from Animals WHERE id = ?', (prey_id,))
            prey_name, relative_strength, mouth_size, weight, energy_capacity, endurance, num_teeth = self.cursor.fetchone()
            prey_score:float = random.uniform(0.01, (relative_strength**0.55)*(mouth_size**0.9)*(num_teeth**0.9)*(endurance**1.1)*energy_capacity*(weight**0.5))
            outcome = predator_score-prey_score
            final_result=(outcome/predator_score)
            if(abs(final_result)>0.1 and abs(final_result)<7):
                injury_types=["eye", "leg", "mouth", "ear", "general"]
                injury_roll=random.randint(0, len(injury_types)-1)
                if(predator_score>prey_score):
                    victim=prey_id
                else:
                    victim=predator_id
                column_name = injury_types[injury_roll] + "_injury"
                query = 'SELECT {} FROM Animals WHERE id = ?'.format(column_name)
                self.cursor.execute(query, (victim,))
                injury=self.cursor.fetchone()[0]
                if((injury+final_result)<10):
                    injury=injury+final_result
                else:
                    injury=10
                injury=int(injury*((100-random.randint(0, self.savagery))/100))
                column_name = injury_types[injury_roll] + "_injury"
                query = 'UPDATE Animals SET {} = ? WHERE id = ?'.format(column_name)
                self.cursor.execute(query, (injury, victim))
                return_value=("\n\033[93m"+str(victim)+ " has been injured\033[0m("+str(final_result))
            elif(abs(outcome)>=0.7):
                if(random.randint(0,100)<=self.savagery):
                    killed_mass=0
                    if(outcome>0):
                        victim=prey_id
                        victor=predator_id
                        if(weight<=self.get_animal_current_hunger_for_kg(victim)):
                            self.delete_animal(victim)
                            return_value  ="Killed"
                            killed_mass=weight
                    else:
                        victim=predator_id
                        victor=prey_id
                        if(p_weight<=self.get_animal_current_hunger_for_kg(victim)):
                            self.delete_animal(victim)
                            return_value  ="Killed"
                            killed_mass=p_weight
                    if(killed_mass!=0):
                        prey:list[str]=self.list_prey(victor)
                        self.cursor.execute('SELECT name FROM Animals WHERE id=?',(victim,))
                        if(self.cursor.fetchone() in prey):
                            self.cursor.execute('SELECT survival_days, weight, food_intake, energy, prey_relationships FROM Animals WHERE id =?', (victor,))
                            sd,w,fi,e=self.cursor.fetchone()
                            daily_req=(fi/100)*w
                            e=min(100,e+(killed_mass/daily_req)*(sd/100))
                    return_value=("\n\033[91m"+str(victim)+ " has been killed\033[0m")
        return return_value

    def get_animal_current_hunger_for_kg(self, animal_id:int)->float:
        self.cursor.execute('SELECT survival_days, food_intake, energy, weight FROM Animals WHERE id = ?', (animal_id,))
        sd, fi, en, w = self.cursor.fetchone()
        return ((en)/(sd/100))*(w*fi)

    def execute_interaction(self, predator_id:int, prey_id:int):
        self.cursor.execute('SELECT name, is_male FROM Animals WHERE id = ?', (predator_id,))
        data=self.cursor.fetchone()
        outcome=None
        if(data!=None):
            predator_name, predator_is_male=data
            self.cursor.execute('SELECT name, is_male FROM Animals WHERE id = ?', (prey_id,))
            prey_name, prey_is_male=self.cursor.fetchone()
            status:str=f"No interaction eventuated between {predator_name} and {prey_name}. "
            logger.log(predator_name + " found a "+prey_name,logging.INFO)
            conception:bool=False
            protected_by_sexual_interest:bool=False
            if(predator_name==prey_name and predator_is_male!=prey_is_male and random.randint(0,100)<=self.birth_tuner):
                prey_can_conceive:bool=self.__pregnancy_manager.is_able_to_conceive(prey_id, self.__today)
                predator_can_conceive:bool=self.__pregnancy_manager.is_able_to_conceive(predator_id, self.__today)
                if(predator_can_conceive):
                    protected_by_sexual_interest=True
                    if(prey_can_conceive):
                        conception=True
            if(conception):
                self.create_child_animal(predator_id, prey_id, predator_is_male)
            elif(protected_by_sexual_interest!=True):
                chase_decision=(self.get_does_chase_animal(predator_id, prey_id),self.get_does_chase_animal(prey_id, predator_id))
                if(chase_decision==(True,True)):
                    status=f"A fight ensued between {predator_name} and {prey_name}"
                    outcome = self.get_combat_outcome(predator_id, prey_id)
                elif(chase_decision==(True,False)):
                    status=f"A chase ensued between {predator_name} and {prey_name}. "
                    if(self.get_does_catch_animal(predator_id, prey_id)):
                        status+="The animal was caught."
                        outcome=self.get_combat_outcome(predator_id, prey_id)
                    else:
                        status+="The animal got away."
                elif(chase_decision==(False, True)):
                    status=f"Prey fought back: {predator_name} and {prey_name}. "
                    if(self.get_does_catch_animal(prey_id, predator_id)):
                        status+= "successful catch"
                        outcome=self.get_combat_outcome(prey_id, predator_id)
                else:
                    status=None
        else:
            status=None
        if(outcome!=None):
            status+=outcome
        return status

    def get_feeding_order(self):
        self.cursor.execute('SELECT id FROM Animals ORDER BY RANDOM()')
        return self.cursor.fetchall()

    def get_energy_after_day_consumed(self, animal_id:int):
        self.cursor.execute('SELECT energy, survival_days FROM Animals where id=?', (animal_id,))
        energy, sd = self.cursor.fetchone()
        energy-=100/sd
        return energy

    def count_animals_by_type(self, animal_type, terrain_id):
        query = 'SELECT COUNT(*) FROM animals WHERE name = ? AND terrain_id = ?'
        self.cursor.execute(query, (animal_type, terrain_id))
        count = self.cursor.fetchone()[0]
        return count


def load_json_data(path):
    with open(path, "r") as json_data:
        data=json.load(json_data)
        return data

def initialize(test:bool=False):
    terrain_manager = Terrain()
    terrain_data = load_json_data("config/terrain.json")
    biomes: list[int] = []
    for terrain_name, terrain_attributes in terrain_data.items():
        logger.log(terrain_attributes, logging.info)
        terrain_id = terrain_manager.create_new_terrain(**terrain_attributes)
        biomes.append(terrain_id)
        with open('config/animals.json', 'r') as file:
            animals_dat = json.load(file)
            animals = list(animals_dat.keys())
    animal_counts = {f"{animal}_{terrain_id}": 0 for animal in animals for terrain_id in biomes}
    animal_counts_by_year = {}  

    animal_manager = Animals()
    animal_manager.pregnancy_manager = Pregnancy()
    animal_data = load_json_data("config/animals.json")
    for animal in animals:
        data = animal_data[animal]
        i = 0
        old_age=data["old_age"]
        lim=100
        if animal=="Crocodile" or animal=="Wolf":
            lim=50
        elif animal=="Rabbit" or animal=="Frog" or animal=="Deer" or animal=="Elephant":
            lim=300
        while i < lim:
            terrain_id = biomes[random.randint(0, len(biomes) - 1)]
            data["terrain_id"] = terrain_id
            data["energy"] = 100
            data["born"]=0-(random.randint(0,int(old_age)))
            animal_manager.create_new_animal(**data)
            i += 1

    i = 0
    with open('config/shared_runtime_config.json', 'r') as file:
        config = json.load(file)
        config["today"] = 0
    if test!=True:
        try:
            while i < 50:
                startvation:int=0
                gotkilled:int=0
                fromage:int=0
                animal_counts_by_year[i] = {}  # Create a dictionary for this year
                for terrain_id in biomes:
                    animal_counts_by_year[i][terrain_id] = {}  # Create a dictionary for this terrain_id
                    for animal_type in animals:
                        count = animal_manager.count_animals_by_type(animal_type, terrain_id)
                        animal_counts_by_year[i][terrain_id][animal_type] = count
                config["today"] = i
                with open('config/shared_runtime_config.json', 'w') as file:
                    json.dump(config, file, indent=4)
                animal_manager.today = i
                for animal_id in animal_manager.get_feeding_order():
                    cursor = conn.cursor()
                    cursor.execute('SELECT name, born, old_age FROM animals WHERE id = ?', animal_id)
                    vals = cursor.fetchone()
                    if vals is not None:
                        name, born, old_age = vals
                        energy = animal_manager.get_energy_after_day_consumed(animal_id[0])
                        cursor.execute("UPDATE Animals SET energy=? WHERE id=?", (energy, animal_id[0]))
                        if energy > 0:
                            if born + old_age <= i:
                                cursor.execute('DELETE FROM animals WHERE id = ?', animal_id)
                                fromage+=1
                            else:
                                encounters_for_animal = animal_manager.get_encounters_in_day(animal_id[0])
                                for encounter in encounters_for_animal:
                                    interaction = animal_manager.execute_interaction(animal_id[0], encounter[0])
                                    if interaction is not None:
                                        if("illed" in interaction):
                                            gotkilled+=1
                                        logger.log(str(i) + " " + interaction, logging.INFO)
                                if(random.randint(0,1000*int(len(encounters_for_animal)*animal_manager.migration))==0):
                                    new_terrain:int=biomes[random.randint(0,len(biomes)-1)]
                                    cursor.execute("UPDATE Animals SET terrain_id=? WHERE id=?", (new_terrain, animal_id[0]))
                                    try:
                                        if("Grass" in animal_manager.list_prey(animal_id[0])):
                                            cursor.execute("UPDATE Animals SET energy=? WHERE id=?", (100, animal_id[0]))
                                    except:
                                        print("Failed to get prey for "+name)
                        else:
                            cursor.execute('DELETE FROM animals WHERE id = ?', animal_id)
                            startvation+=1
                logger.log(animal_manager.get_all_animals(), logging.INFO)
                print(f"Year {i}   Eaten: {gotkilled}    OldAge: {fromage}    Starve: {startvation}")
                i += 1
        finally:
            print(f"Eaten: {gotkilled}    OldAge: {fromage}    Starve: {startvation}")
            conn.close()
            logger.log("Database connection closed.", logging.INFO)
            with open('logs/animal_counts_by_year.json', 'w') as counts_file:
                json.dump(animal_counts_by_year, counts_file, indent=4)
            print("Simulation complete")





