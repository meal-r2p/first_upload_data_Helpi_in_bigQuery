import requests
import pandas as pd
from io import BytesIO
from google.cloud import bigquery


def connect_to_Helpy(url, headers):

    response = requests.get(url, headers=headers)
    df = pd.read_csv(
        BytesIO(response.content),
        sep=";",
        encoding="utf-8-sig"
    )

    return df


def work_data(dfA):

    # Створюємо стовбець dfA['DataSource']
    dfA['DataSource'] = dfA['DataSource'] = 'Дані з Helpi'

    # Видаляємо стовбці 
    delete = ['Count', 'Id', 'BeneficiaryId', 'ServiceId']
    dfA = dfA.drop(columns=delete)

    dfA = dfA[['DataSource', 'Дата', 'CardName', 'RoleName', 'Виконавець', 'Програма', 'Напрямок', 'Проєкт',  'Кількість бенефіціарів', 'Прізвище', "Ім'я", 'По батькові',  'Дата народження', 'Стать', 'Телефон',  'Інвалідність', 'Чи належить людина до ромської національної меншини', 'Назва заходу', 'Структура навчальної програми', 'Офіс', 'Формат проведення']]
    # `DataSource`, `Дата`, `Проєкт`, `Програма`, `Ім'я`,`Телефон`,`Стать`, CardName, `Формат проведення`, `Прізвище`, `Дата народження`, `Інвалідність`, `Назва заходу`, `Чи належить людина до ромської національної меншини`
        
    return dfA


def correct_data_type(dfA):

    dfA = dfA.astype('string')
    dfA['Дата'] = pd.to_datetime(dfA['Дата']).dt.date

    return dfA

# Тут має щось буть ...



# key = r"D:\data_science\R2P_service_acount_API_key.json"
project = "forward-bucksaw-515009-h0"
dataset = "all_datasets"
table = "Helpi_data"
write_mode="WRITE_TRUNCATE"


def upload_to_bigquery(df, key_json, project, dataset, table, write_mode):

    # 1. Connect to BigQuery
    client = bigquery.Client.from_service_account_json(json_credentials_path=key_json, project=project)

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





def run_helpi(url, headers, key_json):
    
    df = connect_to_Helpy(url, headers)
    df = work_data(df)
    df = correct_data_type(df)
    upload_to_bigquery(df, key_json, project, dataset, table, write_mode)


