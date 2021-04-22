import pandas as pd
from io import StringIO
from random import randint
from decimal import Decimal
from urllib.parse import unquote_plus
import json
import boto3
import os
import uuid
import time

def lambda_handler(event, context):

    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    s3_client = boto3.client('s3')

    event_bucket = event['Records'][0]['s3']['bucket']['name']
    event_key = unquote_plus(event['Records'][0]['s3']['object']['key'])        
    bucket_name_results = os.environ['RESULTS_BUCKET']    

    csv_obj = s3_client.get_object(Bucket=event_bucket, Key=event_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    train = pd.read_csv(StringIO(csv_string))

    # PARTICIONAR características / etiquetas 

    #    X_train = train.iloc[:,1:]
    #    y_train = train.iloc[:,0]

    # Entrenar y obtener score

    model_score = randint(0, 100)    
    model = {}
    with open(f'/tmp/{os.environ["MODEL_PATH"]}', 'w') as outfile:    
        json.dump(model, outfile)
    rand_prefix = str(uuid.uuid1())[:6]
    model_name = os.environ["MODEL_PATH"]
    remote_path = f'{rand_prefix}/{model_name}'
    s3_client.upload_file(f'/tmp/{os.environ["MODEL_PATH"]}', bucket_name_results, remote_path)

    metadata_table = os.environ['METADATA_TABLE']
    dybamodb_table = dynamodb_resource.Table(metadata_table)
    dynamo_entry = {'pk': 'MODELO', 'sk': Decimal(str(model_score)), 'path': remote_path, 'dataset_train': event_key}

    # Incluir información adicional con metadatos

    dynamo_entry.update(fecha_generacion=Decimal(str(int(time.time() * 1000))))
    dynamo_entry.update(clasificador="Ninguno")
    dynamo_entry.update(hiper_param_a="A")
    dynamo_entry.update(hiper_param_b="B")
    dybamodb_table.put_item(Item=dynamo_entry)
    return {
        'statusCode': 200,
        'body': json.dumps(f'Modelo entrenado con score score {model_score} y guardado en {remote_path}')
    }

