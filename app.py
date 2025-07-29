import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
# st.set_page_config é a primeira coisa a ser chamada
st.set_page_config(
    page_title="XXX Weather",
    page_icon="🌦️",
    layout="centered" 
)

# --- FUNÇÕES ---

def get_weather(api_key, city):
    """Busca os dados do tempo para uma cidade usando a API do OpenWeatherMap."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',  # Para obter temperatura em Celsius
        'lang': 'pt_br'     # Para obter descrições em português
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Se a cidade não for encontrada, a API retorna 404
        if response.status_code == 404:
            st.error(f"Cidade '{city}' não encontrada. Por favor, verifique o nome e tente novamente.")
        else:
            st.error(f"Erro HTTP: {http_err} - {response.text}")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
        return None

def get_weather_emoji(weather_id):
    """Retorna um emoji correspondente ao código do tempo."""
    if 200 <= weather_id < 300:
        return "⛈️"  # Tempestade
    elif 300 <= weather_id < 400:
        return "🌦️"  # Chuvisco
    elif 500 <= weather_id < 600:
        return "🌧️"  # Chuva
    elif 600 <= weather_id < 700:
        return "❄️"  # Neve
    elif 700 <= weather_id < 800:
        return "🌫️"  # Névoa
    elif weather_id == 800:
        return "☀️"  # Céu limpo
    elif 801 <= weather_id < 805:
        return "☁️"  # Nuvens
    else:
        return "🌍" # Padrão

def get_clothing_suggestion(feels_like, weather_id):
    """Gera uma sugestão de roupa com base na sensação térmica e no tempo."""
    suggestion = ""
    
    # Lógica baseada na sensação térmica
    if feels_like > 26:
        suggestion = "Dia quente! Use roupas leves como camisetas e shorts."
    elif 20 <= feels_like <= 26:
        suggestion = "Tempo agradável. Uma camiseta e calças são uma boa pedida."
    elif 15 <= feels_like < 20:
        suggestion = "Pode ficar um pouco frio. Considere uma blusa de manga longa ou um casaco leve."
    elif 10 <= feels_like < 15:
        suggestion = "Está frio! Um bom casaco ou suéter é essencial."
    else: # feels_like < 10
        suggestion = "Muito frio! Agasalhe-se bem com casaco pesado, cachecol e luvas."

    # Adicionais com base na condição do tempo
    if 200 <= weather_id < 600: # Chuva ou Tempestade
        suggestion += " Não se esqueça de um guarda-chuva ou capa de chuva!"
    elif 600 <= weather_id < 700: # Neve
        suggestion += " E prepare-se para a neve!"
    elif weather_id == 800 and feels_like > 22: # Céu Limpo e quente
        suggestion += " Óculos de sol e protetor solar são recomendados."
        
    return suggestion

# --- INTERFACE DA APLICAÇÃO ---

# Cabeçalho similar ao Navbar do HTML original
st.image("https://storage.googleapis.com/bkt-static-tt/logo.png", width=50)
st.title("XXX Weather App")
st.markdown("---")

# Campo de entrada para o nome da cidade
city = st.text_input(
    "Digite o nome da cidade:", 
    placeholder="Ex: São Paulo, BR"
)

# Botão para buscar os dados do tempo
if st.button("Verificar Tempo", type="primary"):
    if city:
        # Carrega a chave da API a partir dos segredos do Streamlit
        try:
            api_key = st.secrets["OPENWEATHER_API_KEY"]
            
            with st.spinner(f"Buscando dados do tempo para {city}..."):
                weather_data = get_weather(api_key, city)

            if weather_data:
                # Extrai os dados relevantes
                country = weather_data['sys']['country']
                description = weather_data['weather'][0]['description'].capitalize()
                temp = weather_data['main']['temp']
                feels_like = weather_data['main']['feels_like']
                temp_min = weather_data['main']['temp_min']
                temp_max = weather_data['main']['temp_max']
                humidity = weather_data['main']['humidity']
                wind_speed = weather_data['wind']['speed']
                weather_id = weather_data['weather'][0]['id']
                
                # Obtém o emoji e a sugestão de roupa
                emoji = get_weather_emoji(weather_id)
                clothing_suggestion = get_clothing_suggestion(feels_like, weather_id)

                # Exibe os resultados
                st.subheader(f"Tempo agora em {weather_data['name']}, {country} {emoji}")
                
                # Usa colunas para uma melhor organização visual
                col1, col2, col3 = st.columns(3)
                col1.metric("Temperatura", f"{temp:.1f} °C")
                col2.metric("Umidade", f"{humidity}%")
                col3.metric("Vento", f"{wind_speed} m/s")
                
                st.info(f"**Descrição:** {description}")
                st.write(f"🌡️ **Sensação Térmica:** {feels_like:.1f}°C")
                st.write(f"📉 **Mínima / Máxima:** {temp_min:.1f}°C / {temp_max:.1f}°C")

                # Exibe a sugestão de roupa
                st.success(f"👕 **Sugestão de Roupa:** {clothing_suggestion}")


        except KeyError:
            st.error("Chave da API do OpenWeatherMap não encontrada.")
            st.info("Por favor, adicione sua `OPENWEATHER_API_KEY` ao arquivo `.streamlit/secrets.toml`.")
    else:
        st.warning("Por favor, digite o nome de uma cidade.")

st.markdown("---")
st.write("Desenvolvido com ❤️ usando Streamlit.")

