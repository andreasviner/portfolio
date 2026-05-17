import pygame
import pygame.math
from random import randint
poly_maps = [[[(50,20),(20,80),(80,80)]],
         [[(50,15),(30,50),(50,85),(70,50)],[(50,20),(20,70),(35,85),(50,70),(65,85),(80,70)],[(50,20),(20,70),(30,80),(70,80),(80,70)],[(60,15),(50,35),(40,15),(20,75),(80,75)]],
             
         [[(60,20),(40,20),(20,70),(30,80),(70,80),(80,70)],[(60,15),(50,35),(40,15),(20,70),(30,80),(70,80),(80,70)],[(56,30),(50,10),(44,30),(26,70),(38,90),(50,70),(62,90),(74,70)],
         [(34,20),(42,30),(50,10),(58,30),(66,20),(82,80),(18,80)],
         [(50,10),(75,50),(63,65),(65,85),(57,70),(50,90),(43,70),(35,85),(37,65),(25,50)],
         [(50,10),(60,40),(90,50),(60,60),(50,90),(40,60),(10,50),(40,40)],[(60,10),(50,30),(40,10),(25,50),(40,90),(50,70),(60,90),(75,50)],[(50,10),(35,30),(35,70),(50,90),(65,70),(65,30)],
         [(65,30),(50,10),(35,30),(26,70),(38,90),(50,70),(62,90),(74,70)],[(56,10),(50,30),(44,10),(26,70),(38,90),(50,70),(62,90),(74,70)]]]

projectiles = [[(20,10),(30,10),(30,40),(20,40)],[(25,10),(10,40),(40,40)],[(0,0),(0,50),(50,50),(50,0)]]

mode_colors = [(0,162,232),(255,100,0)]



def draw_hp(screen,cords,hp,mode):
    pygame.draw.rect(screen, (0,0,0), (cords[0]-1,cords[1],102,10))
    pygame.draw.rect(screen, mode_colors[mode], (cords[0],cords[1]+1,hp,8))
    


class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.spent_arr = [0,0,0,0,0,0,0,0,0,0]
        self.angle = 0
        pygame.sprite.Sprite.__init__(self)
        self.x = 100
        self.y = 100
        self.lvl = [0,0]
        #speed, max_hp, hp regen, reload_speed, bullet_dmg, bullet_speed, refresh_rate, projectile_dmg, projectile speed
        self.data = [5,100,5,25,5,3,1,5,3]
        self.color = (0,0,0)
        self.rotated = 0
        self.penalty = 0
        self.image = pygame.Surface((100, 100))
        self.image.set_colorkey((255,255,255,0))
        pygame.draw.polygon(self.image, (255,255,0), [(0,0),(0,50),(50,50),(50,0),(20,20)])
        self.rect = self.image.get_rect()
        
        self.original_image = self.image
        self.mask = pygame.mask.from_surface(self.image)

    def reset(self):
        self.angle = 0
        self.x = randint(500,4500)
        self.y = randint(500,4500)
        self.lvl = [0,0]
        self.data = [5,100,5,25,5,3,1,5,3]
        self.spent_arr = [0,0,0,0,0,0,0,0,0,0]


        
    def change_color(self,color):
        if self.color != color:
            self.color = color
        self.original_image.fill((255,255,255,0))
            
        pygame.draw.polygon(self.original_image, mode_colors[color], poly_maps[self.lvl[0]][self.lvl[1]])
 
    def update(self,xy):
        if self.penalty != 0:
            self.penalty += -1
            #sprint(self.penalty)
        self.rotated  += 1
        v = pygame.Vector2()
        x, y = pygame.mouse.get_pos()
        v.xy = (x-self.x+xy[0],y-self.y+xy[1])

        
        self.angle = v.angle_to((0,1))+180
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        self.rect.x = (self.x-self.image.get_height()/2-xy[0])
        self.rect.y = (self.y-self.image.get_width()/2-xy[1])
        self.mask = pygame.mask.from_surface(self.image)

        
    def move(self,x,y):
        if self.penalty == 0:
            self.x += x*self.data[0]
            self.y += y*self.data[0]
        else:
            self.x += x
            self.y += y
            
        if self.x > 5000:
            self.x = 5000
        elif self.x < 0:
            self.x = 0
            
        if self.y > 5000:
            self.y = 5000
        elif self.y < 0:
            self.y = 0


