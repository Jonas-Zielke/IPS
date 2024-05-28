#!/bin/bash

# Start the backend
cd /app/Backend
source ve/bin/activate
python main.py &

# Start the frontend
cd /app/dashboard
npm start
