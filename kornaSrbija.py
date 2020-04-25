import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import os
from att_send_mail import SendMail
import random
import schedule
from time import sleep
try:
    import conf
except:
    import conf_set as conf



class Scraper:
    """
        Informacija o korona vidusu u srbiji 
        Izvor: http://www.batut.org.rs/
        
        INFO:
            Zbog toga sto jednom dnevno izlaze nove informacija na sajtu
            jednom dnevno ( 8 ujutru ) dovoljno je  pokrenuti skriptu kako bi
            bili u toku sa infomacijama o Korona virusu u Srbiji svakoga dana

    """

    URL = "http://www.batut.org.rs/"
    COVID_URL = "https://covid19.rs/"
    INFO_FAJL = "info.txt"
    # FOR FIRST TIME CHECK IF info.txt EXISTS
    if INFO_FAJL not in os.listdir():
        with open(INFO_FAJL, 'w') as f:
            f.write('datum,Broj registrovanih skucajeva,link\n')
    MAILS_TO_SEND = conf.RECIVERS

    def connect(self, u):
        """ request url - u and return soup """
        r = requests.get(u)
        soup = bs(r.text, 'html.parser')
        return soup

    def get_info_link(self):
        """ Nadji info link na strani """
        s = self.connect(self.URL)
        divs = s.find_all('div', {'class': self.DIV_CLASS})
        for div in divs:
            if self.DIV_WORD in div.text:
                return div.select('a')[1]['href']
                break

    def go_to_info_link(self):
        """ Idi na info stranu i pokupi potrebe podatke """
        full_info_link = "https://covid19.rs/"
        info_link = 'neki link'
        if info_link != None:
            s = self.connect(full_info_link)
            title = "KORONA INFO"
            potvrdjen_slucaj = s.select('p.elementor-heading-title.elementor-size-default')[2].text.replace('.','')
            today_ful = datetime.today()
            today = f'{today_ful.day}-{today_ful.month}-{today_ful.year}'
            return title, potvrdjen_slucaj, today, full_info_link
            
    def read_txt(self):
        df = pd.read_csv(self.INFO_FAJL)
        return df

    def write_to_file(self):
        """ Pisanje informacija u fajl """
        title, slucaj, datum, link = self.go_to_info_link()
        self.SLUCAJ = slucaj
        self.DATUM = datum
        self.LINK = link
        today_ful = datetime.today()
        today = f"{today_ful.day}-{today_ful.month}-{today_ful.year}"
        df = self.read_txt()
        print(df)
        provereni_datumi = df['datum'].values.tolist()
        broj_slucajeva = df['Broj registrovanih skucajeva'].values.tolist()
        if len(provereni_datumi) > 0:
            # proveri da li vec postoje ovakvi podaci u fajlu
            if today in provereni_datumi and int(slucaj) == broj_slucajeva[-1]:
                print("DANAS STE PROVERILI INFORMACIJU, NEMA NOVIH INFORMACIJA")
            else:
                with open(self.INFO_FAJL, 'a') as f:
                    f.write(f'{datum},{slucaj},{link}\n')
        else:
            with open(self.INFO_FAJL, 'a') as f:
                f.write(f'{datum},{slucaj},{link}\n')

    def create_excel(self):
        self.FAJL = "KoronaSrbijaInfo.xlsx"
        df = pd.read_csv('info.txt')
        df1 = pd.DataFrame()
        df1['datum'] = df['datum']
        df1['Broj registrovanih skucajeva']= df['Broj registrovanih skucajeva']
        df1.to_excel("KoronaSrbijaInfo.xlsx")

    def send_mails(self):
        random_text=['Molimo perite redovno ruke!',
                     'Vanredno stanje je i dalje na snazi, nadamo se da cemo pobediti koronu uskoro',
                     'Najbolji nacin da pobedimo je da ostanemo kod kuce',
                     ' #OSTANIKODKUCE ',
                     'Nikad briga, nikad stres, ostani kod kuce i jedi keks na eks!',
                ]
        r_text = random.choice(random_text)
        subject = f'KORONA INFO U SRBIJI NA DAN {self.DATUM}'
        text = f'Do danas je u Srbiji registrovano {self.SLUCAJ} obolelih od korona virusa.{r_text}\nZa vise informacija idite na link {self.LINK}'
        for mail in self.MAILS_TO_SEND:
            SendMail(mail, subject, text, self.FAJL)
            print(f'Poslat mail na {mail}')

    def run(self):
        # self.go_to_info_link()
        self.write_to_file()
        self.create_excel()
        self.send_mails()


def main():
    s = Scraper()
    s.run()

if __name__ == '__main__':
    schedule.every().day.at('16:00').do(main)
    while True:
        schedule.run_pending()
        sleep(1)

