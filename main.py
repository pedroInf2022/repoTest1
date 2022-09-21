#!/usr/bin/env python
# coding: utf-8-sig

# Imports
from ast import Return, Try
from cmath import log
from distutils.log import info
from re import template
from turtle import up, update
from flask import Flask
import logging
from datetime import datetime, timedelta
import os

# Initialize flask app
app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Default route, does nothing
@app.route('/')
def blank():
    return 200

# Runs default report
@app.route("/run")
def run():
    print('STATUS: Report Run started')
    logging.info('Status: Report Run started')

    import os
    from modules.tetristools import dDay, hour, reportLog, credsFromDb, jobLog, sendLog
    from modules.kantar_nav import logMeIn
    from modules.kantar_nav import createReport
    import logging
    
    print('STATUS: Modules loaded')
    logging.info('STATUS: Modules loaded')
    
    # Cloud variables
    project_id = "amer-a01-us-amer-dv"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    credentials_table_id = 'amer_bqdset_medidata_br_us_dv.creds'
    report_log_table_id = 'amer_bqdset_medidata_br_us_dv.REPORT_LOG'
    job_log_table_id = 'amer_bqdset_medidata_br_us_dv.JOB_LOG'
          
    # Reads Kantar credentials from database
    platform = 'kantar'
    print(f'STATUS: reading {platform} credentials')
    logging.info(f'STATUS: reading {platform} credentials')
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    username = credentials[0]['username']
    password = credentials[0]['password']

    # Reads email credentials from database
    platform = 'email'
    print(f'STATUS: reading {platform} credentials')
    logging.info(f'STATUS: reading {platform} credentials')
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    mail_username = credentials[0]['username']
    mail_password = credentials[0]['password']

    print('STATUS: all credentials read')
    logging.info('STATUS: all credentials read')

    # Other mail configs
    receiver_email = 'luiz.passarelli@tetris.co'

    # REPORT OPTIONS
    report_name  = 'Job'

    # Sorts - Time period enters by default. limit of selections = 13
    sorts = ['Sector',
            'Category',
            'Subcategory',
            'Parent', 
            'Advertiser', 
            'Master Brand',
            'Product', 
            'Media',
            'Digital Ad Size', 
            'Digital Ad Type',
            'Site Category',
            'Parent Site',
            'Direct/Indirect'
            ]
    measures = ['Reais', 'Units', 'Impressions', 'Seconds']
    column_type = 'Pivot Export'
    # ytd = datetime.today().strftime("%Y") # Year to date
    # date_min = f'01-01-{ytd}' # Sets report starting date to first day of current year
    date_min = dDay(110)
    date_max = dDay(20) # DATE (dd-mm-YYYY) based on delta value. Default = 20 (data consolidation window)


    # REPORT CREATION
    
    # Creates default results object
    result = {'JOB':'RUN',
    'JOB_STATUS':'INCOMPLETE',
    'TEMPLATE_NAME':'',
    'CREATION_STATUS':'',
    'REPORT_NAME':'',
    'REPORT_STATUS':'',
    'FILE_NAME':'',
    'DATE_MIN':date_min,
    'DATE_MAX':date_max,
    'TIME':hour(),
    'ERROR': 'NONE'
    }
    returncode = 200

    try:
        # Creates Chrome driver and logs in with provided credentials
        driver = logMeIn(username, password)
        # Creates report with selected options and returns result
        job_result = createReport(driver, report_name, sorts, measures, column_type, date_min, date_max)
        result.update({'CREATION_STATUS':job_result['CREATION_STATUS'],
                        'REPORT_STATUS':job_result['REPORT_STATUS'],
                        'TEMPLATE_NAME':job_result['TEMPLATE_NAME'],
                        'REPORT_NAME':job_result['REPORT_NAME']
                    })
        logging.info('STATUS: Report created')
        print('Report created')
    except Exception as e:
        print(e)
        returncode = 401
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not create report - {e}')
    

    # LOG
    if returncode == 200:
        result.update({'JOB_STATUS':'SUCCESS'})

    try:
        # Updates result with job run result
        result.update(job_result)
        # Writes result on Google BigQuery
        reportLog(result, report_log_table_id, project_id)
        jobLog(result, job_log_table_id)
        print('Results logged to database')
        logging.info('STATUS: Results logged to database')
    except Exception as e:
        print(e)
        returncode = 402
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not log job on database - {e}')

    # Sends log file to email
    sendLog(mail_username, mail_password, receiver_email, result)
    return returncode

