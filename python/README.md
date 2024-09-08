# MiaoSpeedLib

MiaoSpeed Client Library Implementations for Python.

# Usage


from pypi:
```shell
pip install miaospeedlib -U
```

example:
```python
import asyncio
import miaospeedlib as miaolib


slave_cfg = {
    "id": "local",
    "comment": "Local",
    "hidden": False,
    "token": "miaospeed-dev",
    "type": "miaospeed",
    "address": "127.0.0.1:8765",
    "option": {
        "downloadDuration": 8,
        "downloadThreading": 4,
        "pingAverageOver": 20,
        "taskRetry": 3,
        "downloadURL": "https://dl.google.com/dl/android/studio/install/3.4.1.0/android-studio-ide-183.5522156-windows.exe",
        "pingAddress": "http://www.google.com/generate_204",
        "stunURL": "udp://stunserver2024.stunprotocol.org:3478",
        "taskTimeout": 3000,
        "dnsServer": [
            "119.29.29.29:53",
            "223.5.5.5:53"
        ],
        "apiVersion": 2
    },
    "skipCertVerify": True,
    "tls": False,
    "invoker": "114514",
    "buildtoken": "MIAOKO4|580JxAo049R|GEnERAl|1X571R930|T0kEN",
    "path": "/miaospeed"
}

local_slave = miaolib.MiaoSpeedSlave().from_obj(slave_cfg)
isalive = asyncio.run(miaolib.MiaoSpeed.isalive(local_slave))
print("miaospeed slave isalive:", isalive)
```