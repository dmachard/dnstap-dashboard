# Dnstop - real-time metrics for dns server

## Table of contents
* [Overview](#overview)
* [Installation](#installation)
* [Configuration](#configuration)

## Overview

**dnstop** can display metrics of your dns server in real-time.

> If you want to use-it, your server must support the ``dnstap`` feature and also deploy the following [dnstap receiver](https://github.com/dmachard/dnstap-receiver)
                       
      [             ] ---- stream 1 ------------|
      [     DNS     ]                           |
      [             ]                           v
      [   servers   ] ---- stream 2 ----> [ dnstap receiver ] <-- [ dnstop ]
      [             ]                         

## Installation

Install the dnstop command with the pip command.

```python
pip install dnstop
```

After installation, you can execute the binary `./dnstop` to start-it.
Prefer to install dnstop on the same machine of your dnstap receiver.

![dnstop](/dnstop.png)

## Configuration

See [default config file](/dnstop/dnstop.conf) example.

You can provide your own configuration, to do that create the file following  `/etc/dnstop/dnstop.conf`.

If your dnstop command is not on the same machine of your dnstap receiver, you need to configure 
the api address and provide the good api-key, for example:

```yaml
dnstap-receiver:
  api-ip: 127.0.0.1
  api-port: 8080
  api-key: changeme
```