from pprint import pprint

import yaml
from jinja2 import DictLoader, Environment, FileSystemLoader
from netmiko import (ConnectHandler, NetmikoAuthenticationException,
                     NetmikoTimeoutException)
from rich import print as rprint
from tabulate import tabulate


def save_config(device):
    ip = device.get("host")
    try:
        rprint(f"[yellow]Connecting to {ip}>>>>>")
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            output = ssh.save_config()
            if "[OK]" in output:
                rprint(f"[blue]Configuration on {ip} saved successfully!")
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)
def send_config(device, commands):
    ip = device.get("host")
    result = ""
    try:
        rprint(f"[yellow]Connecting to {ip}>>>>>")
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            if isinstance(commands, str):
                commands = list(commands.split("\n"))
            output = ssh.send_config_set(commands, read_timeout=20)
            if "Invalid input detected at" in output:
                raise ValueError(f"Failed execute config {output}")
            result += output
        return (ip, result)
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)

def generate_loopback(number_of_int):
    number_of_int +=1
    all_int = []
    for i in range(1, number_of_int):
        intf = f"interface Loopback {i}\nip address 22.0.{i}.254 255.255.255.0\nrouter bgp 100\nnetwork 22.0.{i}.0 mask 255.255.255.0"
        intf.strip()
        li = list(intf.split("\n"))
        all_int.append(li)
    return all_int

ospf_core_file = "config_ospf_core.j2"
bgp_core_file = "config_bgp_core.j2"
with open(ospf_core_file, "r") as _file:
    ospf_core_template = _file.read()
with open(bgp_core_file, "r") as _file:
    bgp_core_template = _file.read()

def main():
    with open("device_condition.yml", "r") as f:
        devices_data:dict = yaml.safe_load(f)
    with open("devices.yml", "r") as f:
        devices_con_params:dict = yaml.safe_load(f)
    
    env = Environment(loader=DictLoader({"ospf_core": ospf_core_template, "bgp_core": bgp_core_template}))
    for device, param in devices_con_params.items():
        try:
            device_param = devices_data.get(device)
        except KeyError:
            print(f"Connection for {device} not found!")
        device_role = param[0].get("role")
        #Create config from template
        #save_config(*param)
        device_config_data = env.get_template(device_role).render(device_param)
        print(device_config_data)
        del param[0]["role"]
        rprint(f"[red]{device_param}")
        #device_ip, output = send_config(*param, device_config_data)
        #rprint(f"[cyan]{device_ip}")
        #rprint(f"[green]{output}")
if __name__ == "__main__":
    device = {
        "device_type": "cisco_ios",
        "host": "192.168.100.31",
        "username": "cisco",
        "password": "cisco",
        "secret": "cisco",
    }
    #columns = ['command', 'output']
    #config_data = generate_loopback(100)
    #conf_res = send_config(device, config_data)
    #print(conf_res)
    main()

