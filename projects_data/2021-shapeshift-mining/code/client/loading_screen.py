import pygame, random
#Let's import the Car Class
from loading_screen_sprites import arrow


def init(arrow_size):
    
     
    first_a = arrow((255,255,255), arrow_size)
    first_a.rect.x = 0
    first_a.rect.y = 0
    return first_a
 

def pattern(screen,color_1,color_2,e_off_x,e_off_y,screen_width,screen_hight,first_a,arrow_size,i):
    all_sprites_list = pygame.sprite.Group()
    all_sprites_list.add(first_a)
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            carryOn=False
    #all_sprites_list.update()

    if ((i//90)%2 == 0):
        i += 1
        screen.fill(color_1)
        #screen_color = color_1
        first_a.update_color(color_2)
        all_sprites_list.update()
        off_x = (first_a.image.get_width() - arrow_size)/2 - e_off_x
        off_y = (first_a.image.get_height()- arrow_size)/2 - e_off_y
        first_a.rotate(i%360)
        for x in range(screen_width//arrow_size+2):
            for y in range(screen_hight//arrow_size+2):
                first_a.rect.x = x*arrow_size - off_x
                first_a.rect.y = y*arrow_size - off_y
                all_sprites_list.draw(screen)


    else:
        i += 1
        
        screen.fill(color_2)
        #screen_color = color_2
        first_a.update_color(color_1)
        all_sprites_list.update()
        off_x = (first_a.image.get_width() - arrow_size)/2 +arrow_size/2 - e_off_x
        off_y = (first_a.image.get_height()- arrow_size)/2 +arrow_size/2 - e_off_y
        first_a.rotate(i%360+180)
        for x in range(screen_width//arrow_size+2):
            for y in range(screen_hight//arrow_size+2):
                
                first_a.rect.x = x*arrow_size - off_x
                first_a.rect.y = y*arrow_size - off_y
                all_sprites_list.draw(screen)

    
 
