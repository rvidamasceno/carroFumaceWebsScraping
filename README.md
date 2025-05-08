# 🚗 Carro Fumacê Web Scraping

Projeto para coleta automática de dados geográficos, identificando e listando todas as ruas em um raio de 1 km a partir de um ponto de referência.

Essa ferramenta visa facilitar a geração de relatórios para solicitar o envio do carro fumacê à prefeitura, contribuindo para o combate a doenças transmitidas por mosquitos, como dengue, zika e chikungunya.

## ✨ Funcionalidades
- Coleta de nomes de ruas em um raio de 1 km usando a Overpass API
- Geração automatizada de lista em CSV para envio à administração pública
- Interface gráfica simples para entrada de coordenadas
- Suporte ao planejamento de ações de controle de vetores

## 🛠️ Tecnologias Utilizadas
- Python 3.x
- Tkinter (GUI)
- requests (HTTP)
- csv (nativo)
- Overpass API (OpenStreetMap)

## 📦 Instalação
1. Clone este repositório:
   ```bash
   git clone https://github.com/rvidamasceno/carroFumaceWebsScraping.git
   cd carroFumaceWebsScraping
   ```
2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install requests
   ```
   > **Obs:** O projeto possui um arquivo `requirements.txt`, mas as dependências listadas nele não são necessárias para a execução do `google_maps_scraper.py`. Apenas `requests` é obrigatória.

## ▶️ Como Executar
1. Execute o script principal:
   ```bash
   python google_maps_scraper.py
   ```
2. Na interface gráfica, preencha a latitude e longitude do ponto de referência.
   - Exemplo: `-23.55052` (lat), `-46.633308` (lon)
3. Clique em **Buscar Ruas**.
4. O programa irá gerar um arquivo chamado `ruas_1km.csv` com os nomes das ruas encontradas no raio de 1 km.

## 📝 Observações
- A coleta dos nomes das ruas é realizada via Overpass API (OpenStreetMap), portanto, é necessário acesso à internet.
- O arquivo gerado (`ruas_1km.csv`) pode ser enviado diretamente para a administração pública.
- Caso nenhuma rua seja encontrada, verifique se as coordenadas estão corretas.

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Desenvolvido por [rvidamasceno](https://github.com/rvidamasceno)

Este projeto foi aplicado como ferramenta de apoio à saúde pública, fornecendo dados estruturados para ajudar na definição de rotas para o carro fumacê em regiões com foco de proliferação de mosquitos.

Projeto desenvolvido por Ravi Damasceno