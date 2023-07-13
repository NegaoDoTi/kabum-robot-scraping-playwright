from playwright.sync_api import Playwright, sync_playwright, Page
from pandas import DataFrame
from pandas import ExcelWriter
import sys


class KabumPlaywrightScraping:
    def __init__(self) -> None:
        self.default_url = sys.argv[1]
        self.page:Page
        
        
    def run(self, playwright: Playwright) -> None:
        browser = playwright.chromium.launch(headless=False, args=["--start-fullscreen"])
        context = browser.new_context()
        self.page = context.new_page()
        
        #https://www.kabum.com.br/espaco-gamer/cadeiras-gamer?page_number=1&page_size=20&facet_filters=eyJDb3IiOlsiQnJhbmNvIl19&sort=most_searched
        
        self.page.goto(self.default_url,
                timeout=60000)
        
        self.page.wait_for_load_state(timeout=60000)
        
        infos = []
        
        last_page_number = self.number_pages()
        
        for number in range(1, last_page_number+1):
            self.page.goto(self.get_url(number),
                timeout=60000)
            
            self.page.wait_for_load_state(timeout=60000)
            result = self.extract_info_cards()
            for i in range(len(result["nomes"])):
                infos.append([ result["nomes"][i], result["precos"][i], result["links"][i] ])       
        
        # ---------------------
        context.close()
        browser.close()

                        
        self.export_excel(infos) 

    def number_pages(self) -> int:
        
        pages_numbers = self.page.locator("a.page").all()
        last_page_number = pages_numbers[-1]
        last_page_number = int(last_page_number.inner_text())
        return last_page_number
    
    def extract_info_cards(self) -> dict:
        nomes = []
        precos = []
        links = []
        
        cadeirasCard = self.page.locator("div.productCard").all()
        for cadeira in cadeirasCard:
            string_preco = cadeira.locator("span.priceCard").inner_text()
            if "---" in string_preco:
                continue
            
            nomes.append(cadeira.locator("span.nameCard").inner_text())
            precos.append(string_preco)
            links.append(f'https://www.kabum.com.br{cadeira.locator("a.productLink").get_attribute("href")}')
            
        return {"nomes" : nomes, "precos" : precos, "links" : links}

    def get_url(self, number:int) -> str:
        if "kabum" in self.default_url:
            if "page_number=1" in self.default_url:
                
                url = self.default_url.replace("page_number=1", f"page_number={number}")
                return url
            else:
                url = self.default_url + f"?page_number={number}"
                return url
        else:
            raise ValueError("URL Invalida, a URL deve ser do Site Kabum!")
        
    def export_excel(self, infos:list):
        
        columns = ["Nome", "Preço", "Link"]
        dataframe = DataFrame(data=infos, columns=columns)
        print(dataframe)
        
        archive = ExcelWriter(f"{sys.argv[2]}.xlsx", engine="xlsxwriter")
        
        dataframe.to_excel(archive, index=False)
        
        archive.close()
    
with sync_playwright() as playwright:
    KabumPlaywrightScraping().run(playwright)
