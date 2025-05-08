import PySimpleGUI as sg
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

def create_window():
    # Tema da interface
    sg.theme('LightBlue2')
    
    # Layout da interface
    layout = [
        [sg.Text('Web Scraper do Google Maps', font=('Helvetica', 16), justification='center', expand_x=True)],
        [sg.Text('_' * 80)],
        [sg.Text('Digite o nicho ou categoria de negócio:')],
        [sg.InputText(key='-SEARCH-', size=(50, 1))],
        [sg.Text('Exemplo: clínica veterinária, academia, cafeteria', font=('Helvetica', 9))],
        [sg.Button('Iniciar Busca', size=(15, 1), button_color=('white', '#007bff')), 
         sg.Button('Sair', size=(10, 1), button_color=('white', '#dc3545'))],
        [sg.Text('Status:'), sg.Text('Pronto para começar a busca', key='-STATUS-')],
        [sg.ProgressBar(100, orientation='h', size=(40, 20), key='-PROGRESS-', visible=False)]
    ]
    
    # Criar janela
    return sg.Window('Web Scraper do Google Maps', layout, finalize=True, size=(550, 250))

def update_status(window, message, progress=None):
    window['-STATUS-'].update(message)
    if progress is not None:
        window['-PROGRESS-'].update(progress)
    window.refresh()

def scroll_results(driver, window):
    # Rolar para baixo para carregar mais resultados
    try:
        scroll_div = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
        for i in range(5):  # Ajuste este número conforme necessário
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)
            time.sleep(2)
            update_status(window, f"Carregando mais resultados... ({i + 1}/5)")
    except Exception as e:
        print(f"Erro ao rolar: {str(e)}")

def get_phone(driver):
    try:
        # Procurar por botões com atributo de telefone
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id^='phone']")
        if buttons:
            phone_element = buttons[0]
            # Pegar o atributo aria-label ou o texto do botão
            phone = phone_element.get_attribute("aria-label") or phone_element.text
            # Limpar o número usando regex (extrair apenas dígitos)
            phone_match = re.search(r'(\(\d+\)\s*[\d\s-]+)', phone)
            if phone_match:
                return phone_match.group(1)
    except:
        pass
    return "Não disponível"

def get_email(driver):
    try:
        # Procurar por links que contêm '@' ou texto que indica email
        email_elements = driver.find_elements(By.CSS_SELECTOR, "a")
        for elem in email_elements:
            href = elem.get_attribute("href") or ""
            if "mailto:" in href:
                return href.replace("mailto:", "")
            elif "@" in elem.text and "." in elem.text:
                return elem.text
                
        # Se não encontrar o email, tenta procurar no site da empresa
        website_buttons = driver.find_elements(By.CSS_SELECTOR, "a[data-item-id^='authority']")
        if website_buttons:
            website_url = website_buttons[0].get_attribute("href")
            if website_url:
                # Abrir o site em uma nova aba
                driver.execute_script("window.open(arguments[0]);", website_url)
                
                # Alternar para a nova aba
                driver.switch_to.window(driver.window_handles[1])
                
                # Aguardar o carregamento da página
                time.sleep(3)
                
                # Procurar por emails na página
                page_source = driver.page_source.lower()
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)
                if email_match:
                    email = email_match.group(0)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    return email
                
                # Fechar a aba e voltar para a aba principal
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
    except:
        pass
    return "Não disponível"

def collect_results(driver, window):
    results = []
    
    # Localizar todos os resultados (cards de empresas)
    result_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    total_results = len(result_elements)
    
    window['-PROGRESS-'].update(visible=True)
    
    for idx, result in enumerate(result_elements):
        try:
            progress = int((idx + 1) / total_results * 100)
            update_status(window, f"Coletando dados da empresa {idx + 1}/{total_results}", progress)
            
            # Clicar no resultado para abrir os detalhes
            result.click()
            time.sleep(2)
            
            # Aguardar o carregamento das informações
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
            
            # Obter nome da empresa
            try:
                name = driver.find_element(By.CSS_SELECTOR, "h1").text
            except:
                name = "Não disponível"
            
            # Obter telefone e email usando funções separadas
            phone = get_phone(driver)
            email = get_email(driver)
            
            # Adicionar dados aos resultados
            results.append({
                "Nome da Empresa": name,
                "Telefone": phone,
                "Email": email
            })
            
            # Voltar aos resultados
            back_button = driver.find_element(By.CSS_SELECTOR, "button[jsaction='pane.back']")
            back_button.click()
            time.sleep(1)
            
            # Atualizar a lista de elementos, pois a referência anterior pode estar obsoleta
            if idx < total_results - 1:  # Não precisamos refazer isso para o último elemento
                result_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
        
        except Exception as e:
            print(f"Erro ao processar resultado {idx}: {str(e)}")
            try:
                # Tentar voltar para a lista de resultados em caso de erro
                driver.find_element(By.CSS_SELECTOR, "button[jsaction='pane.back']").click()
                time.sleep(1)
            except:
                pass
    
    window['-PROGRESS-'].update(visible=False)
    return results

def save_to_excel(results, window):
    update_status(window, "Salvando dados em Excel...")
    
    # Criar DataFrame com os resultados
    df = pd.DataFrame(results)
    
    # Salvar em Excel
    df.to_excel("dados_psg.xlsx", index=False)

def start_scraping(search_term, window):
    if not search_term.strip():
        sg.popup_error("Por favor, insira um termo de busca.")
        return
    
    update_status(window, "Configurando navegador...")
    
    try:
        # Configurar o Chrome em modo headless (sem interface visual)
        chrome_options = Options()
        # Descomente a linha abaixo para executar em modo headless
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializar o driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Acessar o Google Maps
        update_status(window, "Acessando o Google Maps...")
        driver.get("https://www.google.com/maps")
        
        # Aguardar a página carregar
        time.sleep(2)
        
        # Localizar e preencher o campo de busca
        update_status(window, f"Pesquisando por: {search_term}")
        
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
        
        # Aguardar os resultados
        update_status(window, "Aguardando resultados...")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']")))
        
        # Coletar resultados
        update_status(window, "Coletando resultados...")
        
        # Rolar a tela para carregar mais resultados
        scroll_results(driver, window)
        
        # Coletar informações
        results = collect_results(driver, window)
        
        # Fechar o navegador
        driver.quit()
        
        # Salvar em Excel
        save_to_excel(results, window)
        
        # Mostrar mensagem de sucesso
        update_status(window, "Busca concluída com sucesso!")
        sg.popup_ok(f"Dados coletados com sucesso! Encontrados {len(results)} resultados.\nSalvo em 'dados_psg.xlsx'")
        
    except Exception as e:
        update_status(window, "Erro durante a busca!")
        sg.popup_error(f"Ocorreu um erro durante a busca: {str(e)}")
        try:
            driver.quit()
        except:
            pass

def main():
    window = create_window()
    
    # Loop de eventos
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Sair':
            break
        elif event == 'Iniciar Busca':
            start_scraping(values['-SEARCH-'], window)
    
    window.close()

if __name__ == "__main__":
    main()
