cd /d "M:\Projekte\netzwerk\test\"
@echo off
SETLOCAL

REM 1. Check for admin privileges
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO This script must be run as administrator.
    EXIT /B 1
)

REM 2. Ask what to install
CHOICE /C abc /M "What do you want to install? a. Everything b. Only the backend c. Only the frontend"
SET "choice=%ERRORLEVEL%"

REM 3. Clone the Git repository
git clone https://github.com/Jonas-zielke/IPS.git
CD IPS

REM 4. Install backend if chosen
IF %choice%==1 ( 
    CD Backend
    python -m venv ve
    CALL ve\Scripts\activate
    pip install -r install.txt
    CD ..
)
IF %choice%==2 ( 
    CD Backend
    python -m venv ve
    CALL ve\Scripts\activate
    pip install -r install.txt
    CD ..
)

REM 5. Install frontend if chosen
IF %choice%==1 (
    CD dashboard
    npm install

    REM 6. Create .env file for admin credentials
    SET /P admin_username="Enter admin username: "
    SET /P admin_password="Enter admin password: "
    ECHO ADMIN_USERNAME=%admin_username% > .env
    ECHO ADMIN_PASSWORD=%admin_password% >> .env
    CD ..
)
IF %choice%==3 (
    CD dashboard
    npm install

    REM 6. Create .env file for admin credentials
    SET /P admin_username="Enter admin username: "
    SET /P admin_password="Enter admin password: "
    ECHO ADMIN_USERNAME=%admin_username% > .env
    ECHO ADMIN_PASSWORD=%admin_password% >> .env
    CD ..
)

REM 7. Configure backend settings
IF %choice%==1 (
    ECHO Do you want to apply the recommended backend settings? (yes/no)
    SET /P apply_settings=""
    IF /I "%apply_settings%"=="yes" (
        ECHO FORWARDING_RULES = { > Backend\config.py
        ECHO } >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO EXCLUDED_IP_RANGES = [ >> Backend\config.py
        ECHO     "192.168.53." >> Backend\config.py
        ECHO ] >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO SYN_FLOOD_PROTECTION_ENABLED = True >> Backend\config.py
        ECHO SYN_FLOOD_TIMEOUT = 2 >> Backend\config.py
    ) ELSE (
        ECHO FORWARDING_RULES = { > Backend\config.py
        ECHO } >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO EXCLUDED_IP_RANGES = [ >> Backend\config.py
        ECHO ] >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO SYN_FLOOD_PROTECTION_ENABLED = False >> Backend\config.py
        ECHO SYN_FLOOD_TIMEOUT = 2 >> Backend\config.py
    )
)
IF %choice%==2 (
    ECHO Do you want to apply the recommended backend settings? (yes/no)
    SET /P apply_settings=""
    IF /I "%apply_settings%"=="yes" (
        ECHO FORWARDING_RULES = { > Backend\config.py
        ECHO } >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO EXCLUDED_IP_RANGES = [ >> Backend\config.py
        ECHO     "192.168.53." >> Backend\config.py
        ECHO ] >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO SYN_FLOOD_PROTECTION_ENABLED = True >> Backend\config.py
        ECHO SYN_FLOOD_TIMEOUT = 2 >> Backend\config.py
    ) ELSE (
        ECHO FORWARDING_RULES = { > Backend\config.py
        ECHO } >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO EXCLUDED_IP_RANGES = [ >> Backend\config.py
        ECHO ] >> Backend\config.py
        ECHO. >> Backend\config.py
        ECHO SYN_FLOOD_PROTECTION_ENABLED = False >> Backend\config.py
        ECHO SYN_FLOOD_TIMEOUT = 2 >> Backend\config.py
    )
)

REM 8. Start everything
IF %choice%==1 (
    START CMD /C "CD dashboard && npm start"
    CD Backend
    CALL ve\Scripts\activate
    START CMD /C "python main.py"
)
IF %choice%==2 (
    CD Backend
    CALL ve\Scripts\activate
    START CMD /C "python main.py"
)
IF %choice%==3 (
    START CMD /C "CD dashboard && npm start"
)

ECHO Installation and setup complete.
ENDLOCAL
PAUSE
