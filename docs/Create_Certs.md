# Creating Certs

Bumper requires specially crafted certificates to work properly.  In the spirit of security, Bumper will not ship with default certificates.  Users will need to generate and provide their own certificates.  

Certificates should be placed in the `{bumper_home}/certs` directory.  If certificates are located elsewhere [environment variables](Env_Var.md) can be set that point to their location.

Users can generate certificates in the following ways:

| Method                                            | Description                                                                                                         |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [OpenSSL](#manually-create-certs-with-openssl)    | Users can manually create the same certificates as Create_Certs by utilizing OpenSSL.                               |
| [Custom CA/Self](#using-a-custom-caself)          | If a user has their own CA the certificates can be generated there and used within Bumper.                          |

**Certificate Requirements:**

* A CA Cert must be provided that can be imported into devices (phones, browsers, etc).
* Server certificate should include [SANs (Subject Alternate Names)](#subject-alternative-name) for all of the *.ecovacs, etc domains.

## Manually create certs with OpenSSL

The easiest way to create the required certs is at https://certificatetools.com/.  In fact the below OpenSSL commands come straight from that site, post creation via the GUI.

### Create a Root CA

1. Create csrconfig_ca.txt for use in later commands

***csrconfig_ca.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper CA
organizationName = Bumper
[ req_ext ]
keyUsage=critical,keyCertSign,cRLSign
basicConstraints=critical,CA:true,pathlen:1
````

1. Create certconfig_ca.txt for use in later commands

***certconfig_ca.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper CA
organizationName = Bumper
[ req_ext ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
keyUsage=critical,keyCertSign,cRLSign
basicConstraints=critical,CA:true,pathlen:1
````

1. Generate the RSA private key 
    
    `openssl genrsa -out ca.key 4096`

1. Create the CSR
    
    `openssl req -new -nodes -key ca.key -config csrconfig_ca.txt -out ca.csr`

1. Self-sign your CSR
    
    `openssl req -x509 -nodes -in ca.csr -days 1095 -key ca.key -config certconfig_ca.txt -extensions req_ext -out ca.crt`

### Create the Server Certificate

1. Create csrconfig_bumper.txt for use in later commands

***csrconfig_bumper.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper Server
organizationName = Bumper
[ req_ext ]
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth,clientAuth
basicConstraints=critical,CA:false
subjectAltName = @alt_names
[ alt_names ]
DNS.0 = ecovacs.com
DNS.1 = *.ecovacs.com
DNS.2 = ecouser.net
DNS.3 = *.ecouser.net
DNS.4 = ecovacs.net
DNS.5 = *.ecovacs.net
DNS.6 = *.ww.ecouser.net
DNS.7 = *.dc-eu.ww.ecouser.net
DNS.8 = *.dc.ww.ecouser.net
DNS.9 = *.area.ww.ecouser.net
````

1. Create certconfig_bumper.txt for use in later commands

***certconfig_bumper.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper Server
organizationName = Bumper
[ req_ext ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth,clientAuth
basicConstraints=critical,CA:false
subjectAltName = @alt_names
[ alt_names ]
DNS.0 = ecovacs.com
DNS.1 = *.ecovacs.com
DNS.2 = ecouser.net
DNS.3 = *.ecouser.net
DNS.4 = ecovacs.net
DNS.5 = *.ecovacs.net
DNS.6 = *.ww.ecouser.net
DNS.7 = *.dc-eu.ww.ecouser.net
DNS.8 = *.dc.ww.ecouser.net
DNS.9 = *.area.ww.ecouser.net
````

1. Generate the RSA private key
    
    `openssl genrsa -out bumper.key 4096`

1. Create the CSR

    `openssl req -new -nodes -key bumper.key -config csrconfig_bumper.txt -out bumper.csr`

1. Sign your CSR with a root CA cert
    
    `openssl x509 -req -in bumper.csr -days 365 -CA ca.crt -CAkey ca.key -extfile certconfig_bumper.txt -extensions req_ext -CAcreateserial -out bumper.crt`

## Using a Custom CA/Self

This should work siimilar to the OpenSSL method.  Ensure the server certificate has the proper SANs (see above) in place.