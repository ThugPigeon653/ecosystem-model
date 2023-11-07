import matplotlib.pyplot as plt
import json
from matplotlib.cm import get_cmap

with open('logs/animal_counts_by_year.json', 'r') as json_file:
    animal_counts = json.load(json_file)
regions = list(animal_counts['0'].keys())
for i in range(len(regions)):
    if '_' in regions[i]:
        regions[i] = regions[i].split('_')[1]
animals = list(animal_counts['0'][regions[0]].keys())
cmap = get_cmap('tab20')  
colors = cmap(range(len(animals)))
for region in regions:
    fig, ax = plt.subplots()
    ax.set_title(f'Region {region}')
    ax.set_xlabel('Day')
    ax.set_ylabel('Count')
    for idx, animal_type in enumerate(animals):
        counts = [animal_counts[day][region][animal_type] for day in animal_counts.keys()]
        ax.plot(list(animal_counts.keys()), counts, label=animal_type, color=colors[idx])
    ax.legend(loc='upper right')
    plt.savefig(f"logs/{region}_graph.png")
    
