import unittest
from unittest.mock import patch
import src.ecosystem as eco

class TestEcosystem(unittest.TestCase):
    def setUp(self):
        eco.initialize(True)

    def test_insert_pregnancy(self):
        pregnancy = eco.Pregnancy()
        result = pregnancy.insert_pregnancy(1, 2, 100)
        self.assertEqual(result,1)

    def test_insert_terrain(self):
        terrain=eco.Terrain()
        terrain_id=terrain.create_new_terrain("Tundra",10,5,12,"terrain-type", 1.1, "a-colour")
        self.assertEqual(terrain_id, 1)
        self.assertEqual(terrain.get_terrain_attributes(terrain_id)['name'], "Tundra")
        
if __name__ == '__main__':
    unittest.main()
