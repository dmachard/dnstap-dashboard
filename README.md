# Dnstop - real-time metrics for dns server

## Table of contents
* [Overview](#overview)
* [Installation](#installation)

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

After installation, you can execute the `dnstop` to start-it.
Prefer to install dnstop on the same machine of your dnstap receiver.

![dnstop](/dnstop.png)