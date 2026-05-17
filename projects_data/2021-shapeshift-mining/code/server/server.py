import socket, pickle
import _thread as thread
from time import time
map_size = 40
squ_size = 100
player_start_size = 50
player_speed = 3
start_size = 4


players = []
stationary_items_arr = []
update = 0

#1 =  update player
#2 = stone
#3 = miner
#4 = heal_thing
#5 = player
#6 = player_update
#7 = hp_update


stationary_items_arr.append([2,(map_size//2)*squ_size,(map_size//2)*squ_size,0])

class player():
    def __init__(self,uid, color1,color2):
        self.active = 1
        self.hp = 100
        self.x = 0
        self.y = 0
        self.color1 = color1
        self.color2 = color2
        self.uid = uid
        self.size = player_start_size
        self.attacking = False
        self.sword_active = False
        self.coins = 0
        self.looking = (0,1)
        self.axe_lvl = 0
        self.sword_lvl = 0

    def update(x,y,a,b,dmg):
        self.x = x
        self.y = y
        self.attacking = a
        self.sword = b
        self.hp += -dmg


        


def on_new_client(clientsocket,addr,index):
    global update
    last_update = time()
    current_player_known_count = 1
    clientsocket.send(pickle.dumps(([map_size,start_size, squ_size,player_speed, player_start_size])))

    temp_arr =[]

        
    clientsocket.send(pickle.dumps((stationary_items_arr)))
    while players[index].active == 1:
        try:
            msg = clientsocket.recv(1024)
        except Exception as e:
            print(e)
            
        #print (addr, '>>', pickle.loads(msg))
        arr = pickle.loads(msg)
        for item in arr:
            if item[0] == 1:
                players[index].x = item[1]
                players[index].y = item[2]
                players[index].attacking = item[3]
                players[index].sword_active = item[4]
                players[index].hp = item[5]
                players[index].looking = item[6]
                players[index].sword_lvl = item[7]
                players[index].axe_lvl = item[8]
            if item[0] == 2:
                players[index].hp = 100
                players[index].uid = item[1]
                players[index].color1 = item[2]
                players[index].color2 = item[3]
                update = time()
        #print(len(players))
        arr = []
        if len(players) > current_player_known_count:
            for i in range(len(players)-current_player_known_count):
                print(current_player_known_count)
                current_player_known_count += 1
                arr.append([5,players[i].x,players[i].y,players[i].color1,players[i].color2,player_start_size,players[i].uid])

        if last_update < update:
            last_update = time()
            for i in range(len(players)):
                if i != index:
                    arr.append([6, players[i].uid, players[i].color1, players[i].color2, players[i].hp])

            print("UPDATED")
        
        for i in range(len(players)):
            if i != index:
                
                arr.append([1,players[i].x,players[i].y,players[i].attacking,players[i].sword_active,players[i].hp,players[i].looking,players[i].axe_lvl,players[i].sword_lvl])
                
        arr.append([7, players[index].hp])
        try:
            clientsocket.send(pickle.dumps((arr)))
        except Exception as e:
            print(e)
            players[index].active = 0
            players[index].hp = -1
            update = time()
        
    #clientsocket.close()
    print("SHUTDOWQN SUCSESS")


s = socket.socket()

host = ''
port = 12345

print("STARTED")

s.bind((host,port))
s.listen(5)

while True:
    c, addr = s.accept()
    print ('Got connection from', addr)
    msg = c.recv(1024)
    print(msg)
    arr = pickle.loads(msg)
    got = -1
    index = 0
    for item in players:
        if item.active == 0:
            if got == -1:
                item.active = 1
                item.hp = 100
                item.uid = arr[0]
                item.color1 = arr[1]
                item.color2 = arr[2]
                update = time()
                got = index
                
        index += 1
                

    if got == -1:
        got = len(players)
        players.append(player(arr[0],arr[1],arr[2]))
    print(len(players))
    update = time()

    c.settimeout(5)
    thread.start_new_thread(on_new_client, (c,addr,got))


s.close()
