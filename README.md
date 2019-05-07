
# Surface Discovery

Automate the discovery of a company's attack surface. This script will check against Owler, Clearbit
WHOIS, TCPIP Utils, and the BGP Toolkit in order to find a company's acquisitions, domains, hosts,
ASNs, People of Contact, and network ranges.

## Installation

```
virtualenv Surface-Discovery-Virt
. bin/activate
git clone https://wwwin-gitlab-sjc.cisco.com/mlombana/Surface-Discovery.git
pip install -Ur requirements.txt
```

### Configuration

There are things to configure before acquisitions.py can be run. They are:

**Setup:**
* surfacediscovery.local.yml

```shell
cp conf/surfacediscovery.yml conf/surfacediscovery.local.yml
vim conf/surfacediscovery.local.yml
```
#### [surfacediscovery.local.yml](./surface-discovery/conf/surfacediscovery.yml)

This file holds global global configuration values.

## Usage

You can run surface_discovery in interactive mode with the following command:

```
./surface_discovery.py
```

To run it in non-interactive mode, use flags to specify each argument. Use the `-h` flag for a
complete list of options. for example, to run against a company:

```
./surface_discovery.py -c <company_name>
```


## Contributing

Fork the repo, and create a pull request!
