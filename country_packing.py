import pygame
import math  # Use the standard math module for trigonometry
from shapely import Polygon, MultiPolygon, Point
from shapely.ops import nearest_points
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


def rotate_polygon(coords, theta, centroid, pos):
    # convert degrees to radians
    theta = np.radians(theta)
    # create rotation matrix
    r = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    r = np.round(r, 3)
    # rotate around the centroid
    return (((coords - centroid) @ r) + centroid) + pos


def calc_intersect(polgon_1, polygon_2):
    intersected = Polygon(polgon_1).intersection(Polygon(polygon_2))
    if intersected.geom_type == "MultiPolygon":
        tmp = np.array([i.area for i in intersected.geoms])
        geom = intersected.geoms[np.argmax(tmp)]
        x, y = geom.exterior.xy
    else:
        x, y = intersected.exterior.xy
    result_polygon = np.array(list(zip(np.array(x), np.array(y))))

    return result_polygon


def calculate_target_function(current_polygon, small_polygons, big_polygon):
    # Check if the current_polygon is entirely within the big_polygon
    ic(current_polygon)
    ic(small_polygons[0])
    if not Polygon(big_polygon).contains(Polygon(current_polygon)):
        return np.inf

    ic(small_polygons[1][0])
    ic(current_polygon)
    # Check if current_polygon intersects with any of the small_polygons
    if Polygon(current_polygon).intersects(Polygon(small_polygons[1][0])): #for small_polygon in small_polygons
           #if not np.array_equal(current_polygon,small_polygon[0])):
        ic("Intersect")
        return np.inf

    # Create a list of all other polygons (excluding the current polygon itself)
    # We include the exterior of the big_polygon
    all_other_polygons = [
        small_polygon for small_polygon in small_polygons
        if current_polygon != Polygon(small_polygon) and Polygon(small_polygon).intersects(big_polygon)
    ]
    all_other_polygons.append(big_polygon.exterior)

    # Convert all_other_polygons to a MultiPolygon for easier distance calculation
    combined_polygons = MultiPolygon(all_other_polygons)

    # Get the points from the exterior of the current polygon
    polygon_points = [Point(coord) for coord in current_polygon.exterior.coords]

    # Calculate distances to the nearest point on any of the other polygons
    distances = [
        point.distance(nearest_points(point, combined_polygons)[1])
        for point in polygon_points
    ]

    # Calculate the mean distance
    mean_distance = np.mean(distances)

    return mean_distance


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
small_countries = [get_polygon(polygons, "Uganda"),
                   get_polygon(polygons, "Chad")]
ic(small_countries)

# Set initial positions for the shapes
big_country_pos = [450, 300]  # Starting position of the rectangle
small_country_pos = [[450, 300], [450,300]]   # Starting position of the triangle
#small_countr_2_pos = [600, 400]
# Define a clock to manage the frame rate
clock = pygame.time.Clock()

# Initialize rotation angle
rotation_angle = [0, 0]

# Main loop
running = True
dragging = False

active = 0
nl = '\n'


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check if the mouse is clicking inside the triangle
            if small_countries_rect[0].collidepoint(mouse_x, mouse_y):
                dragging = True
                mouse_offset_x = small_countries_rect[0].x - mouse_x
                mouse_offset_y = small_countries_rect[0].y - mouse_y
                active = 0
            elif small_countries_rect[1].collidepoint(mouse_x, mouse_y):
                dragging = True
                mouse_offset_x = small_countries_rect[1].x - mouse_x
                mouse_offset_y = small_countries_rect[1].y - mouse_y
                active = 1

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                small_country_pos[active][0] = mouse_x + mouse_offset_x - 450
                small_country_pos[active][1] = mouse_y + mouse_offset_y - 300


        elif event.type == pygame.MOUSEWHEEL:
            rotation_angle[active] += 5  # Adjust rotation speed as needed

    # Clear the screen with a white background
    window.fill((255, 255, 255))

    # Rotate the triangle
    rotated_small_country = rotate_polygon(small_countries[0][0],
                                           rotation_angle[0],
                                           small_countries[0][1],
                                           small_country_pos[0])
    rotated_small_country_2 = rotate_polygon(small_countries[1][0],
                                           rotation_angle[1],
                                           small_countries[1][1],
                                           small_country_pos[1])
    #ic(rotated_small_country)
    # Draw the rectangle and the rotated triangle
    pygame.draw.polygon(window, (0, 119, 182), big_country_[0])  # Blue rectangle
    pygame.draw.polygon(window, (207, 142, 128), rotated_small_country)  # Red triangle
    pygame.draw.polygon(window, (252, 181, 181), rotated_small_country_2)  # Red triangle

    overlap_1 = np.round(Polygon(big_country_[0]).intersection(Polygon(rotated_small_country)).area/Polygon(rotated_small_country).area*100, 1)
    overlap_2 = np.round(Polygon(big_country_[0]).intersection(Polygon(rotated_small_country_2)).area/Polygon(rotated_small_country_2).area*100, 1)
    overlap_b = np.round(Polygon(rotated_small_country).intersection(Polygon(rotated_small_country_2)).area/Polygon(rotated_small_country_2).area*100, 1)
    text_surface = font.render(f"{overlap_1}%",
                               True, (0,0,0))
    text_rect = text_surface.get_rect()
    text_rect.topright = (900, 10)
    window.blit(text_surface, text_rect)
    text_surface = font.render(f"{overlap_2}%",
                               True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.topright = (900, 30)
    window.blit(text_surface, text_rect)
    text_surface = font.render(f"{overlap_b}%",
                               True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.topright = (900, 50)
    window.blit(text_surface, text_rect)

    if Polygon(rotated_small_country).intersects(Polygon(rotated_small_country_2)):
        intersected = calc_intersect(rotated_small_country, rotated_small_country_2)

        pygame.draw.polygon(window, (255, 23, 25), intersected)
        # Update the triangle's rect for collision detection
    small_countries_rect = []
    small_countries_rect.append(pygame.draw.polygon(window,
                                             (255, 0, 0),
                                             rotated_small_country, 1))
    small_countries_rect.append(pygame.draw.polygon(window,
                                                  (255, 0, 0),
                                                  rotated_small_country_2, 1))

   # calculate_target_function(small_countries[active][0], small_countries, Polygon(big_country_[0]))
    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 30 FPS
    clock.tick(30)

# Quit Pygame
pygame.quit()
