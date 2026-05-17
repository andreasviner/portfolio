import pygame
pygame.init()
colors = [(0,162,232),(255,100,0)]
font = pygame.font.SysFont('Eras Bold ITC', 35)

map_map = [[[0,1,2,3]],[[4,5,6,7],[2,4,9,8],[0,1,7,8],[3,1,6,9]]]
    
poly_maps = [[[(50,20),(20,80),(80,80)]],
         [[(50,15),(30,50),(50,85),(70,50)],[(50,20),(20,70),(35,85),(50,70),(65,85),(80,70)],[(50,20),(20,70),(30,80),(70,80),(80,70)],[(60,15),(50,35),(40,15),(20,75),(80,75)]],
         [[(60,20),(40,20),(20,70),(30,80),(70,80),(80,70)],[(60,15),(50,35),(40,15),(20,70),(30,80),(70,80),(80,70)],[(56,30),(50,10),(44,30),(26,70),(38,90),(50,70),(62,90),(74,70)],
         [(34,20),(42,30),(50,10),(58,30),(66,20),(82,80),(18,80)],
         [(50,10),(75,50),(63,65),(65,85),(57,70),(50,90),(43,70),(35,85),(37,65),(25,50)],
         [(50,10),(60,40),(90,50),(60,60),(50,90),(40,60),(10,50),(40,40)],[(60,10),(50,30),(40,10),(25,50),(40,90),(50,70),(60,90),(75,50)],[(50,10),(35,30),(35,70),(50,90),(65,70),(65,30)],
         [(65,30),(50,10),(35,30),(26,70),(38,90),(50,70),(62,90),(74,70)],[(56,10),(50,30),(44,10),(26,70),(38,90),(50,70),(62,90),(74,70)]]]

def make_text(what,length,cut, number = ""):
    text = font.render(what, True, (255,255,254))
    textRect = text.get_rect()
    cropped = pygame.Surface((length, 32))
    cropped.fill(colors[0])
    pygame.draw.rect(cropped,colors[1],(cut,0,length,32))
    cropped.blit(text, (5, 3))

    
    if number != "":
        text = font.render(str(number), True, (255,255,254))
        cropped.blit(text,(length-20,3))
        
    
    return cropped

def make_sqe(arr,mode,point,y,width):
    cropped = pygame.Surface((100, 100))
    cropped.fill((255,255,255))
    if not pygame.Rect(width-110,y+10,100,100).collidepoint(point):
        pygame.draw.rect(cropped, (255,255,254), (0,0,100,100),0,10)
    else:
        pygame.draw.rect(cropped, (169,169,169), (0,0,100,100),0,10)
    
    pygame.draw.rect(cropped, (0,0,0), (0,0,100,100),5,10)
    pygame.draw.polygon(cropped, colors[mode], arr)
    return cropped
    
    

shop_screen = pygame.Surface((400,410))
shop_screen.set_colorkey((255,255,255))
upgrade_screen = pygame.Surface((120,450))
upgrade_screen.set_colorkey((255,255,255))

def update(arr): 
    shop_screen.fill((255,255,255))
    shop_screen.blit(make_text(" Payer Upgrades:", 300, 300), (0,20))
    shop_screen.blit(make_text(" Movement speed", 300, (300/20)*arr[0],1), (0,50))
    shop_screen.blit(make_text(" Max Health", 300, (300/20)*arr[1],2), (0,80))
    shop_screen.blit(make_text(" Health Regen", 300, (300/20)*arr[2],3), (0,110))

    shop_screen.blit(make_text(" Standar Attack:", 300, 300), (0,150))
    shop_screen.blit(make_text(" Reload Rate", 300, (300/20)*arr[3],4), (0,180))
    shop_screen.blit(make_text(" Bullet Damage", 300, (300/20)*arr[4],5), (0,210))
    shop_screen.blit(make_text(" Bullet Speed", 300, (300/20)*arr[5],6), (0,240))

    shop_screen.blit(make_text(" Special Attacks:", 300, 300), (0,280))
    shop_screen.blit(make_text(" Refresh rate", 300, (300/20)*arr[6],7), (0,310))
    shop_screen.blit(make_text(" Projectile damage", 300, (300/20)*arr[7],8), (0,340))
    shop_screen.blit(make_text(" Projectile speed", 300, (300/20)*arr[8],9), (0,370))

def update_upgrade(mode,width,arr):
    
    point = pygame.mouse.get_pos()
    upgrade_screen.fill((255,255,255))
    if arr[0] < 2:
        upgrade_screen.blit(make_sqe(poly_maps[arr[0]+1][map_map[arr[0]][arr[1]][0]],mode,point,0,width),(0,0))
        upgrade_screen.blit(make_sqe(poly_maps[arr[0]+1][map_map[arr[0]][arr[1]][1]],mode,point,110,width),(0,110))
        upgrade_screen.blit(make_sqe(poly_maps[arr[0]+1][map_map[arr[0]][arr[1]][2]],mode,point,220,width),(0,220))
        upgrade_screen.blit(make_sqe(poly_maps[arr[0]+1][map_map[arr[0]][arr[1]][3]],mode,point,330,width),(0,330))


def check(pos,width,arr):
    if pygame.Rect(width-110,10,100,100).collidepoint(pos):
        return map_map[arr[0]][arr[1]][0]
    elif pygame.Rect(width-110,120,100,100).collidepoint(pos):
        return map_map[arr[0]][arr[1]][1]
    elif pygame.Rect(width-110,230,100,100).collidepoint(pos):
        return map_map[arr[0]][arr[1]][2]
    elif pygame.Rect(width-110,340,100,100).collidepoint(pos):
        return map_map[arr[0]][arr[1]][3]
    return 1000

    
def draw(screen):
    screen.blit(shop_screen, (0,-10))

def draw_upgrade(screen, width):
    screen.blit(upgrade_screen, (width-110,10))

   #draw(screen)

    
 
