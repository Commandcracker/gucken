import re
import time
from bs4 import BeautifulSoup

html = '''
<input type="hidden" id="recaptcha-token" value="03AFcWeA63UNMqNIJHmaB6Xj6nRTgNHQisxw1SbdigJVrSWeexc8cCphD9Pc6JSeKSaaKZ3xrx_KXB14FXzO-HCNoG_DyJssDdZfeXuQnlpV5LWaVTc-02MqlYD8B0857IoymZ_aE7jbAErFjWJW4rmc_iwsi9NB8ELWFoMkv_rlT2baeDt5OG2FUosCIHSpzqq6CcKkKSk1MyVfV3XQyABbvvTfREOc3oVNhOKOD1foy0yk7p19ZhoANtlWX-4ARIzlCl_HuUPQuJxRPHZRcaQdRyQPr0rQrB1iSIkFx47xwRpmOVS6S_uWS5803pEIhy-Nx6tQ7vIwxgYC6VWVNeWm8WWY0p3VsKU7YBmWpsiidINyF_eQp6YoTOLOOpAtoUgiRZ8jb39GWgTHGYEuOceJMG9iKQC_puFRZsqb25xb3BV0jO5omOh1ejbagj2w6GcsuCyYJBgc626vS6Kiq0R4j6KUWZv268F2GDUHMJ9P-oNE6SkYgqsyDV_SUlWGNM_NCVUrNXbTCPMcDYDtG1uMniIWpjrl2uA3IdTM2P6bT9hiwzbBXF3WC9SaNWz3ZJtbP7sVQBy4dJJgySLKDv03j7XHBEMaBHs3q2HUg5EuUhWTa9NES9dfUfzPRytv29flC9_AFS_CX51pI2W4zN8OzqbeHT3SJnqPZDYxU7s2eU5sFj5XALklpH1AD80kRXFzK6RUfibxslQdHa_mehpOmIOqtlBi4OC6zDCMGt0o6kYhjYb-a4PkYgdUrxN8GdPFx5dpKckXPDducXSO0-Lsdo6zJQEJwvwwjSRJfPtMiPHtgGo0f1JKPjkiFy2G3NxvPeGSK_xo9qhbZ_M4Hp-ngbVYPqngpfm4yHH-xymrpuReF7E9gJr0sRPxNDmuDgGR9nkbxXN7YuS_ezoxlL9GJft5RkbpZgE8qVcv0NJAZymoTuh24IrYM8rZ0sFvaS3RyIgjM7szquv5_e0NgwXZQWAFWIOA47WjVgKs89VvpnwzLON7AoSB7YqSlMkDjH1rT2P4B3FBlNpPEwEqy23dMk3cfFZ_bhVBPI5kClgoNHbtF4E_dcwY1azHNgcpHLglNP-ekJcKW2k1rwArPsN6YGlKKlXIp4Q-k60VPJRPw3cpIzGfZ6HzCO4dWG5nMqEFsJxWJIt574aIaOBoYt9ZBCWBJcsayRpDwiUOsYaYR646gp35dHowVR9GdNHUmJsCEyhEDweyJZY3xGNqs7GSeBSpnIr-OMurrxEdlvJOhX5GCPl-_JLc1wXmoOP2iJAh1s6i-h9tzCdhtHj32xGccz-yh48Gi4nEPxfAk7TFlj0Ti0w5M2WVQ0v87oHjlStmj17vOAge4wcAN8kQZ-BrqWYSMO6DtoL45_3TdD42V-2hG0hOcxV8HsOYHnoymZqHg_WApHsENg5CfO6OywSNbRnNUaE9dDxsqt9KAUG0g8HIMGzuilefp2EdVTyiNbVtjcuBTg3agGvcS7UMsRLDXAyCqSRI3CLcBVvDaTuQXKovxUZpzDEtQQqtUUmvSuNbK0rHCpBKSQubqONThBTeegy3o3CIuKiA">
'''


# String manipulation method
def extract_value_string(html):
    start = html.find('id="recaptcha-token"')
    if start != -1:
        start = html.find('value="', start) + len('value="')
        end = html.find('"', start)
        return html[start:end]
    return None


# Regex method
def extract_value_regex(html):
    pattern = r'<input[^>]*id="recaptcha-token"[^>]*value="([^"]+)"'
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    return None


# BeautifulSoup method
def extract_value_bs4(html):
    soup = BeautifulSoup(html, 'html.parser')
    input_tag = soup.find('input', {'id': 'recaptcha-token'})
    if input_tag:
        return input_tag.get('value')
    return None


# Measure performance of string manipulation method
start_time = time.time()
for _ in range(100000):
    token = extract_value_string(html)
string_duration = time.time() - start_time

# Measure performance of regex method
start_time = time.time()
for _ in range(100000):
    token = extract_value_regex(html)
regex_duration = time.time() - start_time

# Measure performance of BeautifulSoup method
start_time = time.time()
for _ in range(100000):
    token = extract_value_bs4(html)
bs4_duration = time.time() - start_time

print(f"String manipulation duration: {string_duration:.6f} seconds")
print(f"Regex duration: {regex_duration:.6f} seconds")
print(f"BeautifulSoup duration: {bs4_duration:.6f} seconds")
