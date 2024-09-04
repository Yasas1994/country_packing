import pygame
from shapely import MultiPolygon, Polygon
import pickle as pkl
import numpy as np
from icecream import ic


INITIAL_POS_X = 450
INITIAL_POS_Y = 300
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
WINDOW_CENTER = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
FRAME_RATE = 30
SCALING_PARAM = 30
DEGREES = 5
COLORS = [

    (255, 0, 0),     # Red
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (0, 255, 255),   # Cyan
    (255, 0, 255),   # Magenta
    (255, 165, 0),   # Orange
    (128, 0, 128),   # Purple
    (255, 192, 203),  # Pink
    (0, 128, 128)    # Teal
]



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
            coords = np.array(list(zip(np.array(x),
                                       np.array(y))))
            ic(geom.centroid.xy)
            centroid = np.array([geom.centroid.xy[0],
                                 geom.centroid.xy[1]])
        else:
            x, y = scaled_polygon.exterior.xy
            coords = np.array(list(zip(np.array(x), np.array(y))))
            centroid = np.array([scaled_polygon.centroid.xy[0],
                                 scaled_polygon.centroid.xy[1]])

        centroid = centroid.reshape(1, 2)
        scaled_coords = SCALING_PARAM*coords
        scaled_centroid = SCALING_PARAM*centroid
        ic(scaled_centroid)
        offset = scaled_centroid - np.array([INITIAL_POS_X, INITIAL_POS_Y])
        ic(offset)
        corrected_coords = scaled_coords - offset
        corrected_centroid = scaled_centroid - offset

        corrected_centroid = corrected_centroid.reshape(1, 2)
        return (corrected_coords, corrected_centroid)

    except Exception as e:
        raise e


def rotate_polygon(coords, theta, centroid):
    # convert degrees to radians
    theta = np.radians(theta)
    # create rotation matrix
    r = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    r = np.round(r, 3)
    # rotate around the centroid
    return (((coords - centroid) @ r) + centroid)


def text_box(message, position=(900, 10)):
    text_surface = font.render(f"{message}%",
                                True, (0,0,0))
    text_rect = text_surface.get_rect()
    text_rect.topright = position
    window.blit(text_surface, text_rect)

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

# Initialize Pygame
pygame.init()
font = pygame.font.Font(None, 36)
# Define the dimensions of the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Set the title of the window
pygame.display.set_caption("Country_packing")


# Polygon class to manage polygon objects
class Country:

    def __init__(self, coords, centroid, color):
        self.coords = coords
        self.color = color
        self.centroid = centroid

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.coords)

    def move(self, dx, dy):
        self.coords = [(x + dx, y + dy) for x, y in self.coords]

    def contains_point(self, point):
        return pygame.draw.polygon(window, self.color, self.coords, 0).collidepoint(point)


polygons = pkl.load(open('./assets/polygons.pkl', 'rb'))

# get country (coords, centroid)
big_country_coords = get_polygon(polygons, "Algeria")
small_country_coords = [get_polygon(polygons, "Uganda"),
                        get_polygon(polygons, "Sri Lanka"),
                        get_polygon(polygons, "Palestine"),
                        get_polygon(polygons, "Israel"),
                        get_polygon(polygons, "Syria"),
                        get_polygon(polygons, "South Korea"),
                        get_polygon(polygons, "Bhutan"),
                        get_polygon(polygons, "Nepal"),
                        get_polygon(polygons, "Germany"),
                        ]

# creaate country objects
big_country_obj =  [Country(big_country_coords[0], big_country_coords[1], color=(125,125,125))]
small_country_obj = [Country(i[0], i[1], color=COLORS[index]) for index, i in enumerate(small_country_coords)]


ic(big_country_coords[0].shape, small_country_coords[1][1].shape, big_country_coords[0][:, 0].shape)



# Set initial positions for the shapes
big_country_pos = [INITIAL_POS_X, INITIAL_POS_Y]
# add jitter?
small_country_pos = [[INITIAL_POS_X, INITIAL_POS_Y] for _ in range(len(small_country_coords))]

# Define a clock to manage the frame rate
clock = pygame.time.Clock()

# Initialize rotation angle
rotation_angle = [0 for _ in range(len(small_country_coords))]

# Main loop
running = True
rotating = False
dragging = False
dragged_object_index = 0
dragged_object = None


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            rotating = False
            for index, obj in enumerate(small_country_obj):
                if obj.contains_point(event.pos):
                    dragging = True
                    dragged_object = obj
                    dragged_object_index = index
                    mouse_offset_x_coord = obj.coords[:, 0] - event.pos[0]
                    mouse_offset_y_coord  = obj.coords[:, 1] - event.pos[1]
                    mouse_offset_x_centroid = obj.centroid[:, 0] - event.pos[0]
                    mouse_offset_y_centroid = obj.centroid[:, 1] - event.pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                # update x_position of the object
                dragged_object.coords[:, 0] = event.pos[0] + mouse_offset_x_coord #- INITIAL_POS_X
                # update the y position of the object
                dragged_object.coords[:, 1] = event.pos[1] + mouse_offset_y_coord #- INITIAL_POS_Y

                dragged_object.centroid[:, 0] = event.pos[0] + mouse_offset_x_centroid #- INITIAL_POS_X
                dragged_object.centroid[:, 1] = event.pos[1] + mouse_offset_y_centroid #- INITIAL_POS_Y

        elif event.type == pygame.MOUSEWHEEL:
            rotating = True
            if event.y > 0:
                rotation_angle[dragged_object_index] = (np.abs(rotation_angle[dragged_object_index]) + event.y)*1
            elif event.y < 0:
                # ic(event.y + -1 * (rotation_angle[dragged_object_index]))
                rotation_angle[dragged_object_index] = (event.y + -1 * np.abs(rotation_angle[dragged_object_index]))*1


    # Clear the screen with a white background
    window.fill((215, 215, 215))

    # draw objects
    big_country_obj[0].draw(window)
    for s_obj in small_country_obj:
        # ic(s_obj)
        s_obj.draw(window)

    # Rotate the triangle
    if (dragged_object is not None) and rotating:
        ic(dragged_object_index, rotation_angle)
        rotated_small_country = rotate_polygon(coords=dragged_object.coords,
                                               theta=rotation_angle[dragged_object_index],
                                               centroid=dragged_object.centroid)
        # ic(rotated_small_country)
        # Draw the rectangle and the rotated triangle
        dragged_object.coords = rotated_small_country
        dragged_object.draw(window)
        rotating = False
    # overlap = np.round(Polygon(big_country_[0]).intersection(Polygon(rotated_small_country)).area/Polygon(rotated_small_country).area*100, 1)
    for i, _ in enumerate(small_country_obj):
        overlap = np.round(Polygon(big_country_obj[0].coords).intersection(Polygon(small_country_obj[i].coords)).area/Polygon(small_country_obj[i].coords).area*100, 1)
        text_box(overlap, position=(900, 10+i*20))
        for j, _ in enumerate(small_country_obj):
             if Polygon(small_country_obj[i].coords).intersects(Polygon(small_country_obj[j].coords)):
                 if i != j:
                    intersected = calc_intersect(small_country_obj[i].coords, small_country_obj[j].coords)
        #         ic(intersected)
                    pygame.draw.polygon(window, (0, 0, 0), intersected)
    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 30 FPS
    clock.tick(FRAME_RATE)

# Quit Pygame
pygame.quit()