def draw_player(screen, arr,xy):
    #id = arr[0]
    lvl = arr[1]
    mode = arr[2]
    pos = arr[3]
    angle = arr[4]

    image = pygame.Surface((100,100))
    image.fill((255,255,255))
    image.set_colorkey((255,255,255,0))
    pygame.draw.polygon(image,mode_colors[mode],poly_maps[lvl[0]][lvl[1]])
    
    image = pygame.transform.rotate(image,angle)
    screen.blit(image, ((pos[0]-image.get_height()/2-xy[0]),(pos[1]-image.get_width()/2-xy[1])))



            
class Object(pygame.sprite.Sprite):
    def __init__(self,pos,nr,mode):
        pygame.sprite.Sprite.__init__(self)
        
        self.x = pos[0]
        self.y = pos[1]
        arr = []
        self.nr = nr

        for i in range(nr):
            arr.append((360/nr)*i)

                
        self.mode = mode
        
        self.image = pygame.Surface((50,50))
        poly = []
        v = pygame.Vector2()
        v.xy = (25,0)
        for item in arr:
            poly.append((v.rotate(item)[0]+25,v.rotate(item)[1]+25))
        
        self.image.fill((255,255,255,0))
        self.image.set_colorkey((255,255,255,0))
        pygame.draw.polygon(self.image, mode_colors[self.mode], poly)
        self.image = pygame.transform.scale(self.image, (20+4*self.nr, 20+4*self.nr))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (self.x, self.y)

    def update(self,xy):
        self.rect.center = (self.x-xy[0], self.y-xy[1])
    

    def hurt(self):
        if self.nr == 3:
            self.kill()
            return
        self.image = pygame.Surface((50,50))
        self.image.fill((255,255,255,0))
        self.image.set_colorkey((255,255,255,0))
        self.nr += -1
        arr = []
        
        for i in range(self.nr):
            arr.append((360/self.nr)*i)

        poly = []
        v = pygame.Vector2()
        v.xy = (25,0)
        for item in arr:
            poly.append((v.rotate(item)[0]+25,v.rotate(item)[1]+25))

        pygame.draw.polygon(self.image, mode_colors[self.mode], poly)
        self.image = pygame.transform.scale(self.image, (10+5*self.nr, 10+5*self.nr))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (self.x, self.y)
        

    





class Projectile(pygame.sprite.Sprite):
    def __init__(self, direction, start_pos,what,scale,speed,mode,xy,angle,dmg,the_d):
        pygame.sprite.Sprite.__init__(self)
        self.id = the_d
        self.life = 0
        self.scale = scale
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.speed = speed
        
        self.image  = pygame.Surface((50,50))
        self.image.fill((255,255,255,0))
        self.image.set_colorkey((255,255,255,0))
        pygame.draw.polygon(self.image,mode_colors[mode],projectiles[what])
        if scale != 1:
            self.image = pygame.transform.scale(self.image, (50*scale, 50*scale))
        v = pygame.Vector2()
        v.xy = direction
        v = v.normalize().rotate(angle)
        self.direciton = v
        self.image = pygame.transform.rotate(self.image, v.angle_to((0,1)))
        self.rect = self.image.get_rect()
        self.rect.x =(self.x-self.image.get_height()/2-xy[0])
        self.rect.y = ( self.y-self.image.get_width()/2-xy[1])
        self.mask = pygame.mask.from_surface(self.image)
        self.dmg = 5

    def hurt(self):
        print("USLESS")

    def update(self,xy):
        self.life += 1
        self.x += self.direciton[0]*self.speed
        self.y += self.direciton[1]*self.speed
        self.rect.x =(self.x-self.image.get_height()/2-xy[0])
        self.rect.y = ( self.y-self.image.get_width()/2-xy[1])
        if self.life == 200:
            self.kill()
        
