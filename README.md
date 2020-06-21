# cis-infrastructure

![DNS](https://github.com/mike-matera/cis-infrastructure/workflows/DNS/badge.svg?branch=master)

Infrastructure for the CIS Datacenter

## Contents 

 - `/ansible` - Playbooks to deploy servers
 - `/docker` - Container recipes 
 - `/kubernetes` - Deployment resources 

## Infrastructure 

This repository is used to deploy two key pieces of infrastrucure:

| Host(s) | Addresses | Purpose | 
| --- | --- | --- | 
| opus.cis.cabrillo.edu | 207.62.187.228<br>172.30.5.228/24<br>2607:F380:80F:F425::228/64 | The login server for administrative and student use. This server provides access to infrastructure and other systems. 
| ns1.cis.cabrillo.edu<br>ns2.cis.cabrillo.edu | 207.62.187.252<br>2607:f380:80f:f425::252<br>207.62.187.253<br>2607:f380:80f:f425::253<br> | DNS services. 
 

