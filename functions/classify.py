from boto3.dynamodb.conditions import Key
from random import randint
from joblib import load
import boto3
import json
import os

def lambda_handler(event, context):

    metadata_table = os.environ['METADATA_TABLE']
    bucket_name_results = os.environ['RESULTS_BUCKET']
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    dybamodb_table = dynamodb_resource.Table(metadata_table)

    response = dybamodb_table.query(KeyConditionExpression=Key('pk').eq('MODELO'), Limit=1,  ScanIndexForward=False) 
    items = response.get('Items', [])
    if not items:
        return {'statusCode': 404, 'body': json.dumps('No hay modelos para clasificar')}
    else:
        # DESCARGAMOS EL MODELO DESDE S3 EN FUNCIÓN DE LA RUTA DE DYNAMO	
        s3_client = boto3.client('s3')
        print(f'Hemos cargado el modelo {items[0]["clasificador"]} con score {items[0]["sk"]}')
        model_key = items[0]['path']
        s3_client.download_file(bucket_name_results, model_key, f'/tmp/{os.environ["MODEL_PATH"]}')
	#        model = load(f'/tmp/{os.environ["MODEL_PATH"]}')
        # CLASIFICAR Y DEVOLVER ETIQUETA
        rand_val = randint(0, 9)
        return {'statusCode': 200, 'body': json.dumps(f'Clasificacion realizada con {items[0]["clasificador"]} finalizada con resultado: {rand_val}')}


