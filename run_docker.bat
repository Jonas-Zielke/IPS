@echo off
echo Changing directory to the project root...
cd /d %~dp0

echo Building the Docker image...
docker build -t ips_project .

echo Running the Docker container...
docker run -p 8000:8000 -p 3000:3000 -d ips_project

echo The application is now running.
pause
