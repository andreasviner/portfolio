import json
import requests
import time


def make_arr_color(string):
    all_data = list(map(''.join, zip(*[iter(string)]*6)))
    arr = []
    for item in all_data:
        arr.append([int(item[:2],16),int(item[2:4],16),int(item[4:6],16)])
    return arr


    
def color_valg(arr, valg):
    curr = 0
    arr1  = []
    for index in valg[:16]:
        arr1.append(arr[int(index)+curr])
        curr += 4

    arr2 = []
    curr = 0
    for index in valg[16:20]:
        arr2.append(arr1[int(index)+curr])
        curr += 1
    return [arr, arr1,arr2,arr2[int(valg[-1])]]

def get_ti(ide, data):
    for item in data:
        if item.split("AT")[0] == ide:
            return item.split("AT")[1], item.split("AT")[2]
    return "0", "0"

def get_al(ide, data):
    for item in data:
        age = 0
        if item.split("A")[0] == ide:
            if item.split("A")[1] != '':
                age = item.split("A")[1]
            return age, item.split("A")[2], item.split("A")[3]
    return "0", "30", "u"

def get_rest(ide, data):
    for item in data:
        try:
            if item.split("H")[2] == ide:
                time = item.split("H")[0][1:].split("A")
                valg = item.split("H")[1]
                color = color_valg(make_arr_color(item.split("H")[3]), valg)
                return time, valg, color
                
        except:
            pass
    return "no data", "no data", "no data"

def refresh():
    print("Requesting data from server")
    arr1 = requests.get("https://andreas.informatikk5.net/data/first.txt").text.split(",")
    arr2 = requests.get("https://andreas.informatikk5.net/data/second.txt").text.split(",")
    arr3 = requests.get("https://andreas.informatikk5.net/data/seen.txt").text.split(",")
    print("Got data")
    ids = []
    for item in arr2:
        try:
            if len(item.split("H")[2]) > 0:
                if item.split("H")[2].isdigit():
                    ids.append(item.split("H")[2])
        except:
            pass

    a = len(ids)
    ids = list(dict.fromkeys(ids))
    
    ids2 = []
    for item in arr1:
        try:
            if len(item.split("A")[0]) > 0:
                ids2.append(item.split("A")[0])
        except:
            pass
    ids2 = list(dict.fromkeys(ids2))

    ids3 = []
    for item in arr3:
        try:
            if len(item.split("AT")[0]) > 0:
                ids3.append(item.split("AT")[0])
        except:
            pass

    
    
    ids3 = list(dict.fromkeys(ids3))
    print(str(a-len(ids)) + " duplikate har blitt fjernet")
    print(str(len(ids3)) + " Forskellige ider har sett mailen")
    print(str(len(ids2)) + " Froskellige ider har begynt testen")
    print(str(len(ids)) + " Forskellige ider har gjort hele testen")

    finarr = []
    for idn in ids:
        temp = []
        temp.append(idn)
        time, ip = get_ti(idn, arr3)
        temp.append(time)
        temp.append(ip)

        age, mood, gen = get_al(idn, arr1)
        temp.append(age)
        temp.append(mood)
        temp.append(gen)

        tider, valg, farger = get_rest(idn, arr2)
        temp.append(valg)
        temp.append(tider)
        temp.append(farger)
        finarr.append(temp)


    with open("save.ligma", "w") as file:
        file.write(json.dumps(finarr))
    print("Lagret ny data")
def count():
    print("Requesting data from server")
    arr1 = requests.get("https://andreas.informatikk5.net/data/first.txt").text.split(",")
    arr2 = requests.get("https://andreas.informatikk5.net/data/second.txt").text.split(",")
    arr3 = requests.get("https://andreas.informatikk5.net/data/seen.txt").text.split(",")
    print("Got data")
    ids = []
    for item in arr2:
        try:
            if len(item.split("H")[2]) > 0:
                if item.split("H")[2].isdigit():
                    ids.append(item.split("H")[2])
        except:
            pass

    a = len(ids)
    print(str(len(ids)) + " ikke forskellige ids har tatt testen")
    ids = list(dict.fromkeys(ids))
    
    ids2 = []
    for item in arr1:
        try:
            if len(item.split("A")[0]) > 0:
                ids2.append(item.split("A")[0])
        except:
            pass
    print(str(len(ids2)) + " ikke forskellige ids har begynt testen")
    ids2 = list(dict.fromkeys(ids2))

    ids3 = []
    for item in arr3:
        try:
            if len(item.split("AT")[0]) > 0:
                ids3.append(item.split("AT")[0])
        except:
            pass

    
    print(str(len(ids3)) + " ikke forskellige ids har sett mailen\n")
    ids3 = list(dict.fromkeys(ids3))
    print(str(a-len(ids)) + " duplikate har blitt fjernet")
    print(str(len(ids3)) + " Forskellige ider har sett mailen")
    print(str(len(ids2)) + " Froskellige ider har begynt testen")
    print(str(len(ids)) + " Forskellige ider har gjort hele testen")

