
# Bluesky Disinfo Analyzer

This is an open-source investigative dashboard developed for the **Bellingcat & CLIP Hackathon at Universidad de los Andes** (March 2025).

### **But it can be adapted to other countries, contexts and research — and the analysis methodology can also be used for other social networks.**

The project focuses on monitoring, analyzing, and uncovering disinformation and hate speech campaigns on the Bluesky social network, with a focus on Brazil.

## 🌐 Live App

Try it online:  
**https://blueskyanalytics.streamlit.app/**

## 🎯 Objectives

- Detect and visualize digital disinformation trends.
- Identify inauthentic behavior and coordinated campaigns.
- Monitor flagged content, hashtags, reposting patterns, and user activity.
- Provide journalists and researchers with tools to explore data from Bluesky.

## 🚀 Features

| Functionality            | Description                                                                                      | Script                         |
|--------------------------|--------------------------------------------------------------------------------------------------|--------------------------------|
| 🚩 **Analyze Post**       | Detects country/region flags in names of users who liked a post. Shows like timeline + preview. | `01_analyze_post.py`          |
| 📈 **Analyze Hashtag**    | Searches hashtags on Bluesky API, shows co-occurring hashtags, top users and word cloud.        | `02_analyze_hashtag.py`       |
| 📊 **Repost Distribution**| Shows how many times posts are reposted. (Static JSON for now).                                  | `03_repost_counter.py`        |
| 🧑 **Analyze User**       | Analyzes one user’s latest posts to show who they repost and reply to most.                     | `04_analyze_user.py`          |
| 🔁 **Most Reposted Users**| Extracts most frequently reposted accounts from sample data.                                     | `05_most_reposted_by_user.py` |
| ✍️ **Users with Most Posts** | Lists most active accounts from static post data.                                               | `06_users_with_most_posts.py` |

## 🧠 Data sources

- [Bluesky Public API](https://docs.bsky.app/docs/api)
- All real-time analyses use dynamic API queries
- Some older features use JSON files from prior crawls

## 📦 Installation

```bash
git clone https://github.com/reichaves/bluesky_analytics.git
cd bluesky_analytics
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Folder structure

```
.
├── app.py                         # Main Streamlit dashboard
├── requirements.txt              # Python dependencies
├── data/                         # (Optional) JSON samples
├── 01_analyze_post.py
├── 02_analyze_hashtag.py
├── 03_repost_counter.py
├── 04_analyze_user.py
├── 05_most_reposted_by_user.py
├── 06_users_with_most_posts.py
```

## 👥 Authors

- **Armando Mora** (Costa Rica)  
- **José Luis Peñarredonda** (Colombia)  
- **Tristan Lee** (United States)  
- **Reinaldo Chaves** (Brazil)

## 🛠 Next steps

- Transition all functions to live API queries
- Add sentiment and toxicity detection (e.g., using HateSonar, Detoxify, Perspective API)
- Add network analysis using repost/mention graphs

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

This project is licensed under the [MIT License](LICENSE).
