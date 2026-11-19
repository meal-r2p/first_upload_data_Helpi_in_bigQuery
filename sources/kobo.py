import requests
import pandas as pd
import json
from google.cloud import bigquery

def download_from_koboform(form_uid, api_token):

    # Параметры для "request" запроса
    url = f"https://eu.kobotoolbox.org/api/v2/assets/{form_uid}/data/"
    headers = {"Authorization": f"Token {api_token}"}
    params = {"limit": 1000}

    global_dataset = []
    members_dataset = []

    while url:
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()
        # read = json.dumps(data["results"], indent=4, ensure_ascii=False)
        results = data.get("results")
        y = global_dataset.extend(results)

        params = None
        url = data.get("next")

    dfA = pd.DataFrame(global_dataset)
    dfA["id"] = range(len(dfA))

    dfB = dfA[["id", "Members"]].explode(column='Members', ignore_index=True)
    members = pd.json_normalize(dfB["Members"])
    dfB = pd.concat([members, dfB['id']], axis=1)

    
    return dfA, dfB


def merge_kobo(dfB1, dfB2):

    # Поєднуємо вкладки з датасету Кобо
    dfB = dfB1.merge(dfB2, how='left', left_on='id', right_on='id')

    # Створюємо стовбець dfB['index']
    dfB['index'] = range(len(dfB))

    # Створюємо стовбець dfA['DataSource']
    dfB['DataSource'] = dfB['DataSource'] = 'Дані з kobo'

    return dfB


def veterans_table(dfB):
    veteran_labels = {
    'Members/veteran': 'Ветеран_ка',
    'Members/member_veteran_family': "Член сім'ї ветерана_ки",
    'Members/member_family_fallen_soldier': 'Член сім’ї загиблого (померлого) захисника_ці',
    'Members/Family_captivity': 'Член сім’ї полоненого військовослужбовця_иці',
    'Members/Family_missing': "Член сім'ї безвісно відсутнього військовослужбовця",
    'Members/Veteran_parameters/soldier_family': 'Член сім’ї військовослужбовця_иці',
    'Members/Veteran_parameters/widow': 'Вдова',
    'Members/Civil_captivity': 'Цивільний_полон',
    'Members/Veteran_parameters/veteran_none': 'veteran_none',
    }
    veteran_name = veteran_labels.values()
    dfB_veterans = dfB.rename(columns=veteran_labels)[veteran_name]
    dfB_veterans['index'] = range(len(dfB_veterans))

    return dfB_veterans


def veterans_melt_and_filter(dfB_veterans):

    # Трансформація таблиці у довгий формат "Wide to Long"
    dfB_veterans_long = dfB_veterans.melt(
    id_vars=['index'],
    var_name="Участь у бойових діях військослужбовців",
    value_name='values'
    )

    # Фільтрація значень стовбця ['values'] == 'Yes'
    mask = dfB_veterans_long['values'] == 'Yes'
    dfB_veterans_filter = dfB_veterans_long.loc[mask]

    return dfB_veterans_filter


