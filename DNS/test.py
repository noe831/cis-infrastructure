"""
Execute self-tests for DNS containers. 

"""

import glob
import yaml 
import pydig 
import unittest
import ipaddress

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

class TestDNS(unittest.TestCase):

	real_resolver = pydig.Resolver(
		nameservers=['8.8.8.8', '8.8.4.4',],
	)
	ext_resolver = pydig.Resolver(
		nameservers=['external',],
	)
	int_resolver = pydig.Resolver(
		nameservers=['internal',],
	)

	def select(self, what):
		for host in inv['hosts']:
			for record in inv['hosts'][host]:
				try:
					if what(record):
						yield host, record 
				except:
					pass 

	def test_cname_records(self):
		def is_cname(record):
			try:
				ipaddress.ip_address(record)
				return False
			except:
				pass
			return True 

		for host, cname in self.select(is_cname):
			got = self.real_resolver.query(cname, "A")
			self.assertGreater(len(got), 0, f"Cannot resolve A for {cname} (required by {host}).")

	def test_a_records(self):
		for host, addr in self.select(lambda x: ipaddress.ip_address(x) and True):
			addr = ipaddress.ip_address(addr)
			if addr.version == 4:
				query_type = 'A'
				rev_record = '.'.join(reversed(str(addr).split('.'))) + '.in-addr.arpa'
			else:
				query_type = 'AAAA'
				rev_record = '.'.join(reversed(str(addr.exploded).replace(':',''))) + '.ip6.arpa'

			if addr.is_private:
				# Test internal resolution
				got = self.int_resolver.query(f'{host}.cis.cabrillo.edu', query_type)
				self.assertGreater(len(got), 0, f"Failed to resolve {host}")	
				self.assertEqual(str(addr), got[0], "Resolution mismatch {addr} != {got[0]}")

				# External resolution should fail or give an external address 
				got = self.ext_resolver.query(f'{host}.cis.cabrillo.edu', query_type)
				if len(got) > 0:
					self.assertNotEqual(str(addr), got[0], "Resolution mismatch {addr} == {got[0]}")

				# Test the reverse record 
				got = self.int_resolver.query(rev_record, 'PTR')
				self.assertGreater(len(got), 0, f"Failed to reverse {host} {rev_record}")	
				self.assertEqual(host + '.cis.cabrillo.edu.', got[0], "Reverse resolution mismatch {host} != {got[0]}")

			else:
				# Test external resolution
				got = self.ext_resolver.query(f'{host}.cis.cabrillo.edu', query_type)
				self.assertGreater(len(got), 0, f"Failed to resolve {host} {addr}")	
				self.assertEqual(str(addr), got[0], "Resolution mismatch {host} != {got[0]}")

				# Test the reverse record 
				# Have to mangle this record to match the funky CNAME used in reversing this subnet. 
				rev_record = rev_record.replace('187.', '224-27.187.')
				got = self.ext_resolver.query(rev_record, 'PTR')
				self.assertGreater(len(got), 0, f"Failed to reverse {host} {rev_record}")	
				self.assertTrue(host + ".cis.cabrillo.edu." in got, f"Reverse resolution mismatch {host} not in {got}")

	def test_internal_domains(self):
		for zone in ["cis.cabrillo.edu", 
				"5.30.172.in-addr.arpa",
				"0.168.192.in-addr.arpa",
				"5.2.4.f.f.0.8.0.0.8.3.f.7.0.6.2.ip6.arpa",
			]:
			got = self.int_resolver.query(zone, 'SOA')
			self.assertEqual(len(got), 1, f"Failed to resolve zone {zone}")	

			# Test nameservers
			got = self.int_resolver.query(zone, 'NS')
			self.assertEqual(len(got), 2, f"Didn't get two nameservers in zone {zone}")	
			got.sort()
			self.assertEqual(got[0], 'ns1.cis.cabrillo.edu.', f"Wrong nameserver in zone {zone}: {got[0]}")
			self.assertEqual(got[1], 'ns2.cis.cabrillo.edu.', f"Wrong nameserver in zone {zone}: {got[1]}")


	def test_external_domains(self):
		for zone in ["cis.cabrillo.edu", 
				"224-27.187.62.207.in-addr.arpa",
				"5.2.4.f.f.0.8.0.0.8.3.f.7.0.6.2.ip6.arpa",
			]:
			got = self.ext_resolver.query(zone, 'SOA')
			self.assertGreater(len(got), 0, f"Failed to resolve zone {zone}")	

			# Test nameservers
			got = self.ext_resolver.query(zone, 'NS')
			self.assertEqual(len(got), 2, f"Didn't get two nameservers in zone {zone}: {got}")	
			got.sort()
			self.assertEqual(got[0], 'ns1.cis.cabrillo.edu.', f"Wrong nameserver in zone {zone}: {got[0]}")
			self.assertEqual(got[1], 'ns2.cis.cabrillo.edu.', f"Wrong nameserver in zone {zone}: {got[1]}")

	def test_internal_forwards(self):
		got = self.int_resolver.query('www.google.com', 'A')
		self.assertGreater(len(got), 0, f"Internal zone did not forward a query.")	

	def test_external_not_forwards(self):
		got = self.ext_resolver.query('www.google.com', 'A')
		self.assertEqual(len(got), 0, f"External zone DID forward a query.")	

	# FIXME: No support for CAA in pydig.
	#def test_external_caa(self):
	#	got = self.ext_resolver.query('cis.cabrillo.edu', 'CAA')
	#	self.assertGreater(len(got), 0, f"External did not respond to a CAA.")	

if __name__ == '__main__':
	unittest.main(verbosity=3)