# Użyj oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.9

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd
RUN apt-get update && apt-get install -y iptables
# Skopiuj plik requirements.txt do kontenera
COPY requirements.txt requirements.txt

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu źródłowego do kontenera
COPY . /app

# Zdefiniuj port, na którym będzie działać aplikacja
EXPOSE 5000

# Uruchom aplikację
CMD ["python", "app.py"]
