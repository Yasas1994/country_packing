import pygame
from pygame.locals import *
import shapely
import numpy as np
import math



class Country_2:
    def __init__(self, polygon, pos):
        self.polygon = polygon
        self.angle = 0

    def update_rotation(self):
        rad = math.radians(self.angle)
        rot_matrix = [[math.cos(rad), -math.sin(rad)],[math.sin(rad), math.cos(rad)]]
        self.polygon = np.matmul(rot_matrix, self.polygon-cent)

pol = [[300, 300], [100, 400],
                     [100, 300]]
cent = [1/3*500,1/3*1000]
centr = [[166, 166]]
print(cent)

polygon = Country_2(pol, 0)
class Country:
    def __init__(self, image, pos):
        self.img = image
        self.r_img = image
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.r_rect = self.rect
        self.r_rect.center = self.rect.center
        self.mask = pygame.mask.from_surface(self.img)
        self.angle = 0

    def update_rotation(self):
        self.r_img = pygame.transform.rotate(self.img, self.angle)
        self.r_rect = self.r_img.get_rect(center = self.img.get_rect(topleft = self.r_rect.topleft).center)

    def draw(self, surf):
        surf.blit(self.r_img, self.r_rect)

def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)
    return rotated_image, new_rect
    #pygame.display.flip()

def fill(surface, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    r, g, b, _ = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), Color(r, g, b, a))

# read svg file -> write png file
'''
subprocess.run([inkscape, '--export-type=png', f'--export-filename={"C:/Users/Jonas/Downloads/us_2.png"}',
                f'--export-width={500}', f'--export-height={500}', f"C:/Users/Jonas/Downloads/usa.svg"], capture_output=True)
subprocess.run([inkscape, '--export-type=png', f'--export-filename={"C:/Users/Jonas/Downloads/austria.png"}',
                f'--export-width={100}', f'--export-height={100}', f"C:/Users/Jonas/Downloads/austria.svg"], capture_output=True)
                '''
pygame.init()

w, h = 1000, 500
screen = pygame.display.set_mode((w, h))

img = pygame.image.load('C:\\Users\\Jonas\\Downloads\\us_2.png')
img.convert()

img_2 = pygame.image.load('C:\\Users\\Jonas\\Downloads\\austria.png')
img_2.convert()
USA = Country(img, (500, 250))
Austria = Country(img_2, (800, 150))

#rect = img.get_rect()
#rect.center = w//2, h//2

#rect_2 = img_2.get_rect()
#rect_2.center = w//2 + 300, h//2-100
#Step 7: Later on, set the running value for running the game and moving value for moving the image.

#img_2_r = img_2
#rect_2_r = rect_2
#img_r = img
#rect_r = rect

running = True
moving = False
#Step 8: Set the things which you want your app to do when in running state.

#act_rect = rect_2_r
#act_im = img_2_r


#angle = 0
#while not done:

    # [...]

    #rotated_image = pygame.transform.rotate(image, angle)
    #angle += 1

    #screen.blit(rotated_image, pos)
    #pygame.display.flip()



while running:
   screen.fill("White")
   pygame.draw.polygon(screen, (255,0,0), polygon.polygon)
   Austria.draw(screen)
   #USA.draw(screen)
   for event in pygame.event.get():
       if event.type == QUIT:
           running = False
       elif event.type == MOUSEBUTTONDOWN:
          polygon.angle = 45
          polygon.update_rotation()
          pygame.draw.polygon(screen, (255, 255, 0), polygon.polygon)
          print(polygon.polygon)
   #fill(Austria.r_img, Color(240, 200, 40))
   #img_2.set_alpha(128)
   #screen.blit(img_r, rect_r)
   #blitRotateCenter(screen, img_2, rect.topleft, angle)
   #screen.blit(img_2_r, rect_2_r)
   #pygame.draw.rect(screen, "red", rect_r, 2)
   #pygame.draw.rect(screen, "blue", rect_2_r, 2)
   pygame.display.update()
   #print(USA)

'''
angle_1 = 0
angle_2 = 0
while running:
   for event in pygame.event.get():
       if event.type == QUIT:
           running = False
       elif event.type == MOUSEBUTTONDOWN:
          if rect.collidepoint(event.pos):
              moving = True
              act_rect = rect
          if rect_2_r.collidepoint(event.pos):
              moving = True
              act_rect = rect_2_r
       elif event.type == MOUSEBUTTONUP:
           moving = False

       elif event.type == MOUSEMOTION and moving:
           act_rect.move_ip(event.rel)
           rect_2 = rect_2_r
           rect = rect_r
       elif event.type == MOUSEWHEEL:

            if act_rect == rect:
                angle_1 += 5
                img_r, rect_r = blitRotateCenter(screen, img, rect.topleft, angle_1)
            elif act_rect == rect_2_r:
                angle_2 += 5
                #img_2, rect_2 = rot_center(img_2, rect_2, 5)
                img_2_r, rect_2_r = blitRotateCenter(screen, img_2, rect_2.topleft, angle_2)

   screen.fill("White")
   fill(img_2_r, Color(240, 200, 40))
   img_2.set_alpha(128)
   screen.blit(img_r, rect_r)
   #blitRotateCenter(screen, img_2, rect.topleft, angle)
   screen.blit(img_2_r, rect_2_r)
   pygame.draw.rect(screen, "red", rect_r, 2)
   pygame.draw.rect(screen, "blue", rect_2_r, 2)
   pygame.display.update()
'''
pygame.quit()