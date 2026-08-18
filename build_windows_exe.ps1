$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

pyinstaller --onefile --windowed --noconsole --name ImageToArrayConverter --distpath .\dist\windows .\image_to_array.py

Write-Host "Windows exe generated in .\dist\windows"