@app.route("/run_s/<start>/<finish>")
def run_s(start=110, finish=20):

    import os
    from modules.tetristools import dDay, hour, reportLog, credsFromDb, jobLog, sendLog
    from modules.kantar_nav import logMeIn
    from modules.kantar_nav import createReport
    import logging
    
    print('STATUS: Report Run started')
    logging.info('Status: Report Run started')
    
    print('STATUS: Modules loaded')
    logging.info('STATUS: Modules loaded')
    
    # Cloud variables
    project_id = "amer-a01-us-amer-dv"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    credentials_table_id = 'amer_bqdset_medidata_br_us_dv.creds'
    report_log_table_id = 'amer_bqdset_medidata_br_us_dv.REPORT_LOG'
    job_log_table_id = 'amer_bqdset_medidata_br_us_dv.JOB_LOG'
          
    # Reads Kantar credentials from database
    platform = 'kantar'
    print(f'STATUS: reading {platform} credentials')
    logging.info(f'STATUS: reading {platform} credentials')
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    username = credentials[0]['username']
    password = credentials[0]['password']

    # Reads email credentials from database
    platform = 'email'
    print(f'STATUS: reading {platform} credentials')
    logging.info(f'STATUS: reading {platform} credentials')
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    mail_username = credentials[0]['username']
    mail_password = credentials[0]['password']

    print('STATUS: all credentials read')
    logging.info('STATUS: all credentials read')

    # Other mail configs
    receiver_email = 'luiz.passarelli@tetris.co'

    # REPORT OPTIONS
    report_name  = 'Job'

    # Sorts - Time period enters by default. limit of selections = 13
    sorts = ['Sector',
            'Category',
            'Subcategory',
            'Parent', 
            'Advertiser', 
            'Master Brand',
            'Product', 
            'Media',
            'Digital Ad Size', 
            'Digital Ad Type',
            'Site Category',
            'Parent Site',
            'Direct/Indirect'
            ]
    measures = ['Reais', 'Units', 'Impressions', 'Seconds']
    column_type = 'Pivot Export'
    ytd = datetime.today().strftime("%Y") # Year to date
    if start == 110:
        date_min = dDay(start) # Sets report starting date to first day of current year
    else:
        date_min = start
    
    if finish == 20:
        date_max = dDay(finish) # DATE (dd-mm-YYYY) based on delta value. Default = 30 (data consolidation window)
    else:
        date_max = finish


    # REPORT CREATION
    
    # Creates default results object
    result = {'JOB':'RUN_S',
    'JOB_STATUS':'INCOMPLETE',
    'TEMPLATE_NAME':'',
    'CREATION_STATUS':'',
    'REPORT_NAME':'',
    'REPORT_STATUS':'',
    'FILE_NAME':'',
    'DATE_MIN':date_min,
    'DATE_MAX':date_max,
    'TIME':hour(),
    'ERROR': 'NONE'
    }
    returncode = 200

    try:
        # Creates Chrome driver and logs in with provided credentials
        driver = logMeIn(username, password)
        # Creates report with selected options and returns result
        job_result = createReport(driver, report_name, sorts, measures, column_type, date_min, date_max)
        result.update({'CREATION_STATUS':job_result['CREATION_STATUS'],
                        'REPORT_STATUS':job_result['REPORT_STATUS'],
                        'TEMPLATE_NAME':job_result['TEMPLATE_NAME'],
                        'REPORT_NAME':job_result['REPORT_NAME']
                    })
        logging.info('STATUS: Report created')
        print('Report created')
    except Exception as e:
        print(e)
        returncode = 401
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not create report - {e}')
    

    # LOG
    if returncode == 200:
        result.update({'JOB_STATUS':'SUCCESS'})

    try:
        # Updates result with job run result
        result.update(job_result)
        # Writes result on Google BigQuery
        reportLog(result, report_log_table_id, project_id)
        jobLog(result, job_log_table_id)
        print('Results logged to database')
        logging.info('STATUS: Results logged to database')
    except Exception as e:
        print(e)
        returncode = 402
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not log job on database - {e}')

    # Sends log file to email
    sendLog(mail_username, mail_password, receiver_email, result)
    return returncode
    
