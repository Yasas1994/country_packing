import pygame
import math  # Use the standard math module for trigonometry
from shapely import Polygon, MultiPolygon
import pickle as pkl
import numpy as np
from  icecream import ic


def get_polygon(database, country):
    try:
        scaled_polygon = database[country]
        if isinstance(scaled_polygon, MultiPolygon):

            tmp = np.array([i.area for i in scaled_polygon.geoms])
            # norm_area = tmp/np.max(tmp)

            # for inx, geom in enumerate(scaled_polygon.geoms):
                # if norm_area[inx] > 0.05:

            geom = scaled_polygon.geoms[np.argmax(tmp)]
            x, y = geom.exterior.xy
            coords = np.array(list(zip(np.array(x), np.array(y)))) 
            ic(geom.centroid.xy)
            centroid = np.array([geom.centroid.xy[0],
                                         geom.centroid.xy[1]])
        else:
            x, y = scaled_polygon.exterior.xy
            coords = np.array(list(zip(np.array(x), np.array(y))))
            centroid = np.array([scaled_polygon.centroid.xy[0],
                                         scaled_polygon.centroid.xy[1]])
            
        centroid = centroid.reshape(1, 2)
        scaled_coords = 30*coords
        scaled_centroid = 30*centroid
        ic(scaled_centroid)
        offset = scaled_centroid - np.array([450, 300])
        ic(offset)
        corrected_coords = scaled_coords - offset
        corrected_centroid = scaled_centroid - offset

        corrected_centroid = corrected_centroid.reshape(1, 2)
        return (corrected_coords, corrected_centroid)

    except Exception as e:
        raise e

# Define a function to rotate a polygon
# def rotate_polygon(polygon, angle, center):
#     """Rotate a polygon while keeping its center."""
#     angle_rad = math.radians(angle)  # Convert angle to radians
#     rotated_polygon = []
#     for x, y in polygon:
#         ic(center)
#         temp_x = x - center[0]
#         temp_y = y - center[1]
#         rotated_x = temp_x * math.cos(angle_rad) - temp_y * math.sin(angle_rad)
#         rotated_y = temp_x * math.sin(angle_rad) + temp_y * math.cos(angle_rad)
#         rotated_polygon.append((rotated_x + center[0], rotated_y + center[1]))
#     return rotated_polygon


def rotate_polygon(coords, theta, centroid, pos):
    # convert degrees to radians
    theta = np.radians(theta)
    # create rotation matrix
    r = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    r = np.round(r, 3)
    # rotate around the centroid
    return (((coords - centroid) @ r) + centroid) + pos


# Initialize Pygame
pygame.init()
font = pygame.font.Font(None, 36)
# Define the dimensions of the window
window_width = 900
window_height = 600
window = pygame.display.set_mode((window_width, window_height))

# Set the title of the window
pygame.display.set_caption("Country_packing")

polygons = pkl.load(open('./assets/polygons.pkl', 'rb'))

big_country_ = get_polygon(polygons, "Algeria")
small_country_ = get_polygon(polygons, "Uganda")

ic(big_country_[1], small_country_[1])

ic(big_country_[0], small_country_[0])

# Set initial positions for the shapes
big_country_pos = [450, 300]  # Starting position of the rectangle
small_country_pos = [450, 300]   # Starting position of the triangle

# Define a clock to manage the frame rate
clock = pygame.time.Clock()

# Initialize rotation angle
rotation_angle = 0

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
                small_country_pos[0] = mouse_x + mouse_offset_x - 450
                small_country_pos[1] = mouse_y + mouse_offset_y - 300

        elif event.type == pygame.MOUSEWHEEL:
            rotation_angle += 5  # Adjust rotation speed as needed

    # Clear the screen with a white background
    window.fill((255, 255, 255))

    # Rotate the triangle
    rotated_small_country = rotate_polygon(small_country_[0],
                                           rotation_angle,
                                           small_country_[1],
                                           small_country_pos)
    #ic(rotated_small_country)
    # Draw the rectangle and the rotated triangle
    pygame.draw.polygon(window, (0, 0, 255), big_country_[0])  # Blue rectangle
    pygame.draw.polygon(window, (255, 0, 0), rotated_small_country)  # Red triangle

    overlap = np.round(Polygon(big_country_[0]).intersection(Polygon(rotated_small_country)).area/Polygon(rotated_small_country).area*100, 1)
    text_surface = font.render(f"{overlap}%",
                               True, (0,0,0))
    text_rect = text_surface.get_rect()
    text_rect.topright = (800, 100)
    window.blit(text_surface, text_rect)
    # Update the triangle's rect for collision detection
    small_country_rect = pygame.draw.polygon(window,
                                             (255, 0, 0),
                                             rotated_small_country, 1)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 30 FPS
    clock.tick(30)

# Quit Pygame
pygame.quit()
