import httpx
from pypasser import reCaptchaV3


recaptcha_version = "joHA60MeME-PNviL59xVH9zs"
sitekey = "6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOL"
configuration = "aHR0cHM6Ly9icy50bzo0NDM."  # https://bs.to:443

anchor_url = f"https://www.google.com/recaptcha/api2/anchor?ar=1&k={sitekey}&co={configuration}&hl=en&v={recaptcha_version}&size=invisible"
print("anchor_url", anchor_url)
reCaptcha_response = reCaptchaV3(anchor_url)

audio_url = f"https://www.google.com/recaptcha/api2/payload/audio.mp3?p={reCaptcha_response}&k={sitekey}"
#print("audio_url", audio_url)

userverify_url = f"https://www.google.com/recaptcha/api2/userverify?k={sitekey}"

data = {
    "v": recaptcha_version,

}



exit()

# Define the URL
url = 'https://bs.to/ajax/embed.php'

# Define the headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://bs.to/serie/2012-Das-Jahr-Null/1/1-Die-Entfuehrung/de',
    'Origin': 'https://bs.to',
    'Connection': 'keep-alive',
    'Cookie': '__ddg1_=FwTXJ9V4bcalzSqqwkTL; __bsduid=1k653tmmqsnvallc6ibegtsplh; seriesorder=genre',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'TE': 'trailers',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

# Define the payload
data = {
    'token': '67eef77e4e037b2a6ef2163f',
    'LID': '5649078',
    'ticket': str(reCaptcha_response) #'03AFcWeA6WyzTRsIwdPSmA1PiNutKwmmaujuAwLkMN5-hptBguOyCPPIxmsFDVSUP28uocc7XUO9rg4bD79TqN5OCpd5dkv68YDVtoYD2_5kC5rusBKaAYq70sIWqXhRCLZtvbcQa5RM_3dy_hj8VAm3NOpeGEWzcgeUkbm3JMDNTnTcMpoqWRlTWxGRKxUm9OsP8A897C2afmxAmlln-dUT2tBWGV-Q19ajKW3viZkMoJApBqrRjnHpQxr7G56pTwtUwrcq_pivKGlj2pQXELa7NJkqeieFhXgR--lkd3HD3iYFxHoBrhScIgcD9TVH13iBtz4MeWTjIigT0lmbkC6CeyCZE-5MBYaSbFCjsxDgL9uIYxWiL2-CRyB7jrjVjhEspnc5w5PzCOrwOAehHXUJhBX9foZba56380meug1N_nlfejuQdHgYwutd4G4_c695R8ZGTmN2_JIOphnEw4AMORdvJE2lJu2tB2bI7tW3fqlsSlYZxDkgtrYnsf0ODOpkNOu_zWbGMF9pqDKF3GmEu2OK1YnfrGJndz3V372IS-nRIffiTfOu2sxrfQae7jj4j_s5_X1Q74iuBmo4qnXc3xqOGyTDdBVMVau9lIg2ki0IP_R7iyJac9R584t6yxRbQmnCl0pAlvZrauhAa535HtxT08kP3z6K9F49CAktNWIft8x3_gix0',
}

# Make the POST request
response = httpx.post(url, headers=headers, data=data)

# Print the response
print(response.text)
