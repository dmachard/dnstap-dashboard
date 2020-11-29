# ``dnstop`` - real-time metrics for dns server

**dnstop** can display metrics of your dns server in real-time.

    If you want to use-it, you must also deploy [dnstap_receiver](https://github.com/dmachard/dnstap-receiver) project and activate ``dnstap`` feature on your dns server.

## Table of contents
* [Installation](#installation)
    * [PyPI](#pypi)
    
## Installation

### PyPI

Install the dnstop command with the pip command.

```python
pip install dnstop
```

After installation, you can execute the `dnstop` to start-it.
Prefer to install dnstop on the same machine of your dnstap receiver.

![dnstop](/dnstop.png)