import requests
import math
from datetime import datetime, timedelta
from pathlib import Path
import sys
import pandas as pd
from collections import OrderedDict
import argparse

SERVER = "https://sonarcloud.io/"
ORGANIZATION = "apache"

def query_server(type, iter = 1, project_key = None, metric_list = []):

    page_size = 200
    params = {'p' : iter, 'ps':page_size}
    if type == 'projects':
        endpoint = SERVER + "api/components/search"
        params['organization'] = ORGANIZATION
        params['qualifiers'] = 'TRK'

    elif type == 'metrics':
        endpoint = SERVER + "api/metrics/search"

    elif type == 'analyses':
        endpoint = SERVER + "api/project_analyses/search"
        params['project'] = project_key

    elif type == 'measures':
        endpoint = SERVER + "api/measures/search_history"
        params['component'] = project_key
        params['metrics'] = ','.join(metric_list)

    else:
        print("ERROR: Illegal info type.")
        return None

    r = requests.get(endpoint, params=params)

    if r.status_code != 200:
        print(f"ERROR: HTTP Response code {r.status_code} for request {r.request.path_url}")
        return None

    r_dict = r.json()

    if type == 'projects':
        element_list = r_dict['components']
        total_num_elements = r_dict['paging']['total']
    elif type == 'metrics':
        element_list = r_dict['metrics']
        total_num_elements = r_dict['total']
    elif type == 'analyses':
        element_list = r_dict['analyses']
        total_num_elements = r_dict['paging']['total']
    elif type == 'measures':
        element_list = r_dict['measures']
        total_num_elements = r_dict['paging']['total']

    if iter*page_size < total_num_elements:
        if type == 'measures':
            element_list = concat_measures(element_list, query_server(type, iter+1, project_key))
        else:
            element_list = element_list + query_server(type, iter+1, project_key)
    
    return element_list

def concat_measures(measures_1,measures_2):
    for measure_1, measure_2 in zip(measures_1, measures_2):
        measure_1['history'] = measure_1['history'] + measure_2['history']
    return measures_1

def process_datetime(time_str):
    if time_str is None:
        return None

    ts = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")

    offset = timedelta(hours = int(time_str[20:22]), minutes = int(time_str[22:24]))

    if time_str[19] == '-':
        ts = ts + offset
    elif time_str[19] == '+':
        ts = ts - offset
    
    return ts

def load_metrics(path = None):
    if path is None:
        path = './all_metrics.txt'
    p = Path(path)
    if not p.exists():
        print(f"ERROR: Path for metrics {p.resolve()} does not exists.")
        sys.exit(1)
    try:
        metrics_order = {}
        with open(p, 'r') as f:
            order = 0
            for line in f:
                parts = line.split(' - ')
                metric = parts[2]
                type = parts[3]
                metrics_order[metric] = (order,type)
                order += 1
        return metrics_order
    except:
        print("ERROR: Reading metrics file")
        sys.exit(1)

def safe_cast(val, to_type):
    if to_type in ['INT' ,'WORK_DUR']:
        try:
            return int(val)
        except (ValueError, TypeError):
            print(f"WARNING: exception casting value {str(val)} to type {to_type}")
            return None
    elif to_type in ['FLOAT', 'PERCENT', 'RATING']:
        try:
            return float(val)
        except (ValueError, TypeError):
            print(f"WARNING: exception casting value {str(val)} to type {to_type}")
            return None
    elif to_type == 'BOOL':
        try:
            return bool(val)
        except (ValueError, TypeError):
            print(f"WARNING: exception casting value {str(val)} to type {to_type}")
            return None
    elif type == 'MILLISEC':
        try:
            return datetime.fromtimestamp(int(val)/1000)
        except (ValueError, TypeError):
            print(f"WARNING: exception casting value {str(val)} to type {to_type}")
            return None
    else:
        try:
            return str(val)
        except (ValueError, TypeError):
            print(f"ERROR: error casting to type {to_type}")
            return None

def extract_measures_value(measures, metrics_order_type, columns, data):

    for measure in measures:
        metric = measure['metric']
        type = metrics_order_type[metric][1]

        columns.append(metric)
        history = measure['history']
        values = list((map(lambda x: None if 'value' not in x else safe_cast(x['value'],type), history)))
        values.reverse()
        data[metric] = values
    
    return columns, data

def process_project(project, load, format, output_path, metrics_path = None ):

    project_key = project['key']
    project_analyses = query_server('analyses', 1, project_key = project_key)
    print(f"{project_key} - {len(project_analyses)} analyses")

    if len(project_analyses) == 0:
        return

    revision_list = []
    date_list = []
    version_list = []
    for analysis in project_analyses:
        revision = None if 'revision' not in analysis else analysis['revision']
        revision_list.append(revision)
        date = None if 'date' not in analysis else process_datetime(analysis['date'])
        date_list.append(date)
        version = None if 'projectVersion' not in analysis else analysis['projectVersion']
        version_list.append(version)
    
    metrics_order_type = load_metrics(metrics_path)
    metrics = list(metrics_order_type.keys())

    measures = []
    for i in range(0,len(metrics), 15):
        #Get measures
        measures = measures + query_server('measures',1,project_key, metrics[i:i+15])
    
    measures.sort(key = lambda x: metrics_order_type[x['metric']][0])

    data = OrderedDict()
    data['project'] = [project_key] * len(project_analyses)
    data['version'] = version_list
    data['date'] = date_list
    data['revision'] = revision_list
    columns = ['project', 'version', 'date', 'revision']

    columns_with_metrics, data_with_measures = extract_measures_value(measures, metrics_order_type, columns, data)

    #Create DF
    df = pd.DataFrame(data_with_measures, columns= columns_with_metrics)

    output_path_format = output_path.joinpath(format)
    output_path_format.mkdir(parents=True, exist_ok=True)
    file_path = output_path_format.joinpath(f"{project_key}.{format}")

    if format == "csv":
        df.to_csv(path_or_buf= file_path, index=False, header=True)
    elif format == "parquet":
        df.to_parquet()


def write_metrics_file(metric_list):
    metric_list.sort(key = lambda x: ('None' if 'domain' not in x else x['domain'], int(x['id'])))

    with open('./all_metrics.txt', 'w') as f:
        for metric in metric_list:
            f.write("{} - {} - {} - {} - {}\n".format(
                'No ID' if 'id' not in metric else metric['id'],
                'No Domain' if 'domain' not in metric else metric['domain'],
                'No Key' if 'key' not in metric else metric['key'],
                'No Type' if 'type' not in metric else metric['type'],
                'No Description' if 'description' not in metric else metric['description']
                ))

if __name__ == "__main__":

    ap = argparse.ArgumentParser()

    ap.add_argument("-f","--format", choices=['csv', 'parquet'], default='csv', 
        help="Output file format. Can either be csv or parquet")

    ap.add_argument("-o","--output-path", default='./sonar_data' , help="Path to output file directory.")
    ap.add_argument("-l","--load", choices = ['first', 'incremental'], default='incremental' , help="Path to output file directory.")

    args = vars(ap.parse_args())
    format = args['format']
    output_path = args['output_path']
    load = args['load']

    # Write all metrics to a file
    # write_metrics_file(query_server(type='metrics'))

    project_list = query_server(type='projects')
    project_list.sort(key = lambda x: x['key'])

    print(f"Total: {len(project_list)} projects")
    i = 0
    for project in project_list:
        print(f"\t{i}: ", end = "")
        process_project(project, load, format, output_path)
        i += 1