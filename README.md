# Dnstap dashboard - real-time metrics for dns server

## Table of contents
* [Overview](#overview)
* [Installation](#installation)
* [Configuration](#configuration)

## Overview

**dnstap_dashboard** can display metrics of your dns server in real-time, a top-like command.

> If you want to use-it, your server must support the ``dnstap`` feature and also deploy the following [dnstap receiver](https://github.com/dmachard/dnstap-receiver)
                       
      [             ] ---- stream 1 ------------|
      [     DNS     ]                           |
      [             ]                           v
      [   servers   ] ---- stream 2 ----> [ dnstap receiver ] <-- [ dnstap dashboard ]
      [             ]                         

## Installation

Install the dnstap_dashboard command with the pip command.

```python
pip install dnstap_dashboard
```

After installation, you can execute the binary `./dnstap_dashboard` to start-it.
Prefer to install the dnstap_dashboard binary on the same machine of your dnstap receiver.

![dnstap_dashboard](/screenshot.png)

## Configuration

See [default config file](/dnstap_dashboard/dashboard.conf) example.

You can provide your own configuration, to do that create the following file `/etc/dnstap_dashboard/dashboard.conf`.

If your dnstap_dashboard command is not on the same machine of your dnstap receiver, you need to configure the api address and provide the good api-key, for example:

```yaml
dnstap-receiver:
  api-ip: 127.0.0.1
  api-port: 8080
  api-key: changeme
```