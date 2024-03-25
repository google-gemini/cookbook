# Gemini Files API Sample Client Code

## Background
The Files API is part of the Gemini API family. This new API empowers developers to upload files for Gemini to use in multi-model scenarios. The files API is the most stable and least error prone method of unlocking multi-model support in your applications using Gemini.

This repository provides sample code for using the Files API with Gemini 1.5 API.


> [!IMPORTANT]
> The Files API is currently in early access. Features and endpoints may change. Please use with caution in production environments.


## Python Sample
```
# Prepare a virtual environment for Python.
python3 -m venv venv
source venv/bin/activate

# Add API key to .env file
touch .env
echo "GOOGLE_API_KEY='YOUR_API_KEY'" >> .env

# Install dependencies.
pip3 install -r requirements.txt

# Run the sample code.
python3 sample.py
```

## Node.js Sample
```
# Make sure npm is installed first. 

# Add API key to .env file
touch .env
echo "GOOGLE_API_KEY='YOUR_API_KEY'" >> .env

# Install dependencies.
npm install

# Run the sample code.
npm start
```

## cURL Bash Script Sample
```
bash ./sample.sh -a "<YOUR_KEY>" -i "sample_data/gemini.png" -d "gemini logo"
```