@app.route("/get")
def get():
    print('Report Get started')
    logging.info('STATUS: Report Get started')
    
    import os
    from modules.tetristools import sendLog, reportLog, lastCreated, dataToStorage, credsFromDb, hour, jobLog
    from modules.kantar_nav import logMeIn
    from modules.kantar_nav import getReport

    print('STATUS: Modules loaded')
    logging.info('STATUS: Modules loaded')

    # Cloud variables
    project_id = "amer-a01-us-amer-dv"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    credentials_table_id = 'amer_bqdset_medidata_br_us_dv.creds'
    bucket_name = 'amer-dp2-gcs-dv-medidata-br-landing'
    report_log_table_id = 'amer_bqdset_medidata_br_us_dv.REPORT_LOG'
    job_log_table_id = 'amer_bqdset_medidata_br_us_dv.JOB_LOG'

    # Reads Kantar credentials from database
    platform = 'kantar'
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    username = credentials[0]['username']
    password = credentials[0]['password']

    # Reads email credentials from database
    platform = 'email'
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    mail_username = credentials[0]['username']
    mail_password = credentials[0]['password']

    print('STATUS: all credentials read')
    logging.info('STATUS: all credentials read')

    # Other mail configs
    receiver_email = 'luiz.passarelli@tetris.co'
    
    # Creates default results object
    result = {'JOB':'GET',
    'JOB_STATUS':'INCOMPLETE',
    'TEMPLATE_NAME':'',
    'CREATION_STATUS':'',
    'REPORT_NAME':'',
    'REPORT_STATUS':'',
    'FILE_NAME':'',
    'DATE_MIN':'',
    'DATE_MAX':'',
    'TIME':hour(),
    'ERROR': 'NONE'
    }
    returncode = 200


    # REPORT DOWNLOAD
    print('Getting template names')
    logging.info('STATUS: Getting template names')
    try:
        # Reads last not downloaded report from database
        last_result = lastCreated(project_id, report_log_table_id)
        result.update(last_result)
        print('Report names received')
        logging.info('Report names received')
    except Exception as e:
        print(e)
        returncode = 403
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not search the database for reports to download - {e}')

    # Checks if query resulted on an empty list
    print('Checking reports status')
    logging.info('STATUS: Checking reports status')

    if len(last_result) > 0:
        print('There are reports to download')
        logging.info('STATUS: There are reports to download')
        template_name = last_result['TEMPLATE_NAME']
        # DOWNLOAD
        try:
            # Creates Chrome driver
            driver = logMeIn(username, password)
            # Downloads report
            download_result = getReport(driver, template_name)
            driver.quit()
            result.update(download_result)
            print(f"Report downloaded {download_result['FILE_NAME']}")
            logging.info(f"STATUS: Report downloaded {download_result['FILE_NAME']}")
        except Exception as e:
            print(e)
            returncode = 405
            result.update({'JOB_STATUS':f'ERROR'})
            result.update({'ERROR':returncode})
            logging.error(f'ERROR: Could not download report - {e}')


        # Uploads to Cloud Storage
        try:
            source_file_name = '/reports/' + download_result['FILE_NAME']
            destination_blob_name = 'mediadatabr/' + download_result['FILE_NAME']
            dataToStorage(bucket_name, source_file_name, destination_blob_name)
            print('File uploaded to cloud storage: ',destination_blob_name)
            logging.info(f'STATUS: File uploaded to Cloud Storage: {destination_blob_name}')
        except Exception as e:
            print(e)
            returncode = 406
            result.update({'JOB_STATUS':f'ERROR'})
            result.update({'ERROR':returncode})
            logging.error(f'ERROR: Could not Upload report to Cloud Storage - {e}')

    else:
        print('Nothing left to download')
        logging.info('STATUS: Nothing left to download')

    # Updates result
    if returncode == 200:
        result.update({'JOB_STATUS':'SUCCESS'})
        
    try:
        # Sends results to BigQuery log table
        reportLog(result, report_log_table_id, project_id)
        jobLog(result, job_log_table_id)
        print('Results logged to database')
        logging.info('STATUS: Results logged to database')
    except Exception as e:
        print(e)
        returncode = 402
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not log job on database - {e}')

            
    # Sends log file to email
    sendLog(mail_username, mail_password, receiver_email, result)
    return returncode

