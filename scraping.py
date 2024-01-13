from datetime import datetime
import time
import json
from bs4 import BeautifulSoup
import requests

class IndexScraper:
    def __init__(self):
        self.links = []      # treba mi zasebna lista za pojedinačno otvaranje oglasa
        self.data_gla = {}   # zaglavlje oglasa - treba mi šifra i županija, koju kasnije spajam s pojedinačnim oglasom, koristim dictionary radi lakšeg pozivanja županije preko šifre
        self.data_det = []   # pojedičnačni oglasi; ne sadržavaju županiju
        self.last_page = 1

        self.find_last_page()
        self.fill_headers()
        self.open_posts()
        #self.write_json()
        
        

        end_time = time.time()
        elapsed_time = int(end_time) - int(self.start_time)
        print( str(elapsed_time) + ' sekundi' )

    def find_last_page(self):
        #otvaram prvu stranicu da bi pronašao last_page
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/111.0.1",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"}
        self.start_time = time.time()
        self.s = requests.Session()

        response = self.s.get("https://www.index.hr/oglasi/auto-moto/gid/27?&elementsNum=100&sortby=1&num=1",headers=self.headers)
        web_page = response.content
        soup = BeautifulSoup(web_page, "html.parser")

        for li in soup.find("ul", {'class': 'pagination'}).find_all("li"):
            li_split = (str(li).split("num="))
            if len(li_split) == 2:
                li_split2 = li_split[1].split("\">")
                if int(li_split2[0]) > self.last_page:
                    self.last_page =  int(li_split2[0])

        #print(self.last_page)
        print('Zadnja stranica pronađena: ' + str(self.last_page) + ' --> ' + datetime.now().strftime("%H:%M") + ' h')

    def open_posts(self):
        #kreće otvaranje oglasa 1 po 1
        for i in range (0,len(self.links)):

            response = self.s.get(self.links[i], headers=self.headers)
            web_page = response.content
            soup = BeautifulSoup(web_page, "html.parser")
            oglas_det = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']   
            oglas_det[0] = (str(self.links[i]))
            if soup.find('a', {'class' : 'oglasKorisnickoIme'}) is not None : oglas_det[1] = soup.find('a', {'class' : 'oglasKorisnickoIme'}).get_text()
            if soup.find('div', {'class' : 'oglasivac_info grey_except_on_large'}) is not None:
                if len(soup.find('div', {'class' : 'oglasivac_info grey_except_on_large'}).find('ul').find_all('li')) >= 3 : 
                    oglas_det[2] = str(soup.find('div', {'class' : 'oglasivac_info grey_except_on_large'}).find('ul').find_all('li')[3].get_text()).split(',')[0].strip()   #mjesto
            if soup.find("title") is not None : oglas_det[4] = (str(soup.find("title").get_text()).split(" | ")[0].strip())    #naslov
            if soup.find('div', {'class' : 'oglas_description'}) is not None: oglas_det[5] = str(soup.find('div', {'class' : 'oglas_description'}).get_text()).strip().replace('\r','') #opis
            if soup.find('div', {'class' : 'price'}) is not None: oglas_det[6] = int(str(soup.find('div', {'class' : 'price'}).find('span').get_text()).replace(' €', '').replace('.',''  ).replace(',',''))   #cijena
            if soup.find('div', {'class' : 'published'}) is not None: 
                oglas_det[7] = str(soup.find('div', {'class' : 'published'}).find('strong').get_text())    #šifra oglasa
                if str(oglas_det[7]) != '' : 
                    if str(oglas_det[7]) != '':
                        oglas_det[3] = self.data_gla[oglas_det[7]]  
                    else:
                        oglas_det[3] = '' #zupanija
            datum_objave_str_start = int(str(soup.find('div', {'class' : 'published'})).find('Objava: ')) + 8
            datum_objave_str_end = int(str(soup.find('div', {'class' : 'published'})).find('Objava: ')) + 24
            if soup.find('div', {'class' : 'published'}) is not None: oglas_det[8] = str(soup.find('div', {'class' : 'published'}))[datum_objave_str_start : datum_objave_str_end]  #datum objave
            broj_prikaza_str_start = int(str(soup.find('div', {'class' : 'published'})).find('Prikazan: ')) + 10
            broj_prikaza_str_end = int(str(soup.find('div', {'class' : 'published'})).find(' puta')) 
            if soup.find('div', {'class' : 'published'}) is not None: oglas_det[9] = int(str(soup.find('div', {'class' : 'published'}))[broj_prikaza_str_start : broj_prikaza_str_end].strip())  #broj prikaza
            
            #tražim osnovne podatke o vozilu unutar features_list oglasHolder_1
            for div in soup.find_all('div', {'class' : 'features_list oglasHolder_1'}):
                for li in div.find_all('li'):
                    match str(li.get_text()):
                        case 'Marka:':
                            oglas_det[10] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Model':
                            oglas_det[11] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Tip:':
                            oglas_det[12] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Motor':
                            oglas_det[13] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Stanje vozila':
                            oglas_det[14] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Prijeđeni kilometri':
                            oglas_det[15] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','').replace('.',''  ).replace(',','')
                        case 'Godina proizvodnje':
                            oglas_det[16] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Snaga motora kW':
                            oglas_det[17] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Godina modela':
                            oglas_det[18] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Prodavač':
                            oglas_det[19] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Registriran do':
                            oglas_det[20] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Boja vozila':
                            oglas_det[21] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Broj stupnjeva na mjenjaču':
                            oglas_det[22] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Broj vrata':
                            oglas_det[23] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Oblik karoserije':
                            oglas_det[24] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Prosječna potrošnja goriva l/100km':
                            oglas_det[25] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Radni obujam cm3':
                            oglas_det[26] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Ovjes':
                            oglas_det[27] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Starost':
                            oglas_det[28] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Vrsta pogona':
                            oglas_det[29] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Vrsta mjenjača':
                            oglas_det[30] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')

            for div in soup.find_all('div', {'class' : 'features_list oglasHolder_2'}):
                for li in div.find_all('li'):
                    match str(li.get_text()):
                        case 'Autoradio':
                            oglas_det[31] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
                        case 'Klimatizacija vozila':
                            oglas_det[32] = str(li.find_next_sibling('li').get_text()).replace('\r','').replace('\n','')
            #print(oglas)
            self.data_det.append(oglas_det)
            if i != 0 and (i == 1 or i % 500 == 0): print('Oglas broj: ' + str(i) + ' / ' + str(len(self.links)) + ' --> ' + datetime.now().strftime("%H:%M") + ' h')

    def fill_headers(self):
        for i in range(1, min(self.last_page + 1, 2)):
            print("sad je na :",i)
            response = self.s.get("https://www.index.hr/oglasi/auto-moto/gid/27?&elementsNum=100&sortby=1&num=" + str(i), headers=self.headers)
            web_page = response.content
            soup = BeautifulSoup(web_page, "html.parser")
            for div in soup.find_all('div', {'class': 'OglasiRezHolder'}):
                if div.find('a', {'class': 'result'}) is not None :
                    poveznica = str(div.a['href']).strip()
                    self.links.append(poveznica)
                    sifra_oglasa_br = poveznica.find('/oid/') + 5
                    sifra_oglasa = poveznica[-(len(poveznica)-sifra_oglasa_br):]
                    if div.find('li', {'class': 'icon-marker'}) is not None :
                        zupanija = div.find('li', {'class': 'icon-marker'}).get_text()
                    else:
                        zupanija=''
                    self.data_gla[sifra_oglasa] = zupanija
            if i != 0 and (i == 1 or i % 10 == 0): print(f'Učitavanje oglasa... {i*100} / ' + str(int(self.last_page)*100) + ' --> ' + datetime.now().strftime("%H:%M:%S") + ' h')

        print('Zaglavlja oglasa napunjena: ' + datetime.now().strftime("%H:%M:%S") + ' h')

    def sort_data(self):
        # Create a list to store the header for the CSV file
        header = [
            'poveznica', 'korisnicko_ime', 'mjesto', 'zupanija', 'naslov', 'opis',
            'cijena', 'sifra_oglasa', 'datum_objave', 'broj_prikaza', 'marka',
            'model', 'tip', 'motor', 'stanje_vozila', 'kilometraza', 'godina_proizvodnje',
            'snaga_motora_kw', 'godina_modela', 'prodavac', 'registriran_do',
            'boja_vozila', 'broj_stupnjeva_na_mjenjacu', 'broj_vrata', 'oblik_karoserije',
            'potrosnja_goriva', 'radni_obujam_cm3', 'ovjes', 'starost', 'vrsta_pogona',
            'vrsta_mjenjaca', 'autoradio', 'klimatizacija_vozila'
        ]

        # ... (your existing code remains unchanged until this point)
        data = []
        for self.row_num, self.data_det_row in enumerate(self.data_det):
            data.append({header[i]: self.data_det_row[i] for i in range(len(header))})

        # Sort json_data based on 'datum_objave'
        data = sorted(data, key=lambda x: datetime.strptime(x['datum_objave'], "%d.%m.%Y %H:%M"), reverse=True)
        return data
    
    def write_json(self):
        # Create a list to store the header for the CSV file
        json_header = [
            'poveznica', 'korisnicko_ime', 'mjesto', 'zupanija', 'naslov', 'opis',
            'cijena', 'sifra_oglasa', 'datum_objave', 'broj_prikaza', 'marka',
            'model', 'tip', 'motor', 'stanje_vozila', 'kilometraza', 'godina_proizvodnje',
            'snaga_motora_kw', 'godina_modela', 'prodavac', 'registriran_do',
            'boja_vozila', 'broj_stupnjeva_na_mjenjacu', 'broj_vrata', 'oblik_karoserije',
            'potrosnja_goriva', 'radni_obujam_cm3', 'ovjes', 'starost', 'vrsta_pogona',
            'vrsta_mjenjaca', 'autoradio', 'klimatizacija_vozila'
        ]

        # ... (your existing code remains unchanged until this point)
        json_data = []
        for row_num, self.data_det_row in enumerate(self.data_det):
            json_data.append({json_header[i]: self.data_det_row[i] for i in range(len(json_header))})

        # Sort json_data based on 'datum_objave'
        json_data = sorted(json_data, key=lambda x: datetime.strptime(x['datum_objave'], "%d.%m.%Y %H:%M"), reverse=True)
        # Write data to JSON file
        json_filename = 'Index_auti.json'
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            # Use the json.dump method to write data to the JSON file
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)  # indent for pretty formatting






