# nx-os-grpc-python
NX-OS gRPC Python connectivity library. Proto files sourced from [documentation](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_010111.html#id_41517).

## Development
Requires Python and `pipenv`.

```bash
git clone https://github.com/cisco-grpc-connection-libs/nx-os-grpc-python.git
cd nx-os-grpc-python
# If Pipenv not installed...
pip install --user pipenv
pipenv --three install --dev
pipenv shell
# Do your thing.
exit
```

## TLS Usage
TODO: Where to acquire gRPC Agent RPM?
In order to use a secure channel you must acquire the necessary gRPC PEM files, `grpc.pem`. This PEM file is found with your downloaded gRPC Agent RPM. You must then specify the file path or the content of this PEM file when initializing the Client class.

### Recompile Protobufs
If a new `nxos_grpc.proto` definition is released, use `update_protos.sh` to recompile. If breaking changes are introduced the wrapper library must be updated.

```bash
pipenv shell
./update_protos.sh
exit
```