@app.route("/push")
def push():
    print('Report Push started')
    logging.info('STATUS: Report Push started')

    import pandas as pd
    import os
    from modules.tetristools import lastDownloaded, dataClean, reportLog, dataFromStorage, pushToGbq, sendLog, credsFromDb, jobLog, hour

    print('Modules loaded')
    logging.info('STATUS: Modules loaded')
    
    # Cloud variables
    project_id = "amer-a01-us-amer-dv"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    credentials_table_id = 'amer_bqdset_medidata_br_us_dv.creds'
    bucket_name = 'amer-dp2-gcs-dv-medidata-br-landing'
    raw_table_id = 'amer_bqdset_medidata_br_us_dv.RAW'
    report_log_table_id = 'amer_bqdset_medidata_br_us_dv.REPORT_LOG'
    job_log_table_id = 'amer_bqdset_medidata_br_us_dv.JOB_LOG'
    
    # Reads email credentials from database
    platform = 'email'
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    mail_username = credentials[0]['username']
    mail_password = credentials[0]['password']

    # Other mail configs
    receiver_email = 'luiz.passarelli@tetris.co'

    result = {'JOB':'PUSH',
    'JOB_STATUS':'INCOMPLETE',
    'TEMPLATE_NAME':'',
    'CREATION_STATUS':'',
    'REPORT_NAME':'',
    'REPORT_STATUS':'',
    'FILE_NAME':'',
    'DATE_MIN':'',
    'DATE_MAX':'',
    'TIME':hour(),
    'ERROR': 'NONE'
    }
    returncode = 200
    
    
    # DOWNLOAD
    print('Fetching reports ready for push')
    logging.info('STATUS: Fetching reports ready for push')
    
    try:
        # Reads last downloaded report
        lastDownloaded_result = lastDownloaded(project_id, report_log_table_id)
        print(f"Last report: {lastDownloaded_result['template_name']}")
        logging.info(f"Last report: {lastDownloaded_result['template_name']}")
        result.update({'TEMPLATE_NAME':lastDownloaded_result['template_name'],
                        'FILE_NAME':lastDownloaded_result['file']
                    })
        print('Report ready for push to Big Query')
        logging.info(f"STATUS: Report ready for push to Big Query {lastDownloaded_result['template_name']}")
    except Exception as e:
        print(e)
        returncode = 407
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not get last downloaded report - {e}')
    
    

    # Downloads from Cloud Storage
    destination_file_name = '/reports/' + lastDownloaded_result['file']
    source_blob_name = 'mediadatabr/' + lastDownloaded_result['file']

    try:
        dataFromStorage(bucket_name, destination_file_name, source_blob_name)
        print(f'File downloaded - {source_blob_name}')
        logging.info(f'STATUS: File downloaded - {source_blob_name}')
    except Exception as e:
        print(e)
        returncode = 408
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not retrieve file from Cloud Storage - {e}')

    # Creates dataframe
    print('Creating dataframe')
    logging.info('STATUS: Creating dataframe')
    df = pd.read_csv(destination_file_name, encoding='1252', skiprows=5, skipfooter=5, engine='python')

    # Column titles manipulation
    # df.columns = df.columns.str.replace({' ':'_'})
    # df.columns = df.columns.str.replace({'/':'_'})
    # df.columns = df.columns.str.replace({"$":'EAIS'}, regex=True)
    df = df.rename(columns=lambda s: s.replace(" ", "_"))
    df = df.rename(columns=lambda s: s.replace("/", "_"))
    df = df.rename(columns=lambda s: s.replace("$", "EAIS",))

    # Converts TIME_PERIOD column to datetime
    print('Formatting time period')
    df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'], format="%d/%m/%Y") # DEFAULT
    # df.TIME_PERIOD = df.TIME_PERIOD.apply(lambda x: x.date()) # TEST IMPORT BACKUPS
    print(df)

    # Reads data starting date
    data_start_date = df['TIME_PERIOD'].min()
    data_end_date = df['TIME_PERIOD'].max()
    print('End date =', data_end_date)

    print('Dataframe created')
    logging.info('STATUS: Dataframe created')

    # Deletes data with timestamp in data interval
    print('Clearing old data')
    logging.info('STATUS: Clearing old data')
    try:
        dataClean(project_id, raw_table_id, data_start_date, data_end_date)
        print('Data cleared successfully')
        logging.info('STATUS: Data cleared successfully')
    except Exception as e:
        print(e)
        returncode = 409
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not clear old data from database - {e}')

    # Appends new data into database
    # pandas_gbq.to_gbq(df, raw_table_id, project_id=project_id, if_exists='append')
    
    print('Pushing new data')
    logging.info('STATUS: Pushing new data')
    
    try:
        pushToGbq(df, raw_table_id)
        print('Raw data pushed to BigQuery')
        logging.info('STATUS: Raw data pushed to BigQuery')
    except Exception as e:
        print(e)
        returncode = 410
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not push data to raw table - {e}')

    # Updates result
    if returncode == 200:
        result.update({'JOB_STATUS':'SUCCESS','REPORT_STATUS':'COMMITTED TO DATABASE'})

    # Sends results to BigQuery log table
    try:
        reportLog(result, report_log_table_id, project_id)
        jobLog(result, job_log_table_id)
        print('Results logged to database')
        logging.info('STATUS: Results logged to database')
    except Exception as e:
        print(e)
        returncode = 402
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not log job on database - {e}')

    # Sends log file to email
    sendLog(mail_username, mail_password, receiver_email, result)
    return returncode

