import matplotlib.pyplot as plt

def create_2d_creature(eye_size: float = 1, num_legs: int = 20, leg_gap: float = 0.02):
    if num_legs < 2:
        raise ValueError("The creature must have at least 2 legs.")
    
    fig, ax = plt.subplots()
    
    # Calculate the total width of the legs plus gaps
    total_width = num_legs * 0.05 + (num_legs - 1) * leg_gap
    
    # Calculate the initial horizontal position for the body
    initial_x = 0.5 - total_width / 2
    
    # Widen the body to accommodate the legs
    body_width = total_width + 0.1  # Adjust the body width as needed
    
    body = plt.Rectangle((initial_x - 0.05, 0.2), body_width, 0.5, color='green', fill=True)
    head = plt.Circle((0.5, 0.7), 0.2, color='blue', fill=True)
    
    left_eye = plt.Circle((0.35, 0.8), 0.05 * eye_size, color='white', fill=True)
    right_eye = plt.Circle((0.65, 0.8), 0.05 * eye_size, color='white', fill=True)
    left_pupil = plt.Circle((0.35, 0.8), 0.03 * eye_size, color='black', fill=True)
    right_pupil = plt.Circle((0.65, 0.8), 0.03 * eye_size, color='black', fill=True)
    
    mouth = plt.Rectangle((0.45, 0.55), 0.1, 0.05, color='red', fill=True)
    
    leg_positions = []
    legs = []
    
    for i in range(num_legs):
        x = initial_x + i * (0.05 + leg_gap)
        y = 0.05
        leg_positions.append((x, y))
    
    for x, y in leg_positions:
        legs.append(plt.Rectangle((x, y), 0.05, 0.2, color='brown', fill=True))
        
    for leg in legs:
        ax.add_patch(leg)
    ax.add_patch(body)
    ax.add_patch(head)
    ax.add_patch(left_eye)
    ax.add_patch(right_eye)
    ax.add_patch(left_pupil)
    ax.add_patch(right_pupil)
    ax.add_patch(mouth)

    
    ax.set_aspect('equal', adjustable='datalim')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    plt.show()

create_2d_creature(num_legs=2, leg_gap=0.02)