from os import mkdir

def backup():
    path = str(time.time())
    mkdir(path)
    with open(path + "/first.txt", "w") as file:
        file.write(requests.get("https://andreas.informatikk5.net/data/first.txt").text)
    with open(path + "/second.txt", "w") as file:
        file.write(requests.get("https://andreas.informatikk5.net/data/second.txt").text)
    with open(path + "/seen.txt", "w") as file:
        file.write(requests.get("https://andreas.informatikk5.net/data/seen.txt").text)
    print("backup complete")
        
    
def nutral_refresh():
    print("Requesting data from server")
    arr1 = requests.get("https://andreas.informatikk5.net/data/first.txt").text.split(",")
    arr2 = requests.get("https://andreas.informatikk5.net/data/second.txt").text.split(",")
    arr3 = requests.get("https://andreas.informatikk5.net/data/seen.txt").text.split(",")
    print("Got data")
    ids = []
    for item in arr2:
        try:
            if len(item.split("H")[2]) > 0:
                ids.append(item.split("H")[2])
        except:
            pass


    
    ids2 = []
    for item in arr1:
        try:
            if len(item.split("A")[0]) > 0:
                ids2.append(item.split("A")[0])
        except:
            pass

    ids3 = []
    for item in arr3:
        try:
            if len(item.split("AT")[0]) > 0:
                ids3.append(item.split("AT")[0])
        except:
            pass

    

    print(str(len(ids3)) + " (ikke forskellige) har sett mailen")
    print(str(len(ids2)) + " (ikke forskellige) har begynt testen")
    print(str(len(ids)) + " (ikke forskellige) har gjort hele testen")

    finarr = []
    for idn in ids:
        temp = []
        temp.append(idn)
        time, ip = get_ti(idn, arr3)
        temp.append(time)
        temp.append(ip)

        age, mood, gen = get_al(idn, arr1)
        temp.append(age)
        temp.append(mood)
        temp.append(gen)

        tider, valg, farger = get_rest(idn, arr2)
        temp.append(valg)
        temp.append(tider)
        temp.append(farger)
        finarr.append(temp)

    with open("save.ligma", "w") as file:
        file.write(json.dumps(finarr))
        
    return finarr
        

        
