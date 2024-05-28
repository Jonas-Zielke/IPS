#!/bin/bash

# 1. Check for root/admin privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# 2. Ask what to install
echo "What do you want to install?"
echo "a. Everything"
echo "b. Only the backend"
echo "c. Only the frontend"
read -p "Enter your choice (a/b/c): " choice

# 3. Clone the Git repository
git clone https://github.com/Jonas-zielke/IPS.git
cd IPS

# 4. Install backend if chosen
if [[ "$choice" == "a" || "$choice" == "b" ]]; then
    cd Backend
    python -m venv ve
    source ve/bin/activate
    pip install -r install.txt
    cd ..
fi

# 5. Install frontend if chosen
if [[ "$choice" == "a" || "$choice" == "c" ]]; then
    cd dashboard
    npm install

    # 6. Create .env file for admin credentials
    read -p "Enter admin username: " admin_username
    read -sp "Enter admin password: " admin_password
    echo -e "\nADMIN_USERNAME=$admin_username\nADMIN_PASSWORD=$admin_password" > .env
    cd ..
fi

# 7. Configure backend settings
if [[ "$choice" == "a" || "$choice" == "b" ]]; then
    echo "Do you want to apply the recommended backend settings? (yes/no)"
    read apply_settings

    if [[ "$apply_settings" == "yes" ]]; then
        cat <<EOL > Backend/config.py
FORWARDING_RULES = {

}

EXCLUDED_IP_RANGES = [
    "192.168.53."
]

SYN_FLOOD_PROTECTION_ENABLED = True
SYN_FLOOD_TIMEOUT = 2
EOL
    else
        cat <<EOL > Backend/config.py
FORWARDING_RULES = {

}

EXCLUDED_IP_RANGES = [

]

SYN_FLOOD_PROTECTION_ENABLED = False
SYN_FLOOD_TIMEOUT = 2
EOL
    fi
fi

# 8. Start everything
if [[ "$choice" == "a" || "$choice" == "c" ]]; then
    cd dashboard
    npm start &
    cd ..
fi

if [[ "$choice" == "a" || "$choice" == "b" ]]; then
    cd Backend
    source ve/bin/activate
    python main.py &
fi

echo "Installation and setup complete."
