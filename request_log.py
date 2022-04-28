import argparse
from ipaddress import ip_address
from time import sleep
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

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
    args = parser.parse_args()
    return args

def main():
    args=parse_args()
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
    queries=[]
    for i in range(len(args.ip_addresses)):
        queries.append(
            ' from(bucket: "'+args.buckets[i]+'")\
            |> range(start: -10m)\
            |> filter(fn:(r) => r._measurement == "mem")'#\
            #|> filter(fn: (r) => r.db == "dbproject")\
            #|> filter(fn:(r) => r._field == "tup_returned" ) '
        )
    fhands=[]
    for i in range(len(args.ip_addresses)):
        fhands.append(open(args.ip_addresses[i]+".txt", "w"))
    for i in range(100):
        sleep(1)
        results=[]
        for i in range(len(args.ip_addresses)):
            results.append(
                query_apis[i].query(org=args.orgs[i], query=queries[i])
            )
        for result in results:
            for table in result:
                fhands[i].write(str(table))
                fhands[i].write("\n")
                for row in table:
                    fhands[i].write(str(row.values))
                    fhands[i].write("\n")
    for i in range(len(args.ip_addresses)):
        fhands[i].close()

if __name__=="__main__":
    main()
