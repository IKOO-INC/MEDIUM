import requests
from bs4 import BeautifulSoup

########################### PAYMENT AWAL PENENTUAN METHOD ############
url = "https://siapik.com/aplikasi/wallet/payment_channel"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://siapik.com",
    "Referer": "https://siapik.com/aplikasi/wallet/top_up",
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
}

cookiess = {
    "ci_session_SiApik": "quk9uhrokgs8kbra046tgejirlgm6tgt",
    "csrf_cookie_SiApik": "d3574a22caa7c86f79fddc985e09b84c",
    "cfzs_google-analytics_v4": "%7B%22edeS_pageviewCounter%22%3A%7B%22v%22%3A%2237%22%7D%7D",
    "cfz_google-analytics_v4": "%7B%22edeS_engagementDuration%22%3A%7B%22v%22%3A%220%22%2C%22e%22%3A1816586509410%7D%2C%22edeS_engagementStart%22%3A%7B%22v%22%3A1785050510087%2C%22e%22%3A1816586510792%7D%2C%22edeS_counter%22%3A%7B%22v%22%3A%22159%22%2C%22e%22%3A1816586509410%7D%2C%22edeS_session_counter%22%3A%7B%22v%22%3A%2214%22%2C%22e%22%3A1816586509410%7D%2C%22edeS_ga4%22%3A%7B%22v%22%3A%2221903056-157d-43fd-95b4-8e23c6deb8b3%22%2C%22e%22%3A1816586509410%7D%2C%22edeS__z_ga_audiences%22%3A%7B%22v%22%3A%2221903056-157d-43fd-95b4-8e23c6deb8b3%22%2C%22e%22%3A1809615896472%7D%2C%22edeS_let%22%3A%7B%22v%22%3A%221785050509410%22%2C%22e%22%3A1816586509410%7D%2C%22edeS_ga4sid%22%3A%7B%22v%22%3A%221257000746%22%2C%22e%22%3A1785052309410%7D%7D"
  }


data = {
    "csrf_token_SiApik": "d3574a22caa7c86f79fddc985e09b84c",
    "amount": "70000"
}

response = requests.post(
    url,
    headers=headers,
    cookies=cookiess,
    data=data,
    timeout=30
)

print("Status:", response.status_code)
soup = BeautifulSoup(response.text, "html.parser")

csrf = soup.find("input", {"name": "csrf_token_SiApik"})["value"]

print("CSRF baru:", csrf)
########################### PAYMENT DUA GASKEUNN ############################