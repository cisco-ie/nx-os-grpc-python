# nx-os-grpc-python

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

NX-OS gRPC Python connectivity library. Proto files sourced from [documentation](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_010111.html#id_41517).

## Development
Requires Python and recommends `pipenv`. Manual usage of `pip`/`virtualenv` is not covered. Uses `black` for code formatting and `pylint` for code linting.

### Get Source

```bash
git clone https://github.com/cisco-grpc-connection-libs/nx-os-grpc-python.git
cd nx-os-grpc-python
# If pipenv not installed, install!
pip install --user pipenv
# Now use pipenv, source from lockfile
pipenv --three install --dev --ignore-pipfile
# If that doesn't work..
pipenv --three install --dev
# If you encounter an issue locking dependencies...
./lock_deps.sh
# Enter virtual environment
pipenv shell
# Do your thing.
exit
```

### Clean Code
We use [`black`](https://github.com/ambv/black) for code formatting and `pylint` for code linting. `clean_code.sh` will run `black` against all of the code under `nxos_grpc/` except for `protoc` compiled protobufs, and run `pylint` against Python files directly under `nxos_grpc/`. They don't totally agree, and we aren't using perfect naming conventions in some cases, so we're not looking for perfection here.

```bash
./clean_code.sh
```

TODO: Add pre-commit hook to automatically run black if any Python files are being committed.

### Recompile Protobufs
If a new `nxos_grpc.proto` definition is released, use `update_protos.sh` to recompile. If breaking changes are introduced the wrapper library must be updated.

```bash
./update_protos.sh
```


## TLS Usage
In order to use a secure channel you must acquire the necessary gRPC PEM files, `grpc.pem`. This PEM file is found with your downloaded gRPC Agent RPM. You must then specify the file path or the content of this PEM file when initializing the Client class.

TODO: Where to acquire gRPC Agent RPM?  
