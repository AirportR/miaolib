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

# For other miaospeed branch：
```python
import yaml
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
        "apiVersion": 1 # change to 1 for other branch
    },
    "skipCertVerify": True, # self-signed certificate
    "tls": True, # recommended 
    "invoker": "114514",
    "buildtoken": "MIAOKO4|580JxAo049R|GEnERAl|1X571R930|T0kEN",
    "path": "/miaospeed"
}
async def miaospeed_test(_nodes):
    srme_list = [
        miaolib.SlaveRequestMatrixEntry(miaolib.SlaveRequestMatrixType.TEST_PING_RTT, ""),
        miaolib.SlaveRequestMatrixEntry(miaolib.SlaveRequestMatrixType.TEST_PING_CONN, ""),
        miaolib.SlaveRequestMatrixEntry(miaolib.SlaveRequestMatrixType.GEOIP_OUTBOUND, ""),
        miaolib.SlaveRequestMatrixEntry(miaolib.SlaveRequestMatrixType.GEOIP_INBOUND, ""),
        # miaolib.SlaveRequestMatrixEntry(
        #     Type=miaolib.SlaveRequestMatrixType.TEST_SCRIPT,
        #     Params="IP"
        # ), # add script test if needed
    ]
    msreq = miaolib.SlaveRequest(
        miaolib.SlaveRequestBasics(
            ID="114514",
            Slave="114514",
            SlaveName="slave",
            Invoker="11111111111",
            Version="4.3.3"
        ),
        miaolib.SlaveRequestOptions(Matrices=srme_list),
    )
    msreq.Configs.patch_version() # for other branch
    # with open("./iptype.js", 'r', encoding="UTF-8") as _fp:
    #     js_content = _fp.read() # read script content , name='IP', ID='IP'
    # msreq.Configs.Scripts.append(miaolib.Script(ID="IP", Content=js_content)) # add script to SlaveRequest.Configs.Scripts
    ms = miaolib.MiaoSpeed(slave_config=miaolib.MiaoSpeedSlave().from_obj(slave_cfg), slave_request=msreq,
                                proxyconfig=_nodes)
    # You can add DNS servers to SlaveRequest.Configs.DNSServers, e.g.
    # ms.SlaveRequest.Configs.DNSServers.append("119.29.29.29:53")

    res, start_time = await ms.start()
    return res, start_time
# load clash nodes from Clash.yaml
with open(f"Clash.yaml", 'r', encoding="UTF-8") as fp:
    nodes = yaml.safe_load(fp)['proxies']
print("Your Clash nodes:\n", nodes)
result, _ = miaospeed_test(nodes)
print("result of miaospeed:\n", result)
```

# Tips

- You shoud rewrite the MiaoSpeed.start() method to fit your own test logic.
