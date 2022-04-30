import argparse
from time import sleep
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS, PointSettings
import datetime
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Request logs from machines to be monitored")
    parser.add_argument(
        "--ip_addresses",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--tokens",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--orgs",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--buckets",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--ports",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--control_ip_address",
        type=str,
    )
    parser.add_argument(
        "--control_token",
        type=str,
    )
    parser.add_argument(
        "--control_org",
        type=str,
    )
    parser.add_argument(
        "--control_bucket",
        type=str,
    )
    parser.add_argument(
        "--control_port",
        type=str,
    )
    args = parser.parse_args()
    return args

def main():
    args=parse_args()
    control_client=influxdb_client.InfluxDBClient(
        url="http://"+args.control_ip_address+":"+args.control_port,
        token=args.control_token,
        org=args.control_org,
    )
    write_api=control_client.write_api(write_options=SYNCHRONOUS)
    clients=[]
    for i in range(len(args.ip_addresses)):
        clients.append(
            influxdb_client.InfluxDBClient(
                url="http://"+args.ip_addresses[i]+":"+args.ports[i],
                token=args.tokens[i],
                org=args.orgs[i]
            )
        )
    query_apis=[]
    for i in range(len(args.ip_addresses)):
        query_apis.append(clients[i].query_api())
    
    last_stop_times=[datetime.datetime.now().astimezone() for k in range(len(args.ip_addresses))]
    for i in range(1000):
        sleep(1)
        queries=[]
        for j in range(len(args.ip_addresses)):
            s=last_stop_times[j].isoformat()
            queries.append(
                ' from(bucket: "'+args.buckets[j]+'")\
                |> range(start: '+s+')\
                |> filter(fn:(r) => r._measurement == "cpu" or r._measurement=="mem" or r._measurement=="diskio" or r._measurement=="net" or r._measurement=="postgresql" or r._measurement=="processes")\
                |> filter(fn: (r) => r._field== "usage_system" or r._field== "read_bytes" or r._field== "write_bytes" or r._field== "active" or r._field=="available" or r._field== "buffered" or r._field=="cached" or r._field=="dirty" or r._field=="free" or r._field=="inactive" or r._field=="shared" or r._field=="swap_free" or r._field=="swap_total" or r._field=="used_percent" or r._field== "bytes_received" or r._field== "bytes_sent" or r._field== "tup_deleted" or r._field== "tup_fetched" or r._field== "tup_inserted" or r._field== "tup_returned" or r._field== "tup_updated" or r._field== "total_threads")'#\
                #|> filter(fn:(r) => r._field == "tup_returned" ) '
            )
        results=[]
        for j in range(len(args.ip_addresses)):
            res=query_apis[j].query(org=args.orgs[j], query=queries[j])
            for table in res:
                last_stop_times[j]=max([row.values["_time"]+datetime.timedelta(seconds=1) for row in table])
                break
            results.append(res)
        for j, result in enumerate(results):
            for table in result:
                data=pd.DataFrame([row.values for row in table])
                data=data.set_index("_time")
                data["_value"]=data["_value"].astype("float")
                data.rename(columns={"_value": data["_field"][0]}, inplace=True)
                data.drop(["_field", "_measurement", "result", "table", "_start", "_stop"], inplace=True, axis=1)
                # data["ip"]=args.ip_addresses[j]
                write_api.write(bucket=args.control_bucket, record=data, data_frame_measurement_name=args.ip_addresses[j])

if __name__=="__main__":
    main()