help_str = """
først import andy

så bruk andy.refresh() for å lagre ny data fra webserveren. (krever internett)
denne komandoen krever at du laster ned rudnt 1.2mb data fra serveren, så ikke spam den for mye (en gang per skript er MER en nokk).

for å få tak i dataen må du først lage et data object, dette gjør du ved å skrive
data = andy.data()
Dette dataobjektet har nå lagret all dataen fra undersøkelsen.

For å få tak i all dataen skriv:
data.data
dette vill gi deg en array med all dataen, så i et skript vill det se slik ut:
data = andy.data()
array1 = data.data

arrayen du får fra data.data er sortert slik etter tiden de tokk testen. Arryen ineholder flere subbaryer, hvor hver subbary er et svar.
subbaryene ser slike ut [ider, tid, ip, alder, mood, gender, valg, tider, farger].

Her er litt info om hver:

ider:
    Alle som tar testen får en id, ider er satt etter hvilken posisjon di har i mailsene jeg sendte.
    Dette fører til at det naturlig blir de som har en lav id har navn tidlig i alphabetet, og de med høy id har motstatt.

tid:
    Dette er tidspunktet de begynte testen på. Tidspunktet har samme verdi som du ville fått hvis du hadde skrevet time.tim() i python når de tokk testen. Noen vill ha 'no data' her, dette er fordi de opnet mailen fra en broweser vi ikke kan tracke. 

ip:
    ipen til de som tokk testen.  Noen vill ha 'no data' her, dette er fordi de opnet mailen fra en broweser vi ikke kan tracke.

alder:
    Alderen de selv satt når de tokk testen, de som ikke satt no tall hvill ha verdien 0, de kan også ha veldig høye tall, som 420 siden de satt alder selv.

mood:
    humøret de satt når de tokk testen. 0 er gladest, 60 er surerst.

gender:
    u er uderfienert. g er gutt, og j er jente.

valg:
    valgene de tokk under testen. Hvis de trykket på første rute, la jeg på en 0, andre (øverst til høyre) 1, tredje (nedesrst til venstre) 2, og fjerde 3.

tider:
    Tider er en  liste over tiden i millisekunder det tokk for å ta testen. Tiden blir lagret som en liste hvor tiden fra start ble lagt til for hvert spørsmål. Den siste verdien i testen vill derfor ha tiden det tokk og ta hele testen. Tiden ble målt i millisekunder.

farger:
    Farger vill gi en liste med data om fargene valgt. listen vill se slik ut [[liste over alle fargene de hadde valg mellom], [liste over fargene valgt],[liste over fargene valgt av de valgte fargene], siste farge valgt]
    farger[-1] vill dermed altid gi den fargen di hadde til slutt. I eksemplet jeg sendte med ser du at jeg har brukt dette, samt gjort det om til rgb verdier, fra hex.


Hvis du ikke vill ha all daten har du noen andre valg også.

data.ider:
    gir en liste med idene som har fulført testen.

data.tid:
    gir en liste med når de som har fulført testen begynte testen.

data.ip:
    gir en liste med ipen til de som har fulført testen.

data.alder:
    gir en liste med alderen til de som har fulført testen (Obs. de satt den selv).

data.mood:
    gir en liste med humøret til de som tokk testen, 0 er glad, 60 er surerst.

data.gender:
    gir en liste av kjønn til de som tokk testen, u er underfined, j er jete og g er gutt.

data.valg:
    Gir en liste av valg de tokk under testen gitt som en liste foreks: 0123010203102

data.tider:
    gir en liste over tiden som hadde gått når de trykket.

data.farger:
    gir en liste over alle fargene som var valgt under undersøkelsen. i listen du får vill det være subbarrays med denne formen [[alle fargene de fikk valg om],[farger de valgte første gang],[farger de valgte andre gang], siste farge]
    
data her også noen innebygde funskjoner:

data.refresh():
    gjør det samme som andy.refresh(), men updater også data arryen (noe andy.refresh() ikke gjør) du kan update data arryen ved å ta data.update_data() og lage en ny data array (array2 = data.data).

data.sort():
    sorterer dataen etter hvilen index du gir den (data.sort(0) sorterer etter ider, data.sort(1) sorterer etter tid, data.sort(3) sorterer etter alder, data.sort(4) sorterer etter mood, data.sort(6) sorterer ett valg, og data.sort(7) sorterer etter hvor lang tid de brukte. 

data.get_data(id):
    gir deg bare listen over daten fra den iden du vil ha.

data.filter():
    filtrerer bort de dataene du ikke vill ha
    andy.filter_hlep() for mer info!!!!!!!!!!!

data.save():
    lagrer daten i data.data (neste gang du kaller andy.data() vill du opne denne lagrede arryen (kommandoen andy.refresh() vill erstarte den lagrede arryen
"""
        
def help():
    print(help_str)
        

def filter_help():
    print("""filter som fjerner shiit
data.config() for å se filter settingsene som er satt
data.check_if_valid(valg_array) hvis du vill se om en array passer til filteret.

VIKTIG:
data.filter() filtrerer data.data (listen du allerede har fitrert) (andy.refresh() har et filter som filtrer bort blandt annent duplikate ider)
for å ungå dette kan du bruke data.refresh_filter(), da lastes ny data ned fra webserveren og blir bare filtrert med data.filter() (ikke andy.refresh() standard filter)


litt forklaring på hva ting gjør:
sort_need_gender; når den er True må man enten ha valgt jente eller gutt.
sort_min_time; Minst tid de kan ha brukt på hele testen. (målt i millisek)
sort_min_question_time; minst tid de kan ha brukt på ett spørsmål. (målt i millisek)
sort_min_valg; Minste forskellige valg de kan ha tatt, så hvis de bare har trykket 11111111111111111111 blir verdien 1, 22222222222222222 verdien også 1, men 11111111111113 verdien 2 og 123120013132131 verdien 4.

""")


    
    #id, time, ip, alder, humør, gender, valg, tider, farger
