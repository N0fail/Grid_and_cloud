from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption
import networkx as nx
import matplotlib.pyplot as plt
import paramiko
import time
import json
import threading

SUBSCRIPTION_ID = ''
CLIENT_ID = ""
TENANT = ""
OBJECT_ID = ""
SECRET = ""

def send_task(host, n, m, seed, customer):
    host = host
    user = 'azureuser'
    port = 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, port=port)  # connecting
    stdin, stdout, stderr = client.exec_command('sudo /usr/bin/python3 /home/azureuser/www/Grid_solver.py {} {} {} {}'.format(n, m, seed, customer))  # sending task and recieving results
    print(stderr.read())
    #stdin.read()
    graph, colors = str(stdout.read()).split('\\n')[0:2]  # parsing results
    stdin.flush()
    graph = json.loads(graph[2:])
    colors = json.loads(colors)
    print(colors)
    G = nx.jit_graph(graph)
    nodes = list(G.nodes)
    colors = list(map(lambda x: colors[nodes[x]], range(len(colors))))  # setting colors in right order
    nx.draw(G, node_color=colors, pos=nx.drawing.layout.kamada_kawai_layout(G), with_labels=True)
    plt.savefig("static/{}_{}_{}.png".format(n, m, seed))
    client.close()

class VM:
    def __init__(self, name, group, ip):
        self.name = name
        self.group = group
        self.ip = ip
        self.running = False  # indicates if VM is running (not stopped)
        self.task_info = None  # task class object (from __init__.py)
        self.task = threading.Thread() # current task running on VM, if task.isAlive()==false then task finished
        self.credentials = ServicePrincipalCredentials(client_id = CLIENT_ID, secret = SECRET, tenant = TENANT) # permission to manupilate VMs
        self.compute_client = ComputeManagementClient(self.credentials, SUBSCRIPTION_ID)
    
    def run_task(self, task):
        self.task_info = task
        self.task = threading.Thread(target=send_task,  args=(self.ip, task.n, task.m, task.seed, task.user))
        self.task.start()
        
    def start(self):
        self.compute_client.virtual_machines.start(self.group, self.name)
        self.running = True
        
    def stop(self):
        self.compute_client.virtual_machines.power_off(self.group, self.name)
        self.running = False
