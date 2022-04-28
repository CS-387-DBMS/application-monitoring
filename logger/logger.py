from time import sleep, time
from json import dumps
import threading
import psutil
import pyshark

MYIP         = '127.0.0.1'
INTERFACES   = ['lo']
PORT         = 8000

# if you want to monitor specific connections between machines
# eg: CONNS = [('234.22.11.12', 800), ... ]
CONNS        = []

LOG_INTERVAL = 5

# for alerts
CPU_THRESH_IN_PERC = 0.8 * 100
MEM_THRESH_IN_PERC = 0.8 * 100
PACKET_DROP_THRESH = 0.1

hostlog = open('host.log', 'wb', buffering=0)
httplog = open('http.'+str(PORT)+'.log', 'wb', buffering=0)

def check_for_alert(rec):
    if(rec['total_cpu_used'] > CPU_THRESH_IN_PERC):
        x = {'timestamp': rec['timestamp'], 'type':'ALERT', 'alert':'CPU_USAGE', 'value':rec['total_cpu_used']}
        hostlog.write((dumps(x)+'\n').encode())

    if(rec['total_mem_used'] > MEM_THRESH_IN_PERC):  
        x = {'timestamp': rec['timestamp'], 'type':'ALERT', 'alert':'RAM_USAGE', 'value':rec['total_mem_used']}
        hostlog.write((dumps(x)+'\n').encode())
    
    if(rec['total_dropin']/rec['total_packets_recv'] > PACKET_DROP_THRESH or
       rec['total_dropout']/rec['total_packets_sent'] > PACKET_DROP_THRESH):
        val = max(rec['total_dropin']/rec['total_packets_recv'], rec['total_dropout']/rec['total_packets_sent'])
        x = {'timestamp': rec['timestamp'], 'type':'ALERT', 'alert':'PKT_DROP', 'value':val}
        hostlog.write((dumps(x)+'\n').encode())

def log_connection(ip):
    f = open('conn.'+ip[0]+'.'+str(ip[1])+'.log', 'wb', buffering=0)
    while True:
        to_myip, from_myip = 0, 0
        def examine(pkt):
            nonlocal from_myip, to_myip
            if(pkt.tcp.srcport != ip[1] and pkt.tcp.destport != ip[1]):
                return
            if(pkt.ip.src == MYIP):
                from_myip += int(pkt.length)
            if(pkt.ip.dst == MYIP):
                to_myip   += int(pkt.length)
        try:
            capture = pyshark.LiveCapture(interface=INTERFACES, bpf_filter='ip host '+ip[0])
            capture.apply_on_packets(lambda x : examine(x), timeout=LOG_INTERVAL)
        except:
            f.write((dumps({'timestamp': time(), 'bytes_sent': from_myip, 'bytes_recv': to_myip})+'\n').encode())

def log_host():
    p = None
    bytes_read = 0
    bytes_write = 0
    total_bytes_read = 0
    total_bytes_write = 0
    total_bytes_sent = 0
    total_bytes_recv = 0
    total_packets_sent = 0
    total_packets_recv = 0
    total_dropin = 0
    total_dropout = 0
    
    while True:
        to_myip, from_myip = 0, 0
        def examine(pkt):
            nonlocal from_myip, to_myip
            if(pkt.ip.src == MYIP and pkt.tcp.srcport == str(PORT)):
                from_myip += int(pkt.length)
            if(pkt.ip.dst == MYIP and pkt.tcp.dstport == str(PORT)):
                to_myip   += int(pkt.length)
            if(pkt.highest_layer == 'HTTP'):
                httplog.write(
                    (dumps({'timestamp': time(), 'method': pkt.http.request_method, 'url': pkt.http.request_uri})+'\n')
                    .encode()
                )
        try:
            capture = pyshark.LiveCapture(interface=INTERFACES, bpf_filter='tcp port '+str(PORT))
            capture.apply_on_packets(lambda x : examine(x), timeout=LOG_INTERVAL)
        except:
            try:
                vals = p.as_dict(['cpu_percent', 'memory_percent', 'io_counters'])
                tot_disk = psutil.disk_io_counters(nowrap=True)
                tot_net = psutil.net_io_counters(nowrap=True)

                record = { 'timestamp'       : time(),
                           'type'            : 'LOG',
                           'cpu_used'        : vals['cpu_percent'] / psutil.cpu_count(),
                           'total_cpu_used'  : psutil.cpu_percent(), 
                           'mem_used'        : vals['memory_percent'],
                           'total_mem_used'  : psutil.virtual_memory().percent,
                           'total_swap_used' : psutil.swap_memory().percent,
                           'disk_read'       : vals['io_counters'].read_bytes - bytes_read,
                           'disk_write'      : vals['io_counters'].write_bytes - bytes_write,
                           'total_disk_read' : tot_disk.read_bytes - total_bytes_read,
                           'total_disk_write': tot_disk.write_bytes - total_bytes_write,
                           'bytes_sent'      : from_myip,
                           'bytes_recv'      : to_myip,
                           'total_bytes_sent': tot_net.bytes_sent - total_bytes_sent,
                           'total_bytes_recv': tot_net.bytes_recv - total_bytes_recv,
                           'total_packets_sent': tot_net.packets_sent - total_packets_sent,
                           'total_packets_recv': tot_net.packets_recv - total_packets_recv,
                           'total_dropin'    : tot_net.dropin - total_dropin,
                           'total_dropout'   : tot_net.dropout - total_dropout,
                         }

                check_for_alert(record)
                
                hostlog.write((dumps(record)+'\n').encode())

                bytes_read = vals['io_counters'].read_bytes
                bytes_write = vals['io_counters'].write_bytes
                total_bytes_read = tot_disk.read_bytes
                total_bytes_write = tot_disk.write_bytes
                total_bytes_sent = tot_net.bytes_sent
                total_bytes_recv = tot_net.bytes_recv
                total_packets_sent = tot_net.packets_sent
                total_packets_recv = tot_net.packets_recv
                total_dropin = tot_net.dropin
                total_dropout = tot_net.dropout
            except:
                pid = None
                for c in psutil.net_connections():
                    if c.laddr.port == PORT:
                        pid = c.pid
                if not pid:
                    print("service not running on port", PORT)
                    continue
                p = psutil.Process(pid)

if __name__ == "__main__":
    threads = []
    threads.append(threading.Thread(target=log_host))
    for ip in CONNS:
        threads.append(threading.Thread(target=log_connection, args=(ip,)))
  
    for t in threads:
        t.start()
    for t in threads:
        t.join()
