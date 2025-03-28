# Bluesky Disinfo Analyzer

This is an open-source investigative dashboard developed for the **Bellingcat & CLIP Hackathon at Universidad de los Andes** (March 2025).

### But it can be adapted to other countries, contexts and research - and the analysis methodology can also be used for other social networks.

The project focuses on monitoring, analyzing, and uncovering disinformation and hate speech campaigns on the Bluesky social network, with a focus on Brazil.

## 🌐 Live App

You can try the dashboard at:  
https://blueskyanalytics.streamlit.app/

## 🎯 Objectives

- Detect and visualize digital disinformation trends.
- Identify inauthentic behavior and organized campaigns.
- Monitor flagged content, hashtags, and reposting patterns.
- Provide journalists and researchers with tools to explore data from Bluesky.

## 🚀 Features

| Functionality | Description | Script |
|---------------|-------------|--------|
| 🚩 **Flag detector** | Finds country or regional flag emojis in profile names of users who liked a specific post. Uses real-time API queries based on a Bluesky URL. | `01_look_for_flags.py` |
| 📅 **Hashtag analysis** | Searches for hashtags using the Bluesky API and extracts trending terms from post metadata. Includes bar chart and word cloud. | `02_hashtags.py` |
| 📈 **Repost distribution** | Calculates how many times posts were reposted. (Currently uses a static JSON; will be updated to fetch from API.) | `03_repost_counter.py` |
| 📅 **Likes by date** | Analyzes the total number of likes per day. (Static JSON for now.) | `04_number_likes_by_dates.py` |
| 🔁 **Most reposted accounts** | Detects which accounts are most commonly reposted. | `05_most_reposted_by_user.py` |
| ✍️ **Users with most posts** | Identifies the most prolific accounts (excluding replies). | `06_users_with_most_posts.py` |

## 🧠 Data sources

- [Bluesky Public API](https://docs.bsky.app/docs/api)
- Queries are made using `requests` directly from the app

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/reichaves/bluesky_analytics.git
   cd bluesky_analytics
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## 📁 Folder structure

```
.
├── app.py                   # Main Streamlit app
├── requirements.txt         # Python dependencies
├── data/                    # Local data files (temporary; to be replaced by dynamic API)
├── 01_look_for_flags.py
├── 02_hashtags.py
├── 03_repost_counter.py
├── 04_number_likes_by_dates.py
├── 05_most_reposted_by_user.py
├── 06_users_with_most_posts.py
```

## 👥 Authors

- **Armando Mora** (Costa Rica)  
- **José Luis Peñarredonda** (Colombia)  
- **Tristan Lee** (United States)  
- **Reinaldo Chaves** (Brazil)

## 🛠 Next steps

- Replace remaining static scripts with real-time API queries
- Improve visualizations with dynamic graph/network libraries
- Add search by username and richer metadata visualizations

## 🧵 Common hashtags and keywords used in disinformation or hate campaigns in Brazil (2025)

```
#FraudeNasUrnas
#VotoImpressoJá
#STFCensurador
#CPIdaFarsa
#VacinaMatando
#CovidFraude
#TratamentoPrecoce
#Globalismo
#NovaOrdemMundial
#Agenda2030
#MarxismoCultural
#DitaduraGay
#IdeologiaDeGênero
#VacinaChinesaNão
#GloboLixo
#FolhaPutinhaDoPT
#STFLixo
#CongressoCorrupto
#MídiaComprada
#ImprensaGolpista
#CensuraNoBrasil
#Esquerdopata
#Petralha
#ComunistaSafado
#Feminazi
#Lacração
#MilitanteChato
#Cancelamento
#FakeNews
#ImpeachmentFake
#LiberdadeDeExpressao
#CensuraNuncaMais
folhalixo
estadãolixo
forapt
foraalexandredemoraes
canetadesmanipuladora
fakenews
esquerdanuncamais
esquerdalixo
globolixotraidoradapátria
forafláviodino
nãoaototalitarismo
nãoaofeminismo
nãoaocomunismo
voltaporcima
foralula
fantásticolixo
vejalixo
corrupçãosemfim
cegueiraeleitoral
lulaladrão
canalmeiolixo
globomente
foraladrao
liberdademasculina
impeachmentdelulajá
bolsonaro2026
efeitolula
governolula
recordlixo
globosta
mídiapodre
trump
censura
liberdadefinanceira
donaldtrump
direita
ditadura
globalism
stf
woke
bolsonaro
conservador
globalistica
comunismo
janja
esquerdistas
esquerdoloides
jumentodolula
jumentinhodolula
bolsominion
redpill
bluepill
fuckmarxism
liberdadedeexpressão
pablomarçal
xandao
censuranão
recontagem
stopthecount
globalistico
novaordem
illuminatti
ordeminternacional
controledasmassas
iluminati
votoimpresso
tselixo
xandaonacadeia
direitaunida
ptnuncamais
direitaseguedireita
womad
esquerdista
pix
culturawoke
```

## 📄 License

This project is shared under the MIT License.
