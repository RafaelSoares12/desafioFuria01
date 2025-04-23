from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime

def getProximosJogos(url):
    driver = Driver(uc=True, headless=True)
    jogos = []

    try:
        driver.get(url)

        try:
            allowButton = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            )
            allowButton.click()
        except:
            pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        section = soup.find('h2', string='Upcoming matches for FURIA')
        if section:
            empty = section.find_next_sibling('div', class_='empty-state')
            if empty:
                return ['Nenhuma partida futura da FURIA foi encontrada.']

        tables = soup.select('table.match-table')
        for table in tables:
            eventName = table.select_one('thead .event-header-cell a')
            event = eventName.text.strip() if eventName else "Evento desconhecido"

            rows = table.select('tbody tr.team-row')
            for row in rows:
                dataTag = row.select_one('.date-cell span')
                dataStr = dataTag.text.strip() if dataTag else None

                if dataStr:
                    data = datetime.strptime(dataStr, '%d/%m/%Y').date()
                    if data >= datetime.today().date():
                        time1 = row.select_one('.team-name.team-1')
                        time2 = row.select_one('.team-name.team-2')
                        time1 = time1.text.strip() if time1 else "Time 1"
                        time2 = time2.text.strip() if time2 else "Time 2"
                        jogos.append(f"{dataStr} - {time1} vs {time2} - {event}")

        if not jogos:
            jogos.append("Nenhum jogo futuro encontrado.")

    finally:
        driver.quit()

    return jogos

def getResultadosRecentes(url):
    driver = Driver(uc=True, headless=True)
    jogos = []

    try:
        driver.get(url)

        try:
            allowButton = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            )
            allowButton.click()
        except:
            pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        tables = soup.select('table.match-table')
        
        for table in tables:
            eventName = table.select_one('thead .event-header-cell a')
            event = eventName.text.strip() if eventName else "Evento desconhecido"

            rows = table.select('tbody tr.team-row')
            
            for row in rows:
                dataTag = row.select_one('.date-cell span')
                dataStr = dataTag.text.strip() if dataTag else None

                if dataStr:
                    data = datetime.strptime(dataStr, '%d/%m/%Y').date()
                    if data < datetime.today().date():
                        time1 = row.select_one('.team-name.team-1')
                        time2 = row.select_one('.team-name.team-2')
                        time1 = time1.text.strip() if time1 else "Time 1"
                        time2 = time2.text.strip() if time2 else "Time 2"

                        placares = row.select('.score')

                        if len(placares) >= 2:
                            score1 = placares[0].text.strip()
                            score2 = placares[1].text.strip()
                        else:
                            score1 = score2 = "0"

                        if "FURIA" in time1:
                            resultado = "VITÓRIA" if int(score1) > int(score2) else "DERROTA"
                        elif "FURIA" in time2:
                            resultado = "VITÓRIA" if int(score2) > int(score1) else "DERROTA"
                        else:
                            resultado = "EMPATE"
                        
                        jogos.append(f"{dataStr} - {time1} ({score1}) vs {time2} ({score2}) - {resultado} - {event}")

        if not jogos:
            jogos.append("Nenhum resultado recente encontrado.")

    finally:
        driver.quit()

    return jogos

print(getResultadosRecentes('https://www.hltv.org/team/8297/furia#tab-matchesBox'))