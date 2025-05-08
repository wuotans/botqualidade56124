from botweb import BotWeb
from bs4 import BeautifulSoup
from datetime import datetime
import time
import urllib.parse
#teste
class MyBot(BotWeb):
    def __init__(self, *args, **kwargs):
        super().__init__(
            prefix_env="SSW",
            credentials_keys=['DOMINIO', "CPF", "USUARIO", "SENHA"]
        )

        self.headers = {
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

    def _enter_domain(self):
        self.driver.execute_script(
            f"document.getElementById('1').value='{self.credentials['DOMINIO']}'"
        )

    def _enter_cpf(self):
        self.driver.execute_script(
            F"document.getElementById('2').value='{self.credentials['CPF']}'"
        )

    def _enter_user(self):
        self.driver.execute_script(
            F"document.getElementById('3').value='{self.credentials['USUARIO']}'"
        )

    def _enter_password(self):
        self.driver.execute_script(
            F"document.getElementById('4').value='{self.credentials['SENHA']}'"
        )

    def _click_submit(self):
        self.driver.execute_script(
            F"document.getElementById('5').click()"
        )

    def _enter_code(self, code):
        self.driver.execute_script(
            F"document.getElementById('3').value='{code}'; doOption();"
        )

    def login(self):
        self._enter_domain()
        self._enter_cpf()
        self._enter_user()
        self._enter_password()
        self._click_submit()
        self.get_cookies()

    def post_56(self):
        body = "sequencia=56&dummy=1734112159743"
        response = self.session.post(
            "https://sistema.ssw.inf.br/bin/ssw0082",
            headers=self.headers,
            data=body
        )

    def filtro_56(self):
        body = "act=FILCOD&f1=124&dummy=1734114950341"
        response = self.session.post(
            "https://sistema.ssw.inf.br/bin/ssw0082",
            headers=self.headers,
            data=body
        )

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # Data do dia 1º do mês vigente
            hoje = datetime.now()
            data_primeiro_mes_vigente = hoje.strftime("01/%m/%y")

            elemento_xmlsr = soup.find(id="xmlsr")
            if elemento_xmlsr:
                linhas = elemento_xmlsr.find_all('r')
                for linha in linhas:
                    data_tag = linha.find('f4')
                    if data_tag and data_primeiro_mes_vigente in data_tag.text:
                        tag_f6 = linha.find('f6')
                        if tag_f6:
                            conteudo_f6 = tag_f6.text.strip()
                            timestamp = str(int(time.time() * 1000))
                            linha_formatada = f"act={conteudo_f6}&dummy={timestamp}"
                            print("Linha formatada:", linha_formatada)
                            self.linha_formatada_56 = linha_formatada
                            return linha_formatada

            print(f"Nenhuma linha encontrada com a data {data_primeiro_mes_vigente}.")
        else:
            print("Erro ao gerar 56:", response.status_code)
    
    def generate_56(self):
        body = self.linha_formatada_56
        reponse = self.session.post(
            "https://sistema.ssw.inf.br/bin/ssw0082",
            headers=self.headers,
            data=body
        )
        if reponse.status_code == 200:
            print(reponse.text)
            return self.decode(reponse.text) 
            


    def decode(self, url_codificada):
        url_decodificada = urllib.parse.unquote(url_codificada)
        parametros = url_decodificada.split(',')
        print("URL decodificada", url_decodificada)
        print("Parametros", parametros)
        first_name = parametros[0].split('abrir')[1].replace("('", '').replace("'", '')
        second_name = parametros[1].replace("'", '')
        print (first_name, second_name)
        return first_name,second_name


        
            

    def download_56(self, first_name, second_name):
        response = self.session.get(
            f"https://sistema.ssw.inf.br/bin/ssw0424?act={first_name}&filename={second_name}&path=/usr/tmp/&down=1&nw=1",
            headers=self.headers
        )
        if response.status_code == 200:
            with open('downloads/56_124.csv', 'wb') as f:
                f.write(response.content)
                print('relatorio salvo')

if __name__ == '__main__':
    with MyBot() as mybot:
        mybot.init_browser(
            headless=True,
            browser="chrome"
        )
        mybot.open(
            "https://sistema.ssw.inf.br/bin/ssw0422"
        )
        mybot.login()
        mybot.post_56()
        mybot.filtro_56()
        first_name, second_name = mybot.generate_56()
        mybot.download_56(first_name, second_name)




