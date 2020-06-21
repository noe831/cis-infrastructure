"""
Generate BIND9 db files from yaml. 
"""

import yaml 
import jinja2 
import datetime 
import ipaddress
import glob 
import pathlib 
import os 


def reverse(hosts, network):
	rval = ''
	rzone = ipaddress.ip_network(network)
	for host in hosts:
		for addr in hosts[host]:
			try:
				ip = ipaddress.ip_address(addr)
				if ip in rzone:
					if ip.version == 4:
						hostaddr = str(ip).split('.')[3]
					else:
						hostaddr = '.'.join(reversed(ip.exploded.replace(':', '')[16:]))
					rval += f"{hostaddr} IN PTR {host}.cis.cabrillo.edu.\n"	
			except:
				"""not an IP address""" 

	return(rval)


def fwd(hosts, role):
	rval = ""
	for host in hosts:
		for addr in hosts[host]:
			try:
				ip = ipaddress.ip_address(addr)
				if ((role == 'external' and (ip.version == 6 or not ip.is_private)) or 
					(role == 'internal' and (ip.version == 6 or ip.is_private))):
					if ip.version == 4:
						rval += f"{host} IN A {ip}\n"
					else:
						rval += f"{host} IN AAAA {ip}\n"
			except:
				# This is a name 
				rval += f"{host} IN CNAME {addr}\n"	

	return rval 


def main():
	print("Loading inventory.yaml")
	with open('inventory.yaml') as f:
		inv = yaml.load(f, Loader=yaml.Loader)

	now = datetime.datetime.now()
	inv['soa'] = inv['soa'].format(serial=f'{now:%Y%m%d}{inv["serial"]}')

	os.mkdir('build')

	for templfile in glob.glob('templates/db.*'):
		print(f"Building template {templfile}")
		with open(templfile) as f:
			template = jinja2.Template(f.read())	
			output = "build/" + pathlib.Path(templfile).name
			with open(output, 'w') as of:
				rendered = template.render(inv, 
						reverse=reverse,
						fwd=fwd,
					)
				of.write(rendered)
				print(rendered)

if __name__ == '__main__':
	main()
