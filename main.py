import aiohttp
from aiohttp import web
import asyncio
import json
import os
import requests
import json
import subprocess
from flask import Flask

# app = Flask(__name__)

TOKEN = os.environ["API_TOKEN"]
API_URL = f'https://api.telegram.org/bot{TOKEN}/'


def main():
    r = requests.get(API_URL + 'getUpdates')
    print(r.json())

if __name__ == '__main__':
    # app.run()
    main()