def rename_labels_kobo(dfB):

    labels = {
    # 'Id': 'Id',
    # 'BeneficiaryId': 'BeneficiaryId',
    # 'ServiceId': 'ServiceId',
    'Format': 'CardName',
    # 'RoleName': 'RoleName',
    'Date': 'Дата',
    # 'Виконавець': 'Виконавець',
    'direction': 'Програма',
    # 'Напрям захисту ВПО та постраждалого населення': 'Напрямок',
    'Project': 'Проєкт',
    # 'Кількість бенефіціарів': 'Кількість бенефіціарів',
    # 'oblast': 'Місце надання послуги (область)',
    # 'Місце надання послуги (область) (код)': 'Місце надання послуги (область) (код)',
    # 'raion': 'Місце надання послуги (район)',
    # 'Місце надання послуги (район) (код)': 'Місце надання послуги (район) (код)',
    # 'hromada': 'Місце надання послуги (громада)',
    # 'Місце надання послуги (громада) (код)': 'Місце надання послуги (громада) (код)',
    # 'settlement': 'Місце надання послуги (населений пункт)',
    # 'Місце надання послуги (населений пункт) (код)': 'Місце надання послуги (населений пункт) (код)',
    # 'Місце надання послуги (МТП)': 'Місце надання послуги (МТП)',
    # 'Місце надання послуги (МТП) (код)': 'Місце надання послуги (МТП) (код)',
    'Members/Surname': 'Прізвище',
    'Members/Name': "Ім'я",
    # 'По батькові': 'По батькові',
    'Members/Age': 'Дата народження',
    'Members/Sex': 'Стать',
    'Members/Phone': 'Телефон',
    # 'Статус переміщення / громадянства': 'Статус переміщення / громадянства',
    'Members/Disabilities': 'Інвалідність',
    # 'Участь у бойових діях / пов’язаність з військовою службою': 'Участь у бойових діях / пов’язаність з військовою службою',
    'Members/Etnicity': 'Чи належить людина до ромської національної меншини',
    # 'Місце поточного проживання (область)': 'Місце поточного проживання (область)',
    # 'Місце поточного проживання (область) (код)': 'Місце поточного проживання (область) (код)',
    # 'Місце поточного проживання (район) (код)': 'Місце поточного проживання (район) (код)',
    # 'Місце поточного проживання (громада)': 'Місце поточного проживання (громада)',
    # 'Місце поточного проживання (громада) (код)': 'Місце поточного проживання (громада) (код)',
    # 'Місце поточного проживання (населений пункт)': 'Місце поточного проживання (населений пункт)',
    # 'Місце поточного проживання (населений пункт) (код)': 'Місце поточного проживання (населений пункт) (код)',
    # 'Status_y': 'Поточний статус перебування / проживання',
    'Training_name': 'Назва заходу',
    # 'Структура навчальної програми': 'Структура навчальної програми',
    # 'Офіс': 'Офіс',
    '_': 'Формат проведення',
    'DataSource': 'DataSource',
    'index': 'index'
    }
    name = labels.values()
    dfB = dfB.rename(columns=labels)[name]

    return dfB


def merge_veterans_with_kobo_table(dfB, dfB_veterans_filter):

    # поєднуємо дві таблиці
    dfB = dfB.merge(dfB_veterans_filter[["Участь у бойових діях військослужбовців", 'index']], how='left', on='index')

    return dfB

def split_name_beneficiar(dfB):

    dfB['Прізвище'] = dfB["Ім'я"].str.split(' ', n=1).str[0]
    dfB["По батькові"] = dfB["Ім'я"].str.rsplit(' ', n=1).str[-1]
    dfB["Ім'я"] = dfB["Ім'я"].str.split(' ', n=2).str[1]

    return dfB

def correct_data_type(dfB):

    dfB = dfB.astype('string')
    dfB['Дата'] = pd.to_datetime(dfB['Дата']).dt.date

    return dfB


key = r"D:\data_science\R2P_service_acount_API_key.json"
project = "forward-bucksaw-515009-h0"
dataset = "all_datasets"
table = "Kobo_data"
write_mode="WRITE_TRUNCATE"

def upload_to_bigquery(df, key, project, dataset, table, write_mode):

    # 1. Connect to BigQuery
    client = bigquery.Client.from_service_account_json(json_credentials_path=key, project=project)

    # 2. Define table
    table_id = f"{project}.{dataset}.{table}"

    # 3. Configure upload
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    # 4. Upload DataFrame
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

    # 5. Wait for completion
    job.result()

    # 6. Get table information
    result = client.get_table(table_id)

    return result


def run_kobo(form_uid, api_token):

    dfB1, dfB2 = download_from_koboform(form_uid, api_token)
    dfB = merge_kobo(dfB1, dfB2)
    dfB_veterans = veterans_table(dfB)
    dfB_veterans_filter = veterans_melt_and_filter(dfB_veterans)
    dfB = rename_labels_kobo(dfB)
    dfB = merge_veterans_with_kobo_table(dfB, dfB_veterans_filter)
    dfB = split_name_beneficiar(dfB)
    dfB = correct_data_type(dfB)

    upload_to_bigquery(dfB, key, project, dataset, table, write_mode)

