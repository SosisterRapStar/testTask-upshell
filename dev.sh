#!/bin/bash


sudo apt update
sudo apt install -y python3.11-venv
cd testTask-upshell || { echo "Ошибка"; exit 1; }
python3.11 -m venv venv || { echo "Ошибка"; exit 1; }
source venv/bin/activate || { echo "Ошибка"; exit 1; }

echo "Установка poetry..."
pip install poetry || { echo "Ошибка"; exit 1; }

poetry install || { echo "Ошибка"; exit 1; }
make run || { echo "Ошибка"; exit 1; }

echo "Done"