# Integration with Apache Guacamole

SupraRBI-VNC can be integrated with Apache Guacamole for secure access to a target URL, with [projector-chrome](https://github.com/supraaxes/projector-chrome) or [projector-supra-web](https://github.com/supraaxes/projector-supra-web).

No modification to Apache Guacamole client *guacmaole/guacamole* or server *guacamole/guacd* is required, and all sessions to the target URL can be managed just as any other VNC sessions.

![Guacamole](/resources/guacamole.png "Guacamole")

### Resource Configuration Examples

The configuration on Apache Guacamole is straight forward.

1. Standalone SupraRBI-VNC server, dynamic session to https://github.com

    > *SupraRBI-VNC server is at 192.168.0.178:5998*. <br>
    > 
    > Name: *rbi-github*<br>
    > Protocol: *VNC*<br>
    > Hostname: *192.168.0.178*<br>
    > Port: *5998*<br>
    > Username: *https://github.com*<br>
    > Password: *{}*<br>

2. Integrated installation with containers, dynamic session to https://www.google.com, with audio on. 
    
    > *NOTE: Please ensure the guacd container is in the same network as the SupraRBI-VNC server*. <br>
    >
    > Name: *rbi-google*<br>
    > Protocol: *VNC*<br>
    > Hostname: *rbi-vnc*<br>
    > Port: *5900*<br>
    > Username: *https://www.google.com*<br>
    > Password: *{"id":{"type":"norm","name":"1234"}}*<br>
    > Enable audio: *checked*<br>
    > Audio server name: *rbi-norm-1234*<br>

3. Integrated installation with containers, dynamic session to https://github.com, using licensed [projector-supra-web](/resources/projector_supra.md) with auto login. 
    
    > *NOTE: 
    >   1. The guacd container is in the same network as the SupraRBI-VNC server*. <br>
    >   2. The github autofill setting file on host is /opt/supra/rbi/conf/autofill/github.json
    >   3. The license file on host is /opt/supra/rbi/conf/license.json
    >
    > Name: *rbi-google*<br>
    > Protocol: *VNC*<br>
    > Hostname: *rbi-vnc*<br>
    > Port: *5900*<br>
    > Username: *https://github.com*<br>
    > Password: *{"mounts":["/opt/supra/rbi/conf/autofill/github.json:/opt/supra/conf/autofill.json:ro","/opt/supra/rbi/conf/license.json:/opt/supra/conf/license.jsob:ro"],"instance-settings":{"autofill-username": "myname", "autofill-password": "mypassword"}}*<br>

### Auto resize to VNC sessions
The issue is expected be fixed in 1.6.0, please check the latest Apache Guacamole release.

https://issues.apache.org/jira/browse/GUACAMOLE-1196<br>
https://general.sautx.com/github.com/apache/guacamole-server/pull/469