@app.route("/model")
def model():
    from modules.tetristools import credsFromDb, pushToGbq, dataClean, dfFromTable, jobLog, reportLog, sendLog, hour
    from modules.data_model import dataModel
    import pandas as pd
    import os

    # Cloud variables
    project_id = "amer-a01-us-amer-dv"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    credentials_table_id = 'amer_bqdset_medidata_br_us_dv.creds'
    raw_table_id = 'amer_bqdset_medidata_br_us_dv.RAW'
    lookup_table_id = 'amer_bqdset_medidata_br_us_dv.LOOKUP'
    base_table_id = 'amer_bqdset_medidata_br_us_dv.BASE_TEST'
    job_log_table_id = 'amer_bqdset_medidata_br_us_dv.JOB_LOG'
    
    # Reads email credentials from database
    platform = 'email'
    credentials = credsFromDb(platform, project_id, credentials_table_id)
    mail_username = credentials[0]['username']
    mail_password = credentials[0]['password']
    receiver_email = 'luiz.passarelli@tetris.co'

    result = {'JOB':'MODEL',
    'JOB_STATUS':'INCOMPLETE',
    'TEMPLATE_NAME':'',
    'CREATION_STATUS':'',
    'REPORT_NAME':'',
    'REPORT_STATUS':'',
    'FILE_NAME':'',
    'DATE_MIN':'',
    'DATE_MAX':'',
    'TIME':hour(),
    'ERROR': 'NONE'
    }
    returncode = 200

    try:
        df_raw = dfFromTable(project_id, raw_table_id)
        df_lookup = dfFromTable(project_id, lookup_table_id)
        print('Databases retrieved as dataframes')
        logging.info('STATUS: Databases retrieved as dataframes')
    except Exception as e:
        print(e)
        returncode = 411
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not retrieve databases as dataframes - {e}')


    print('Modeling data')
    logging.info('STATUS: Modeling data')
    # Run modeling script
    try:
        df_base = dataModel(df_raw, df_lookup)
        print('Data modeling success')
        logging.info('STATUS: Data modeling success')
    except Exception as e:
        print(e)

    # Update result
    data_start_date = df_base['TIME_PERIOD'].min()
    data_end_date = df_base['TIME_PERIOD'].max()
    result.update({'DATE_MIN':data_start_date,'DATE_MAX':data_end_date})


    # Deletes data with timestamp in data interval
    print('Clearing old data')
    logging.info('STATUS: Clearing old data')
    try:
        dataClean(project_id, base_table_id, data_start_date, data_end_date)
        print('Data cleared successfully')
        logging.info('STATUS: Data cleared successfully')
    except Exception as e:
        print(e)
        returncode = 409
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not clear old data from database - {e}')


    # Push results to base
    print('Pushing results to BigQuery')
    try:
        pushToGbq(df_base, base_table_id, overwrite=True)
        print('Modeled data pushed to Big Query')
        logging.info('STATUS: Modeled data pushed to Big Query')
    except Exception as e:
        print(e)
        returncode = 412
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not push data to database - {e}')

    # Create incomplete products export
    df_incomplete = df_base.loc[df_base['MARCA_LOREAL'].isnull()]
    df_incomplete = df_incomplete.drop(columns=[
        'TIME_PERIOD',
        'SECTOR',
        'MEDIA',
        'WEB_AD_SIZE',
        'DIGITAL_AD_TYPE',
        'SITE_CATEGORY',
        'PARENT_SITE',
        'DIRECT_INDIRECT',
        'REAIS',
        'UNITS',
        'DIGITAL_IMP',
        'SEC',
        'TOP_PLAYERS',
        'SIGLA'
        ])
    df_incomplete = df_incomplete.drop_duplicates()
    print('df_incomplete:')
    print(df_incomplete)
    

    if returncode == 200:
        result.update({'JOB_STATUS':'SUCCESS'})
        
    try:
        # Sends results to BigQuery log table
        jobLog(result, job_log_table_id)
        print('Results logged to database')
        logging.info('STATUS: Results logged to database')
    except Exception as e:
        print(e)
        returncode = 402
        result.update({'JOB_STATUS':f'ERROR'})
        result.update({'ERROR':returncode})
        logging.error(f'ERROR: Could not log job on database - {e}')
    
    # Sends log file to email
    sendLog(mail_username, mail_password, receiver_email, result)
    return returncode

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))