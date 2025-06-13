# IPS System

Ein umfassendes Netzwerküberwachungssystem zur Erfassung und Analyse von Netzwerkverkehr und Ressourcenverbrauch.

## Übersicht

Dieses Projekt bietet eine robuste Lösung zur Überwachung und Verwaltung von Netzwerkressourcen und -aktivitäten. Es besteht aus einem Backend, das Netzwerkverkehr und Systemressourcen protokolliert, und einem Frontend, das Benutzern eine intuitive Oberfläche zur Verwaltung und Analyse bietet.

## Funktionen

### Backend

- **Netzwerkverkehrsprotokollierung**: Erfasst und speichert detaillierte Informationen über den Netzwerkverkehr.
- **Ressourcenüberwachung**: Überwacht CPU- und RAM-Auslastung sowie Netzwerktraffic.
- **Datenprotokollierung**: Speichert Protokolle in JSON-Dateien zur späteren Analyse.
- **API**: Bietet Endpunkte zum Abrufen aktueller Ressourcennutzungsdaten.

### Frontend

- **Benutzeranmeldung**: Ermöglicht die Anmeldung mit Administratoranmeldeinformationen.
- **Zwei-Faktor-Authentifizierung (2FA)**: Beim ersten Login muss die 2FA aktiviert werden, und bei jedem Login muss der 2FA-Code eingegeben werden.
- **Intuitive Benutzeroberfläche**: Bietet eine benutzerfreundliche Oberfläche zur Anzeige und Analyse von Netzwerk- und Ressourcendaten.

## Installation

### Voraussetzungen

- Python 3.x
- Node.js 20 und npm
- Ein unterstützter Webbrowser

### Backend

1. Klonen Sie das Repository:
    ```bash
   git clone https://github.com/Jonas-Zielke/IPS.git
   cd IPS/Backend
    ```

2. Erstellen Sie eine virtuelle Umgebung und installieren Sie die Abhängigkeiten:
    ```bash
    python -m venv ve
    ve/Scripts/activate
    pip install -r install.txt
    ```

3. Starten Sie das Backend:
    ```bash
    ve/Scripts/python.exe main.py
    ```

### Frontend

1. Navigieren Sie zum Frontend-Verzeichnis:
    ```bash
    cd ../dashboard
    ```

2. Installieren Sie die Abhängigkeiten:
    ```bash
    npm install
    ```

3. Starten Sie das Frontend:
    ```bash
    npm start
    ```

## Nutzung

1. Starten Sie sowohl das Backend als auch das Frontend wie oben beschrieben.
2. Öffnen Sie einen Webbrowser und navigieren Sie zur Adresse des Frontends (normalerweise `http://localhost:3000`).
3. Melden Sie sich mit den Administratoranmeldeinformationen an.
4. Aktivieren Sie die Zwei-Faktor-Authentifizierung beim ersten Login.
5. Verwenden Sie den 2FA-Code bei jedem weiteren Login, um auf die Anwendung zuzugreifen.

## API-Endpunkte

### Ressourcenüberwachung

- **GET** `/resource/usage`: Abrufen der aktuellen CPU- und RAM-Auslastung sowie des Netzwerktraffics.

### Netzwerkverkehrsprotokollierung

- **GET** `/logs/network`: Abrufen der protokollierten Netzwerkdaten.
- **GET** `/logs/resource`: Abrufen der protokollierten Ressourcennutzungsdaten.

## Fehlerbehebung

### Bekannte Probleme

- **NameError: 'ResourceManager' is not defined**: Stellen Sie sicher, dass `ResourceManager` korrekt importiert und initialisiert ist. Weitere Details finden Sie im Code und in den Kommentaren im Quellcode.

## Mitwirkende

- **Jonas Zielke** - *Projektleitung und Entwicklung* - [Jonas Zielke](https://github.com/Jonas-Zielke)

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE)-Datei für Details.
