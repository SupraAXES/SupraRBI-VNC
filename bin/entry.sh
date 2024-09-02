#!/bin/bash

echo 'vnc-rbi 0.0.1'

check_cert() {
  if [ ! -d /supra/cert ]; then
    mkdir -p /supra/cert
  fi

  if [ ! -f /supra/cert/server.crt ]; then
    echo "Certificate not found, generating a new one"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /supra/cert/server.key -out /supra/cert/server.crt -subj "/C=US/ST=Delaware/O=SupraAXES/CN=www.supraaxes.com"
  fi
}

check_cert

/supra/bin/vncd.py &

wait -n
