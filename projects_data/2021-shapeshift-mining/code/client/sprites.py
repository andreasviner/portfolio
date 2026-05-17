import pygame
WHITE = (255, 255, 20)
pygame.init()
username_font = pygame.font.SysFont('Calibri', 16)

class other_dude(pygame.sprite.Sprite):

    def __init__(self, color1,color2, size,cordx,cordy,uid):

        super().__init__()
        self.uid = uid
        self.last_uid = uid
        self.text = username_font.render(uid, True, (0, 0, 0))
        self.hp = 100
        self.size = size
        self.x = cordx
        self.y = cordy
        self.attacking = 0
        self.sword_active = 0
        self.looking =(0,1)
        self.axe_lvl = 0
        self.sword_lvl = 0
        self.image = pygame.Surface([size, size+20])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        pygame.draw.circle(self.image, color1, [size/2,size/2], size/2)
        pygame.draw.circle(self.image, (0,0,0), [size/2,size/2], size/2,5)

        pygame.draw.rect(self.image, (0,0,0), pygame.Rect(0,size+2,size,6),0,2)

        pygame.draw.rect(self.image, (40,200,0), pygame.Rect(0,size+2,size//2,6),0,2)
        
        self.rect = self.image.get_rect()
        

    def update(self,x,y):
        if self.uid != self.last_uid:
            self.text = username_font.render(self.uid, True, (0, 0, 0))
            self.last_uid = self.uid
            
        self.rect.x = self.x + x
        self.rect.y = self.y + y
        if self.hp < 0:
            self.rect.x = -1000
            self.rect.y = -1000
            
        pygame.draw.rect(self.image, (0,0,0), pygame.Rect(0,self.size+2,self.size,6),0,2)

        pygame.draw.rect(self.image, (40,200,0), pygame.Rect(0,self.size+2,self.hp//2,6),0,2)

    def draw_name(self,screen):
        screen.blit(self.text, (self.rect.x + self.size//2 - self.text.get_width()//2, self.rect.y + self.size + 8))
        





class dude(pygame.sprite.Sprite):

    def __init__(self, color, size,cord,speed):

        super().__init__()
        self.sword_lvl = 0
        self.axe_lvl = 0
        self.hp = 100
        self.size = size
        self.x = cord
        self.y = cord
        self.last_x = cord
        self.last_y = cord
        self.move_x = 0
        self.move_y = 0
        self.speed = speed
        self.uid = ""
        self.color1 = (255,0,0)
        self.color2 = (255,0,0)

        self.image = pygame.Surface([size, size+20])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        pygame.draw.circle(self.image, color, [size/2,size/2], size/2)
        pygame.draw.circle(self.image, (0,0,0), [size/2,size/2], size/2,5)

        pygame.draw.rect(self.image, (0,0,0), pygame.Rect(0,size+2,size,6),0,2)

        pygame.draw.rect(self.image, (40,200,0), pygame.Rect(0,size+2,size//2,6),0,2)
        
        self.rect = self.image.get_rect()

    def update(self,x,y):
        self.last_x = self.x
        self.last_y = self.y
        if self.move_x != 0 or self.move_y != 0:
            if abs(self.move_x) + abs(self.move_y) > 1:
                self.x += self.move_x*0.7071067811865475*self.speed
                self.y += self.move_y*0.7071067811865475*self.speed
            else:
                self.x += self.move_x*self.speed
                self.y += self.move_y*self.speed
        
        self.rect.x = self.x + x
        self.rect.y = self.y + y
        self.move_x = 0
        self.move_y = 0
        pygame.draw.rect(self.image, (0,0,0), pygame.Rect(0,self.size+2,self.size,6),0,2)

        pygame.draw.rect(self.image, (40,200,0), pygame.Rect(0,self.size+2,self.hp//2,6),0,2)


    def move(self, x, y):
        self.move_x += x
        self.move_y += y

    def back(self):
        self.x = self.last_x
        self.y = self.last_y

    
class drill(pygame.sprite.Sprite):
    def __init__(self, x,y, owner):
        super().__init__()
        self.x = x
        self.y = y
        self.images = []
        self.images.append(pygame.image.load('drill0.png'))
        self.images.append(pygame.image.load('drill1.png'))
        self.images.append(pygame.image.load('drill2.png'))
        self.images.append(pygame.image.load('drill3.png'))


        self.index = 0

        self.image = self.images[self.index]
        self.rect = pygame.Rect(x, y, 63, 88)


    def update(self, x_offset, y_offset):
        #when the update method is called, we will increment the index
        self.index += 0.2
        self.rect.x = self.x + x_offset
        self.rect.y = self.y + y_offset
        arr = [0,1,2,3,3,2,1,0]
        #if the index is larger than the total images
        if int(self.index) > 7:
            #we will make the index to 0 again
            self.index = 0
        
        #finally we will update the image that will be displayed
        self.image = self.images[arr[int(self.index)]]


class shop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
       
        self.image = pygame.image.load('shop.png')
        self.image.set_colorkey((255,255,255))
        self.x = x
        self.y = y

        self.rect = pygame.Rect(0,0,90,90)

    def update(self, x_offset, y_offset):
        self.rect.x = self.x + x_offset
        self.rect.y = self.y + y_offset
        


        
class add_arrow(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite().__init__()
        self.images = []
       
        self.images.append(pygame.image.load('add_arrow_disabled.png'))
        self.images.append(pygame.image.load('add_arrow.png'))
        self.images[0].set_colorkey((255,255,255))
        self.images[1].set_colorkey((255,255,255))
        self.images[0] = pygame.transform.scale(self.images[0],(40,14))
        self.images[1] = pygame.transform.scale(self.images[1],(40,14))
                                    
        self.image = self.images[1]

        self.rect = pygame.Rect(0,0,40,14)

    def update(self, x_offset, y_offset):
        self.rect.x = self.x + x_offset
        self.rect.y = self.y + y_offset

    def bilt(self, screen, x,y,rotation,mouse_pos):
        self.rect.x = x
        self.rect.y = y
        if rotation%2 == 1:
            foo = self.rect.w
            self.rect.w = self.rect.h
            self.rect.h = foo
        self.image = pygame.transform.rotate(self.images[self.rect.collidepoint(mouse_pos)], rotation*90)
        screen.blit(self.image, self.rect)

class pickaxe(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite().__init__()
        self.pos = pygame.math.Vector2((0,0))
        self.images = []
        self.rotation = 0
        self.images.append(pygame.image.load('pick0.png'))
        self.images.append(pygame.image.load('pick1.png'))
        self.images.append(pygame.image.load('pick2.png'))
        self.images.append(pygame.image.load('pick3.png'))
        self.images.append(pygame.image.load('pick4.png'))
        self.images.append(pygame.image.load('pick5.png'))
        self.images[0].set_colorkey((255,255,255))
        for i in range(len(self.images)):
            self.images[i].set_colorkey((255,255,255))
            self.images[i] = pygame.transform.scale(self.images[i],(23,31))
            

        self.image = self.images[5]
        self.image.set_colorkey((255,255,255))

        self.rect = pygame.Rect(0,0,47,62)

    def bilt(self, screen, x, y, vector,what,i):
        self.rotation = (i%30)*3
        if self.rotation > 90:
            self.rotation = 0
        v1 = pygame.math.Vector2(1,0)
        rotation = -v1.angle_to(vector)
        self.rect.x = x
        self.rect.y = y-63
        self.image = self.images[what]
        img = pygame.transform.rotate(self.image,rotation)
        img.set_colorkey((255,255,255))

        img = pygame.transform.rotozoom(self.image, rotation+45+self.rotation, 1)  # Rotate the image.
        img.set_colorkey((255,255,255))
        offset_vec = self.pos.rotate(rotation)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        vector = vector.rotate(-10)
        rect = img.get_rect(center=offset_vec+pygame.math.Vector2((x -vector[0],y-vector[1])))

        screen.blit(img,rect)


class sword(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite().__init__()
        self.pos = pygame.math.Vector2((0,0))
        self.images = []
        self.rotation = 0
        self.images.append(pygame.image.load('sword0.png'))
        self.images.append(pygame.image.load('sword1.png'))
        self.images.append(pygame.image.load('sword2.png'))
        self.images.append(pygame.image.load('sword3.png'))
        self.images.append(pygame.image.load('sword4.png'))
        self.images.append(pygame.image.load('sword5.png'))
        self.images[0].set_colorkey((255,255,255))
        for i in range(len(self.images)):
            self.images[i].set_colorkey((255,255,255))
            self.images[i] = pygame.transform.scale(self.images[i],(24,55))
            

        self.image = self.images[5]
        self.image.set_colorkey((255,255,255))

        self.rect = pygame.Rect(0,0,47,62)

    def bilt(self, screen, x, y, vector,what,i):
        self.rotation = i%20
        v1 = pygame.math.Vector2(1,0)
        rotation = -v1.angle_to(vector)
        self.rect.x = x
        self.rect.y = y-63
        self.image = self.images[what]
        img = pygame.transform.rotate(self.image,rotation)
        img.set_colorkey((255,255,255))

        img = pygame.transform.rotozoom(self.image, rotation+90, 1)  # Rotate the image.
        img.set_colorkey((255,255,255))
        offset_vec = self.pos.rotate(rotation)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        vector.scale_to_length(vector.length()+self.rotation)
        rect = img.get_rect(center=offset_vec+pygame.math.Vector2((x -vector[0],y-vector[1])))

        screen.blit(img,rect)


class stone(pygame.sprite.Sprite):
    def __init__(self, x, y, lvl):
        super().__init__()
        
        self.images = []
        self.lvl = lvl

        if lvl == 0:
            self.image = pygame.image.load('rock_s.png')
        elif lvl == 1:
            self.image = pygame.image.load('rock_g.png')
        elif lvl == 2:
            self.image = pygame.image.load('rock_d.png')
            
        self.image.set_colorkey((255,255,255))
        self.x = x
        self.y = y

        self.rect = pygame.Rect(0,0,90,90)

    def update(self, x_offset, y_offset):
        self.rect.x = self.x + x_offset
        self.rect.y = self.y + y_offset
            

class shop_pick(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite().__init__()
        self.images = []
        self.images.append(pygame.image.load('pick0.png'))
        self.images.append(pygame.image.load('pick1.png'))
        self.images.append(pygame.image.load('pick2.png'))
        self.images.append(pygame.image.load('pick3.png'))
        self.images.append(pygame.image.load('pick4.png'))
        self.images.append(pygame.image.load('pick5.png'))

        for i in range(len(self.images)):
            self.images[i].set_colorkey((255,255,255))
        self.rect = pygame.Rect(0,0,47,62)

    def blit(self, screen, x, y, i):
        self.rect.x = x
        self.rect.y = y
        screen.blit(self.images[i],self.rect)

class shop_sword(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite().__init__()
        self.images = []
        self.images.append(pygame.image.load('sword0.png'))
        self.images.append(pygame.image.load('sword1.png'))
        self.images.append(pygame.image.load('sword2.png'))
        self.images.append(pygame.image.load('sword3.png'))
        self.images.append(pygame.image.load('sword4.png'))
        self.images.append(pygame.image.load('sword5.png'))

        for i in range(len(self.images)):
            self.images[i].set_colorkey((255,255,255))
        self.rect = pygame.Rect(0,0,48,110)

    def blit(self, screen, x, y, i):
        self.rect.x = x
        self.rect.y = y
        screen.blit(self.images[i],self.rect)



FONT = pygame.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.w = w
        self.color = (137, 16, 156)
        self.text = ''
        self.type = text
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.active = False

    def handle_event(self, event):
            # Change the current color of the input box.
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.type==True:
                    if len(self.text) < 21:
                        self.text += event.unicode
                else:
                    try:
                        self.text += str(int(event.unicode))
                    except:
                        pass

    def draw(self, screen,i):
        # Blit the text.
        pygame.draw.rect(screen, (0,0,0), self.rect)
        if (i//60)%2 == 0:
            self.txt_surface = FONT.render(self.text + '_', True, self.color)
        else:
            self.txt_surface = FONT.render(self.text +  " ", True, self.color)
        screen.blit(self.txt_surface, (self.rect.x+10, self.rect.y+10))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 5)

    def update(self, off_x, off_y):
        
        self.rect.y = self.y + off_y
        width = max(self.w, self.txt_surface.get_width()+10)
        self.rect.w = width
        self.rect.x = self.x + off_x -self.rect.w//2

