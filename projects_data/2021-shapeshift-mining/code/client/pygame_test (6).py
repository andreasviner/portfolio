import pygame
import win32api
import win32con
import win32gui
import pyautogui
import loading_screen
import sprites
import _thread as thread
import socket,pickle  


s = socket.socket()        


pick_prices = [30,100,1000,5000,40000]
sword_prices = [30,100,1000,5000,40000]

# Define the port on which you want to connect
port = 1337
s.connect(('51.175.184.127', port))
arr = (["User",(200,200,200),(220,220,220)])

data_string = pickle.dumps(arr)
s.send(data_string)


arr = pickle.loads(s.recv(1024))




unlocked_size = arr[0]
start_size = arr[1]
squ_size = arr[2]

offset_x = -squ_size*unlocked_size//2+400
offset_y = -squ_size*unlocked_size//2+300


player_coins = 100000
standard_player_speed = arr[3]
standard_player_size = arr[4]


arrow_size  = 100
arrows_data = []
lines_arr = []
arrows_rects =[]
unlocked_arr = []
screen_x = 0

for a in range(unlocked_size):
    unlocked_arr.append([])
    for b in range(unlocked_size):
        unlocked_arr[-1].append(2)

#print(unlocked_arr)
for a in range(start_size+2):
    for b in range(start_size+2):
        unlocked_arr[unlocked_size//2-start_size//2+a-1][unlocked_size//2-start_size//2+b-1] = 0
        
for a in range(start_size):
    for b in range(start_size):
        unlocked_arr[unlocked_size//2-start_size//2+a][unlocked_size//2-start_size//2+b] = 1
        

for line in unlocked_arr:
    print(line)
















inited = loading_screen.init(arrow_size)
pygame.init()
screen = pygame.display.set_mode((0, 0),pygame.NOFRAME,pygame.FULLSCREEN) # For borderless, use pygame.NOFRAME
infoObject = pygame.display.Info()
SCREENWIDTH = infoObject.current_w
SCREENHEIGHT = infoObject.current_h


done = False

screen_rect = pygame.rect.Rect(100,100,start_size*squ_size,start_size*squ_size)
bar_rect = pygame.rect.Rect(100,100,200,30)

screen_moving = False

fuchsia = (255, 0, 128)  # Transparency color
win_color = (0, 162, 237)
start_x = 0
start_y = 0



# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
icon = pygame.image.load(r'.\icon.png')
#win_standard = myfont = pygame.font.SysFont('Calibri', 15)
win_standard = pygame.font.SysFont('Segoe UI', 12)
coin_font = pygame.font.SysFont('Verdana', 16,1)

shop_font = pygame.font.SysFont('Verdana', 18,1)
welcom_text = shop_font.render('To quit the shop, walk out', True, (0,0,0))

title_text = win_standard.render('Python 3.0.8', True, (0, 0, 0))

bar_width = 100
bar_x = 0
bar_y = 0


def turn_if_not_one(turn_x,turn_y):
    if unlocked_arr[turn_x][turn_y] != 1:
        unlocked_arr[turn_x][turn_y] = 0

def add_squ(add_x,add_y):
    global screen_x
    global bar_y
    
    if unlocked_arr[add_x][add_y] == 1:
        return
    for xx in range(3):
        for yy in range(3):
            turn_if_not_one(add_x-1+xx,add_y-1+yy)
    unlocked_arr[add_x][add_y] = 1

    if screen_rect.w//squ_size + screen_x//squ_size < add_x+1:
        screen_rect.w  += squ_size
        #+1 bs pga bar
        for i in range(screen_rect.h//squ_size):
            turn_if_not_one(screen_rect.w//squ_size + screen_x//squ_size-1 ,   bar_y//squ_size + i)

        
    elif screen_x//squ_size > add_x:
        screen_x -= squ_size
        screen_rect.w += squ_size
        for i in range(screen_rect.h//squ_size):
            turn_if_not_one(screen_x//squ_size,bar_y//squ_size + i)


    if screen_rect.h//squ_size + bar_y//squ_size < add_y+1:
        screen_rect.h += squ_size
        for i in range(screen_rect.w//squ_size):
            turn_if_not_one(screen_x//squ_size+i,bar_y//squ_size+screen_rect.h//squ_size-1)       



        
    elif bar_y // squ_size > add_y:
        screen_rect.h += squ_size
        bar_y -= squ_size
        for i in range(screen_rect.w//squ_size):
            turn_if_not_one(screen_x//squ_size+i,bar_y//squ_size)

    print(screen_rect.w//squ_size)
    update_screen_rect()
    update_bar_rect()
    gen_lines()



def update_bar_rect():
    global bar_x
    global bar_y
    lowest_y = 100
    lowest_x = 100
    for x in range(unlocked_size):
        for y in range(unlocked_size):
            if unlocked_arr[x][y] == 1:
                if y < lowest_y:
                    lowest_y = y
                    lowest_x = x

    bar_y = lowest_y *squ_size
    bar_x = lowest_x *squ_size
    screen_rect.y = bar_y + offset_y
    bar_width = 0
    while unlocked_arr[lowest_x+bar_width][lowest_y] == 1:
        bar_width += 1
    bar_rect.w = bar_width *squ_size
    bar_rect.x = bar_x + offset_x
    bar_rect.y = bar_y + offset_y-30


    ###################



def update_screen_form():
    global screen_x
    global bar_x
    global bar_y
    lowest_y = 100
    lowest_x = 100
    for x in range(unlocked_size):
        for y in range(unlocked_size):
            if unlocked_arr[x][y] == 1:
                if y < lowest_y:
                    lowest_y = y
                    lowest_x = x

    bar_y = lowest_y *squ_size
    bar_x = lowest_x *squ_size
    screen_x = bar_x
    screen_rect.x = bar_x + offset_x
    screen_rect.y = bar_y + offset_y
    bar_width = 0
    while unlocked_arr[lowest_x+bar_width][lowest_y] == 1:
        bar_width += 1
    bar_rect.w = bar_width *squ_size

def gen_lines():
    global lines_arr
    global arrows_data
    global arrows_rects
    arrows_rect = []
    arrows_data = []
    lines_arr = []
    last = 3
    for x in range(unlocked_size):
        for y in range(unlocked_size):
            curr = unlocked_arr[x][y]
            if (curr == 1  and  last == 0):
                lines_arr.append((x*squ_size, y*squ_size,x*squ_size+squ_size, y*squ_size))
                arrows_data.append((x*squ_size+squ_size//2-20, y*squ_size,0))
                arrows_rects.append((pygame.Rect(x*squ_size+squ_size//2-20, y*squ_size,40,14),x,y-1))
            last = curr

    for x in range(unlocked_size):
        for y in range(unlocked_size):
            curr = unlocked_arr[x][y]
            if (curr == 0  and  last == 1):
                lines_arr.append((x*squ_size, y*squ_size,x*squ_size+squ_size, y*squ_size))
                arrows_data.append((x*squ_size+squ_size//2-20, y*squ_size-14,2))
                arrows_rects.append((pygame.Rect(x*squ_size+squ_size//2-20, y*squ_size-14,40,14),x,y))
            last = curr


    for y in range(unlocked_size):
        for x in range(unlocked_size):
            curr = unlocked_arr[x][y]
            if (curr == 0  and  last == 1):
                lines_arr.append((x*squ_size, y*squ_size,x*squ_size, y*squ_size+squ_size))
                arrows_data.append((x*squ_size-14, y*squ_size + squ_size//2-20,3))
                arrows_rects.append((pygame.Rect(x*squ_size-14, y*squ_size + squ_size//2-20,14,40),x,y))
            last = curr

    for y in range(unlocked_size):
        for x in range(unlocked_size):
            curr = unlocked_arr[x][y]
            if (curr == 1  and  last == 0):
                lines_arr.append((x*squ_size, y*squ_size,x*squ_size, y*squ_size+squ_size))
                arrows_data.append((x*squ_size, y*squ_size + squ_size//2-20,1))
                arrows_rects.append((pygame.Rect(x*squ_size, y*squ_size + squ_size//2-20,14,40),x-1,y))
            last = curr



def update_screen_rect():
    screen_rect.x = screen_x + offset_x
    screen_rect.y = bar_y + offset_y

def render_coins():
    coin_text = coin_font.render(str(player_coins), True, (0, 0, 0))
    screen.blit(coin_text,(bar_rect.x+35+1,bar_rect.y +37))
    screen.blit(coin_text,(bar_rect.x+35-1,bar_rect.y +37))
    screen.blit(coin_text,(bar_rect.x+35,bar_rect.y +37+1))
    screen.blit(coin_text,(bar_rect.x+35,bar_rect.y +37-1))

    
    
    coin_text = coin_font.render(str(player_coins), True, (255, 242, 0))
    screen.blit(coin_text,(bar_rect.x+35,bar_rect.y +37))
    
def fill():
    #screen.fill(fuchsia)
    for x in range(unlocked_size):
        for y in range(unlocked_size):
            if unlocked_arr[x][y] == 0:
                pygame.draw.rect(screen, fuchsia, pygame.Rect(x*squ_size + offset_x, y*squ_size + offset_y, squ_size, squ_size))
  
    
    #pygame.draw.rect(screen, win_color, pygame.Rect(bar_rect.x, bar_rect.y, bar_rect.w, 30))

    pygame.draw.rect(screen, fuchsia, pygame.Rect(0, 0, SCREENWIDTH, screen_rect.y))
    pygame.draw.rect(screen, fuchsia, pygame.Rect(0, screen_rect.y, screen_rect.x, screen_rect.h))
    pygame.draw.rect(screen, fuchsia, pygame.Rect(0,screen_rect.y+screen_rect.h, SCREENWIDTH, SCREENHEIGHT-(screen_rect.y+screen_rect.h)))
    pygame.draw.rect(screen, fuchsia, pygame.Rect(screen_rect.x+screen_rect.w, screen_rect.y, SCREENWIDTH-(screen_rect.x+screen_rect.w), screen_rect.h))

    #balnk screen
    #pygame.draw.rect(screen, (0,255,255), pygame.Rect(bar_rect.x+1, bar_rect.y+30, bar_rect.w-2, bar_rect.h-31))


    #OUTLINE
    for data in arrows_data:
        arrow_sprite.bilt(screen,data[0]+offset_x,data[1]+offset_y,data[2],pygame.mouse.get_pos())

    
    pygame.draw.rect(screen, win_color, pygame.Rect(bar_rect.x, bar_rect.y, bar_rect.w+1, bar_rect.h),1)
    for line in lines_arr:
        pygame.draw.line(screen,win_color, (line[0]+offset_x,line[1]+offset_y),(line[2]+offset_x,line[3]+offset_y))

    #bar
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(bar_rect.x+1, bar_rect.y+1, bar_rect.w-1, bar_rect.h))

    #icon
    screen.blit(icon, (bar_rect.x + 9, bar_rect.y + 8))

    render_coins()
    #text
    screen.blit(title_text,(bar_rect.x+35,bar_rect.y +7))

    #X
    if pygame.Rect(bar_rect.x + bar_rect.w - 50,bar_rect.y,50,30).collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (230,0,0),pygame.Rect(bar_rect.x + bar_rect.w - 45,bar_rect.y+1,45,30))

        pygame.draw.line(screen, (255,255,255), (bar_rect.x + bar_rect.w - 28, bar_rect.y+11) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+19),2  )
        pygame.draw.line(screen, (255,255,255), (bar_rect.x + bar_rect.w - 28, bar_rect.y+19) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+11),2  )
    else:
        pygame.draw.line(screen, (0,0,0), (bar_rect.x + bar_rect.w - 28, bar_rect.y+11) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+19),2  )
        pygame.draw.line(screen, (0,0,0), (bar_rect.x + bar_rect.w - 28, bar_rect.y+19) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+11),2  )
    #square
    pygame.draw.rect(screen, (200,200,200), pygame.Rect(bar_rect.x+bar_rect.w-75, bar_rect.y+11,10, 10),1)
    pygame.draw.line(screen, (200,200,200), (bar_rect.x + bar_rect.w - 120, bar_rect.y+15) , (bar_rect.x + bar_rect.w - 111, bar_rect.y+15)  )


def fill_clean():
    #screen.fill(fuchsia)
    for x in range(unlocked_size):
        for y in range(unlocked_size):
            if unlocked_arr[x][y] == 0:
                pygame.draw.rect(screen, fuchsia, pygame.Rect(x*squ_size + offset_x, y*squ_size + offset_y, squ_size, squ_size))
  
    
    #pygame.draw.rect(screen, win_color, pygame.Rect(bar_rect.x, bar_rect.y, bar_rect.w, 30))

    pygame.draw.rect(screen, fuchsia, pygame.Rect(0, 0, SCREENWIDTH, screen_rect.y))
    pygame.draw.rect(screen, fuchsia, pygame.Rect(0, screen_rect.y, screen_rect.x, screen_rect.h))
    pygame.draw.rect(screen, fuchsia, pygame.Rect(0,screen_rect.y+screen_rect.h, SCREENWIDTH, SCREENHEIGHT-(screen_rect.y+screen_rect.h)))
    pygame.draw.rect(screen, fuchsia, pygame.Rect(screen_rect.x+screen_rect.w, screen_rect.y, SCREENWIDTH-(screen_rect.x+screen_rect.w), screen_rect.h))

    
    pygame.draw.rect(screen, win_color, pygame.Rect(bar_rect.x, bar_rect.y, bar_rect.w+1, bar_rect.h),1)
    for line in lines_arr:
        pygame.draw.line(screen,win_color, (line[0]+offset_x,line[1]+offset_y),(line[2]+offset_x,line[3]+offset_y))

    #bar
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(bar_rect.x+1, bar_rect.y+1, bar_rect.w-1, bar_rect.h))

    #icon
    screen.blit(icon, (bar_rect.x + 9, bar_rect.y + 8))
    
    screen.blit(title_text,(bar_rect.x+35,bar_rect.y +7))

    #X
    if pygame.Rect(bar_rect.x + bar_rect.w - 50,bar_rect.y,50,30).collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (230,0,0),pygame.Rect(bar_rect.x + bar_rect.w - 45,bar_rect.y+1,45,30))

        pygame.draw.line(screen, (255,255,255), (bar_rect.x + bar_rect.w - 28, bar_rect.y+11) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+19),2  )
        pygame.draw.line(screen, (255,255,255), (bar_rect.x + bar_rect.w - 28, bar_rect.y+19) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+11),2  )
    else:
        pygame.draw.line(screen, (0,0,0), (bar_rect.x + bar_rect.w - 28, bar_rect.y+11) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+19),2  )
        pygame.draw.line(screen, (0,0,0), (bar_rect.x + bar_rect.w - 28, bar_rect.y+19) , (bar_rect.x + bar_rect.w - 20, bar_rect.y+11),2  )
    #square
    pygame.draw.rect(screen, (200,200,200), pygame.Rect(bar_rect.x+bar_rect.w-75, bar_rect.y+11,10, 10),1)
    pygame.draw.line(screen, (200,200,200), (bar_rect.x + bar_rect.w - 120, bar_rect.y+15) , (bar_rect.x + bar_rect.w - 111, bar_rect.y+15)  )

    
def check_exit(event):
    if pygame.Rect(bar_rect.x + bar_rect.w - 50,bar_rect.y,50,30).collidepoint(event.pos):
        pygame.quit()

def check_shop(event):
    global player_coins
    if shop.rect.collidepoint((player.rect.x+standard_player_size//2,player.rect.y+standard_player_size//2)):
        #pick:
        if pygame.Rect(shop.rect.x-30, shop.rect.y+10, 120, 100).collidepoint(pygame.mouse.get_pos()):
            if player.axe_lvl < 5:
                if player_coins >= pick_prices[player.axe_lvl]:
                    player_coins -= pick_prices[player.axe_lvl]
                    player.axe_lvl += 1


        if pygame.Rect(shop.rect.x-30, shop.rect.y+140, 120, 100).collidepoint(pygame.mouse.get_pos()):
            if player.sword_lvl < 5:
                if player_coins >= sword_prices[player.sword_lvl]:
                    player_coins -= sword_prices[player.sword_lvl]
                    player.sword_lvl += 1

clock = pygame.time.Clock()

i = 0
update_screen_form()

#add_squ(7,10)
#add_squ(12,12)
#add_squ(13,13)
#add_squ(13,13)
#add_squ(13,13)
##add_squ(7,10)

all_sprites_list = pygame.sprite.Group()
all_stones = pygame.sprite.Group()
other_dudes = pygame.sprite.Group()


shop_pick = sprites.shop_pick()
shop_sword = sprites.shop_sword()
player = sprites.dude((255,0,0), standard_player_size,(unlocked_size//2)*squ_size,standard_player_speed)
drill_example = sprites.drill((unlocked_size//2)*squ_size+100,(unlocked_size//2)*squ_size+100,2)
arrow_sprite = sprites.add_arrow()
pick = sprites.pickaxe()
sword = sprites.sword()
shop = sprites.shop((unlocked_size//2)*squ_size-squ_size,(unlocked_size//2)*squ_size-squ_size)

all_sprites_list.add(drill_example)
all_sprites_list.add(shop)
all_sprites_list.add(player)







update_screen_rect()
update_bar_rect()
gen_lines()
all_sprites_list.update(offset_x, offset_y)
attacking = False
sword_active = True
shop_open = False



def data_from_server(s,a):
    while True:

        data = pickle.loads(s.recv(20489))

        index = 0
        index_update = 0
        for item in data:
            #print(data)
            #print(item)
            
            if item[0] == 1:
                sprite = other_dudes.sprites()[index]
                sprite.x = item[1]
                sprite.y = item[2]
                sprite.attacking = item[3]
                sprite.sword_active = item[4]
                sprite.hp = item[5] 
                sprite.looking = item[6]
                sprite.axe_lvl = item[7]
                sprite.sword_lvl = item[8]
                index += 1
                
            elif item[0] == 6:
                sprite = other_dudes.sprites()[index]
                sprite.uid = item[1]
                sprite.color1 = item[2]
                sprite.color2 = item[3]
                sprite.hp = item[4]
                index_update += 1

            elif item[0] == 7:
                player.hp = item[1]
                
            elif item[0] == 2:
                all_stones.add(sprites.stone(item[1],item[2],item[3]))
                
        #sprites.stone_s((unlocked_size//2)*squ_size,(unlocked_size//2)*squ_size,2)
            elif item[0] == 5:
                print("ADDED DUDE")
                player2 = sprites.other_dude(item[3], item[4], item[5],item[1],item[2],item[6])
                other_dudes.add(player2)
                all_sprites_list.add(player2)

            else:
                print(item)


thread.start_new_thread(data_from_server, (s,0))

player.hp = -1
refreshed_squ = 1
username_input = sprites.InputBox((unlocked_size//2)*squ_size,(unlocked_size//2)*squ_size-20,200,40)
while not done:
    pickle_send_arr = []
    while player.hp < 0:
        if refreshed_squ == 0:
            for a in range(unlocked_size):
                for b in range(unlocked_size):
                    unlocked_arr[a][b] = 2
            #print(unlocked_arr)
            for a in range(start_size+2):
                for b in range(start_size+2):
                    unlocked_arr[unlocked_size//2-start_size//2+a-1][unlocked_size//2-start_size//2+b-1] = 0
                    
            for a in range(start_size):
                for b in range(start_size):
                    unlocked_arr[unlocked_size//2-start_size//2+a][unlocked_size//2-start_size//2+b] = 1
            screen_rect = pygame.rect.Rect(100,100,start_size*squ_size,start_size*squ_size)
            bar_rect = pygame.rect.Rect(100,100,200,30)
            refreshed_squ = 1
            update_screen_rect()
            update_bar_rect()
            gen_lines()
                    

        for event in pygame.event.get():
            username_input.handle_event(event)
            if event.type == pygame.QUIT:
                done = True
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username_input.text == "":
                        username_input.text = "Idiot_without_name"
                    player.uid = username_input.text
                    username_input.text = ""
                    player.hp = 100
                    pickle_send_arr.append([2,player.uid,player.color1,player.color2])
                    player.x = (unlocked_size//2)*squ_size
                    player.y = (unlocked_size//2)*squ_size
                    player.last_x = (unlocked_size//2)*squ_size
                    player.last_y = (unlocked_size//2)*squ_size
   
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    attacking = True
                    check_exit(event)
                    check_shop(event)
                    if bar_rect.collidepoint(event.pos):
                        screen_moving = True
                        start_x, start_y = pyautogui.position()
                        start_x += -offset_x
                        start_y += -offset_y

                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    screen_moving = False
        if screen_moving:
            mouse_x, mouse_y = pyautogui.position()
            offset_x = mouse_x - start_x
            offset_y = mouse_y - start_y
            update_screen_rect()
            update_bar_rect()

        
        
        i += 1
        loading_screen.pattern(screen,(255,255,255),(0,0,0),screen_rect.x,screen_rect.y,screen_rect.w,screen_rect.h,inited,arrow_size, i)
        fill_clean()
        username_input.update(offset_x, offset_y)
        username_input.draw(screen,i)
        pygame.display.update()
        clock.tick(60)
        #MÅ SENDE OG READE FRA SOCKET I DENNE



    
    shop_open = False
    refreshed_squ = 0
    i += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                sword_active = not sword_active



        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                attacking = True
                check_exit(event)
                check_shop(event)
                if bar_rect.collidepoint(event.pos):
                    screen_moving = True
                    start_x, start_y = pyautogui.position()
                    start_x += -offset_x
                    start_y += -offset_y


                for arr_rect_arr in arrows_rects:
                    arr_rect = arr_rect_arr[0]
                    if pygame.Rect(arr_rect.x+offset_x,arr_rect.y+offset_y,arr_rect.w,arr_rect.h).collidepoint(event.pos):
                        if player_coins >= 500:
                            if unlocked_arr[arr_rect_arr[1]][arr_rect_arr[2]] != 1:
                                player_coins -= 500
                                add_squ(arr_rect_arr[1],arr_rect_arr[2])

                                ##############XXXXXXXXXx
##                                if bar_rect.y + offset_y < 0:
##                                    offset_y = -bar_rect.y
##                                    update_screen_rect()
##                                    update_bar_rect()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:            
                screen_moving = False
                attacking = False


    if screen_moving:
        mouse_x, mouse_y = pyautogui.position()
        offset_x = mouse_x - start_x
        offset_y = mouse_y - start_y
        update_screen_rect()
        update_bar_rect()

    if bar_rect.y < 0:
        offset_y -= bar_rect.y
        update_screen_rect()
        update_bar_rect()
        
        
    keys = pygame.key.get_pressed() 

    if keys[pygame.K_a]:
        player.move(-1,0)
        
        
    if keys[pygame.K_d]:
        player.move(1,0)

    if keys[pygame.K_w]:
        player.move(0,-1)

    if keys[pygame.K_s]:
        player.move(0,1)

 
    other_dudes.update(offset_x,offset_y)
    player.update(offset_x, offset_y)
    
    
    if unlocked_arr[int((player.rect.x - offset_x)//squ_size)][int((player.rect.y - offset_y)//squ_size)] != 1 or unlocked_arr[int((player.rect.x - offset_x + player.size)//squ_size)][int((player.rect.y - offset_y + player.size)//squ_size)] != 1:
        player.back()

    
    all_sprites_list.update(offset_x, offset_y)
    all_stones.update(offset_x,offset_y)


    
    #screen.fill(fuchsia)  # Transparent background

    
    screen.fill((255,255,255))
    all_stones.draw(screen)
    all_sprites_list.draw(screen)
    other_dudes.draw(screen)
    for dude in other_dudes:
        dude.draw_name(screen)
    #print(len(other_dudes))
    
    v2 = (0,1)
    for dude in other_dudes:
        if dude.attacking:
            v2 = pygame.math.Vector2(dude.looking[0],dude.looking[1])
            try:
                v2.scale_to_length(standard_player_size//2+7)
            except:
                v2 = pygame.math.Vector2(0,1)
            if dude.sword_active:
                sword.bilt(screen,dude.rect.x+standard_player_size//2,dude.rect.y+standard_player_size//2,v2,dude.sword_lvl,i)
                if i%20 == 0:
                    
                    if player.rect.collidepoint((dude.rect.x+standard_player_size//2 - v2[0],dude.rect.y+standard_player_size//2 - v2[1])):
                        player.hp += -2**dude.sword_lvl
                    else:
                        v2.scale_to_length(standard_player_size//2+30)
                        if player.rect.collidepoint((dude.rect.x+standard_player_size//2 - v2[0],dude.rect.y+standard_player_size//2 - v2[1])):
                            player.hp += -2**dude.sword_lvl
            else:
                pick.bilt(screen,dude.rect.x+standard_player_size//2,dude.rect.y+standard_player_size//2,v2,dude.axe_lvl,i)
        
    if attacking:
        v2 = pygame.math.Vector2(player.rect.x+standard_player_size//2-pygame.mouse.get_pos()[0], player.rect.y+standard_player_size//2-pygame.mouse.get_pos()[1])
        try:
            v2.scale_to_length(standard_player_size//2+7)
        except:
            v2 = pygame.math.Vector2(0,1)
        if sword_active:
            sword.bilt(screen,player.rect.x+standard_player_size//2,player.rect.y+standard_player_size//2,v2,player.sword_lvl,i)
        else:
            pick.bilt(screen,player.rect.x+standard_player_size//2,player.rect.y+standard_player_size//2,v2,player.axe_lvl,i)
            
        if sword_active == False:
            if i % 30 == 0:
                for sprite in all_stones:
                    
                    if sprite.rect.collidepoint((player.rect.x+standard_player_size//2 - v2[0],player.rect.y+standard_player_size//2 - v2[1])):
                        player_coins += (2**sprite.lvl)*(2**player.axe_lvl)
                #print("HI")
    #loading_screen.pattern(screen,(255,255,255),(0,0,0),screen_rect.x,screen_rect.y,screen_rect.w,screen_rect.h,inited,100, i)
    fill()
    #player.set_hp(50)
    ##pygame.draw.rect(screen, (255,200,200), pygame.Rect(i%1000,i%1000, 100, 100))

    #pygame.draw.rect(screen, dark_red, pygame.Rect(30, 30, 60, 60))
    
    if shop.rect.collidepoint((player.rect.x+standard_player_size//2,player.rect.y+standard_player_size//2)):
        
        pygame.draw.rect(screen, (200,0,0), pygame.Rect(shop.rect.x-50, shop.rect.y-50, 300, 300),0,10)
        pygame.draw.rect(screen, (100,0,0), pygame.Rect(shop.rect.x-50, shop.rect.y-50, 300, 300),5,10)

        welcom_text = shop_font.render('To quit the shop, walk out', True, (0,0,0))
        screen.blit(welcom_text, (shop.rect.x-39, shop.rect.y-45))
        screen.blit(welcom_text, (shop.rect.x-41, shop.rect.y-45))
        screen.blit(welcom_text, (shop.rect.x-40, shop.rect.y-44))
        screen.blit(welcom_text, (shop.rect.x-40, shop.rect.y-46))
        welcom_text = shop_font.render('To quit the shop, walk out', True, (255,242,0))
        screen.blit(welcom_text, (shop.rect.x-40, shop.rect.y-45))

        
        pygame.draw.rect(screen, (200,100*(not pygame.Rect(shop.rect.x-30, shop.rect.y+10, 120, 100).collidepoint(pygame.mouse.get_pos())),100), pygame.Rect(shop.rect.x-30, shop.rect.y+10, 120, 100),0,10)
        pygame.draw.rect(screen, (100,50,50), pygame.Rect(shop.rect.x-30, shop.rect.y+10, 120, 100),5,10)
        
        if player.axe_lvl  < 5:
            shop_pick.blit(screen,shop.rect.x+5,shop.rect.y+28,player.axe_lvl+1)

            
            welcom_text = shop_font.render(str(pick_prices[player.axe_lvl])+' coins:', True, (0,0,0))
            screen.blit(welcom_text, (shop.rect.x-35, shop.rect.y-15))
            screen.blit(welcom_text, (shop.rect.x-37, shop.rect.y-15))
            screen.blit(welcom_text, (shop.rect.x-36, shop.rect.y-16))
            screen.blit(welcom_text, (shop.rect.x-36, shop.rect.y-14))
            welcom_text = shop_font.render(str(pick_prices[player.axe_lvl])+ ' coins:', True, (255,242,0))
            screen.blit(welcom_text, (shop.rect.x-36, shop.rect.y-15))

        pygame.draw.rect(screen, (200,100*(not pygame.Rect(shop.rect.x-30, shop.rect.y+140, 120, 100).collidepoint(pygame.mouse.get_pos())),100), pygame.Rect(shop.rect.x-30, shop.rect.y+140, 120, 100),0,10)
        pygame.draw.rect(screen, (100,50,50), pygame.Rect(shop.rect.x-30, shop.rect.y+140, 120, 100),5,10)
        
        if player.sword_lvl < 5:
            shop_sword.blit(screen,shop.rect.x+5,shop.rect.y+125,player.sword_lvl+1)
            
            
            welcom_text = shop_font.render(str(sword_prices[player.sword_lvl])+ ' coins:', True, (0,0,0))
            screen.blit(welcom_text, (shop.rect.x-35, shop.rect.y+130-15))
            screen.blit(welcom_text, (shop.rect.x-37, shop.rect.y+130-15))
            screen.blit(welcom_text, (shop.rect.x-36, shop.rect.y+130-16))
            screen.blit(welcom_text, (shop.rect.x-36, shop.rect.y+130-14))
            welcom_text = shop_font.render(str(sword_prices[player.sword_lvl])+ ' coins:', True, (255,242,0))
            screen.blit(welcom_text, (shop.rect.x-36, shop.rect.y+130-15))



        pygame.draw.rect(screen, (200,100*(not pygame.Rect(shop.rect.x+110, shop.rect.y+10, 120, 100).collidepoint(pygame.mouse.get_pos())),100), pygame.Rect(shop.rect.x+110, shop.rect.y+10, 120, 100),0,10)
        pygame.draw.rect(screen, (100,50,50), pygame.Rect(shop.rect.x+110, shop.rect.y+10, 120, 100),5,10)


        welcom_text = shop_font.render('1000 coins:', True, (0,0,0))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y-15))
        screen.blit(welcom_text, (shop.rect.x+112, shop.rect.y-15))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y-16))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y-14))
        welcom_text = shop_font.render('1000 coins:', True, (255,242,0))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y-15))

        

        pygame.draw.rect(screen, (200,100*(not pygame.Rect(shop.rect.x+110, shop.rect.y+140, 120, 100).collidepoint(pygame.mouse.get_pos())),100), pygame.Rect(shop.rect.x+110, shop.rect.y+140, 120, 100),0,10)
        pygame.draw.rect(screen, (100,50,50), pygame.Rect(shop.rect.x+110, shop.rect.y+140, 120, 100),5,10)
        
        welcom_text = shop_font.render('500 coins:', True, (0,0,0))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y+130-15))
        screen.blit(welcom_text, (shop.rect.x+112, shop.rect.y+130-15))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y+130-16))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y+130-14))
        welcom_text = shop_font.render('500 coins:', True, (255,242,0))
        screen.blit(welcom_text, (shop.rect.x+110, shop.rect.y+130-15))
        

    pygame.display.update()
    pickle_send_arr.append([1,player.x,player.y,attacking,sword_active,player.hp,(v2[0],v2[1]),player.sword_lvl,player.axe_lvl])
    s.send(pickle.dumps((pickle_send_arr)))
    clock.tick(60)
    
pygame.quit()
