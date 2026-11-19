
from settings.settings import form_uid, api_token, key_json
from settings.settings import url, headers, key_json
from sources.helpi import run_helpi
# from sources.hand_kobo import download_ecxel_kobo
from sources.kobo import run_kobo
# from transformation.global_dataset import concat


run_helpi(url, headers, key_json)
print("***************************** \n*** Дані Хелпі завантажені *** \n*****************************")
run_kobo(form_uid, api_token, key_json)
print("***************************** \n*** Дані Kobo завантажені *** \n*****************************")
