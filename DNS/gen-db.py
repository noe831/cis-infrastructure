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
import argparse


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


def subdomain(domains):
	"""Make glue records.""" 
	rval = ""
	for d in domains:
		domain = dict(d)
		name = domain['name']
		del domain['name']
		for ns in domain:
			rval += f"""{name}.cis.cabrillo.edu. IN NS {ns}.{name}.cis.cabrillo.edu.\n"""
			for addr in domain[ns]:
				ip = ipaddress.ip_address(addr)
				if ip.version == 4:
					rval += f"""{ns}.{name}.cis.cabrillo.edu. IN A {ip}\n"""
				else:
					rval += f"""{ns}.{name}.cis.cabrillo.edu. IN AAAA {ip}\n"""
	
	return rval 


def main():
	parser = argparse.ArgumentParser(description='Generate zone files from templates')
	parser.add_argument('--dry-run', action='store_true', help='Print files instead of writing them.')
	args = parser.parse_args()

	inv = {}
	for source in sorted(glob.glob('source/*.yaml')):
		print(f"Loading {source}")
		with open(source) as f:
			y = yaml.load(f, Loader=yaml.Loader)
			for k in list(inv.keys()):
				if k in y:
					inv[k].update(y[k])
			for k in y:
				if k not in inv:
					inv[k] = y[k]

	now = datetime.datetime.now()
	inv['soa'] = inv['soa'].format(serial=f'{now:%Y%m%d}{inv["serial"]}')

	if not args.dry_run:
		os.mkdir('build')

	for templfile in glob.glob('templates/db.*'):
		print(f"Building template {templfile}")
		with open(templfile) as f:
			template = jinja2.Template(f.read())	
			output = "build/" + pathlib.Path(templfile).name
			rendered = template.render(inv, 
					reverse=reverse,
					fwd=fwd,
					subdomain=subdomain,
				)
			print(rendered)
			if not args.dry_run:
				with open(output, 'w') as of:
					of.write(rendered)

if __name__ == '__main__':
	main()
