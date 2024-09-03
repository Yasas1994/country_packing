import pygame
import math  # Use the standard math module for trigonometry
from shapely import Polygon, MultiPolygon
import pickle as pkl
import numpy as np

# Initialize Pygame
pygame.init()

# Define the dimensions of the window
window_width = 900
window_height = 600
window = pygame.display.set_mode((window_width, window_height))

# Set the title of the window
pygame.display.set_caption("Pygame Example - Movable Objects")

polygons = pkl.load(open('country_packing/assets/polygons.pkl', 'rb'))

big_country_ = polygons["Germany"]
small_country_ = polygons["Denmark"]

# Set initial positions for the shapes
big_country_pos = [100, 100]  # Starting position of the rectangle
small_country_pos = [300, 100]   # Starting position of the triangle

# Define a clock to manage the frame rate
clock = pygame.time.Clock()

# Initialize rotation angle
rotation_angle = 0

# Define a function to rotate a polygon
def rotate_polygon(polygon, angle, center):
    """Rotate a polygon while keeping its center."""
    angle_rad = math.radians(angle)  # Convert angle to radians
    rotated_polygon = []
    for x, y in polygon:
        temp_x = x - center[0]
        temp_y = y - center[1]
        rotated_x = temp_x * math.cos(angle_rad) - temp_y * math.sin(angle_rad)
        rotated_y = temp_x * math.sin(angle_rad) + temp_y * math.cos(angle_rad)
        rotated_polygon.append((rotated_x + center[0], rotated_y + center[1]))
    return rotated_polygon

# Main loop
running = True
dragging = False


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check if the mouse is clicking inside the triangle
            if small_country_rect.collidepoint(mouse_x, mouse_y):
                dragging = True
                mouse_offset_x = small_country_rect.x - mouse_x
                mouse_offset_y = small_country_rect.y - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                small_country_pos[0] = mouse_x + mouse_offset_x
                small_country_pos[1] = mouse_y + mouse_offset_y

        elif event.type == pygame.MOUSEWHEEL:
            rotation_angle += 5  # Adjust rotation speed as needed

    # Clear the screen with a white background
    window.fill((255, 255, 255))

    # Define the rectangle as a polygon (big_country)
    big_country = [
        np.array(list(zip(big_country_.exterior.xy[0], big_country_.exterior.xy[1])))
    ]

    # Define the triangle as a polygon (small_country)
    small_country = [
        np.array(list(zip(small_country_.exterior.xy[0], small_country_.exterior.xy[1])))
    ]

    # Get the center of the triangle for rotation
    small_country_center = (
        small_country_.centroid.xy
    )

    # Rotate the triangle
    rotated_triangle = rotate_polygon(small_country, rotation_angle, small_country_center)

    # Draw the rectangle and the rotated triangle
    pygame.draw.polygon(window, (0, 0, 255), big_country)  # Blue rectangle
    pygame.draw.polygon(window, (255, 0, 0), rotated_triangle)  # Red triangle

    # Update the triangle's rect for collision detection
    small_country_rect = pygame.draw.polygon(window, (255, 0, 0), rotated_triangle, 1)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 30 FPS
    clock.tick(30)

# Quit Pygame
pygame.quit()