#refresh()
        
class data:
    def __init__(self):
        with open("save.ligma", "r") as file:
            x = file.read()
        self.data = json.loads(x)
        self.update_data()

        self.sort_remove_duplicate_ids = True
        self.sort_need_id = True
        self.sort_need_ip = True
        self.sort_need_time = True
        self.sort_age_min = 5
        self.sort_age_max = 68
        self.sort_need_gender = True
        self.sort_min_valg = 2
        self.sort_min_time = 20000
        self.sort_min_question_time = 400
    def config(self):
        print("Du kan endre filtrene ved å sette data.FILTERET_DU_VILL_ENDRE = HVA_DU_VILL")
        print("Foreksempel data.sort_remove_duplicate_ids = False\n\n\nConfigurasjonen du nå bruker:\n")
        print("sort_remove_duplicate_ids " + str(self.sort_remove_duplicate_ids))
        print("sort_need_id = " + str(self.sort_need_id))
        print("sort_need_ip = " + str(self.sort_need_ip))
        print("sort_need_time = " + str(self.sort_need_time))
        print("sort_age_min = " + str(self.sort_age_min))
        print("sort_age_max = " + str(self.sort_age_max))
        print("sort_need_gender = " + str(self.sort_need_gender))
        print("sort_min_valg = " + str(self.sort_min_valg))
        print("sort_min_time = " + str(self.sort_min_time))
        print("sort_min_question_time = " + str(self.sort_min_question_time))
        print("\nandy.filter_help() for mer info")

    
        
    def update_data(self):
        self.ider = [x[0] for x in self.data]
        self.tid = [x[1] for x in self.data]
        self.ip = [x[2] for x in self.data]
        self.alder = [x[3] for x in self.data]
        self.mood = [x[4] for x in self.data]
        self.gender = [x[5] for x in self.data]
        self.valg = [x[6] for x in self.data]
        self.tider = [x[7] for x in self.data]
        self.farger = [x[8] for x in self.data]
    def refresh(self):
        refresh()
        with open("save.ligma", "r") as file:
            x = file.read()
        self.data = json.loads(x)
        self.update_data()
    def get_data(self, ide):
        if type(ide) == int:
            ide = str(ide)
        return self.data[self.ider.index(ide)]

    def check_if_valid(self, arr):
        if self.sort_need_id == True:
            if arr[0].isdigit() == False:
                return False
                
        if self.sort_remove_duplicate_ids == True:
            if arr[0] in [x[0] for x in self.temp_data]:
                return False

        if self.sort_need_ip == True:
            if arr[2] == "0":
                return False

        if self.sort_need_time == True:
            if arr[1] == "0":
                return False
        try:
            if int(arr[3]) < self.sort_age_min:
                return False
        except:
            return False

        if int(arr[3]) > self.sort_age_max:
            return False

        if self.sort_need_gender == True:
            if arr[5] != "g" and arr[5] != "j":
                return False

        if len("".join(set(arr[6]))) < self.sort_min_valg:
            return False

        if int(arr[7][-1]) < self.sort_min_time:
            return False

        for item in arr[7]:
            if int(item) < self.sort_min_question_time:
                return False

        return True

        
            
    
    def sort(self, what):
        
        if what == 1:
            with open("save.ligma", "r") as file:
                x = file.read()
            self.data = json.loads(x)
            self.update_data()
        elif what == 2:
            print("hvordan i granskauen vill du at jeg skal sortere etter ip??")
        elif what == 5:
            print("ork")
        elif what == 8:
            print("no can do boss")
        elif what == 7:
            self.data = sorted(self.data, key=lambda x: int(x[what][-1]), reverse=False)
            self.update_data()
        else:
            self.data = sorted(self.data, key=lambda x: int(x[what]), reverse=False)
            self.update_data()

    def filter(self):
        self.temp_data = []

        for item in self.data:
            if self.check_if_valid(item) == True:
                self.temp_data.append(item)

        print("removed " + str(len(self.data)-len(self.temp_data)) + " that didnt meet requerments, andy.filter_help() for more info")
        self.data = []

        for item in self.temp_data:
            self.data.append(item)
    def save(self):
        with open("save.ligma", "w") as file:
            file.write(json.dumps(self.data))

        
    def refresh_filter(self):
        self.data = nutral_refresh()
        self.filter()
        

