#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: www
@Date: 2024/6/26 下午2:17
@Description: 
"""
import base64
import hashlib
import ssl
import time
import asyncio
from copy import deepcopy
from typing import Tuple

import aiohttp
from aiohttp import WSMsgType, ClientConnectorError, ClientWebSocketResponse, WSCloseCode
from async_timeout import timeout
from loguru import logger

from .types.config import MiaoSpeedSlave
from .types.items import ItemType, BaseItem, ScriptItem, GEO_ITEMS
from .types.miaospeed import *
from .types.miaospeed import Script as MSScript
from .types.task import SlaveRequest as KoiSlaveRequest

__version__ = "0.1.0"
MS_BUILDTOKEN = "MIAOKO4|580JxAo049R|GEnERAl|1X571R930|T0kEN"  # miaospeed的build_token
MS_CONN = {}  # 保存websocket连接池


class MiaoSpeed:
    def __init__(self,
                 slave_config: MiaoSpeedSlave,
                 slave_request: SlaveRequest,
                 proxyconfig: List[dict] = None,
                 debug: bool = False,
                 ):
        """
        初始化miaospeed
        :param slave_config 测速后端自定义配置
        :param slave_request: MS的请求结构体
        :param debug 是否是debug模式，会打印出多一点信息

        """
        self.scfg = slave_config
        self.buildtoken = slave_config.buildtoken or MS_BUILDTOKEN
        self.token = slave_config.token
        addr = slave_config.address if slave_config.address else ""
        i = addr.rfind(":")
        self.host = addr[:i]
        try:
            self.port = int(addr[i + 1:])
        except (TypeError, ValueError):
            raise ValueError(f"can not parse address: {addr}")
        self.path = "/" + slave_config.path.removeprefix("/") if slave_config.path else "/"
        if self.path == "/":
            logger.warning("unsafer path, please set a safer path for miaospeed: " + self.path)

        self.nodes = proxyconfig or []
        if slave_config.tls:
            self.ssl_type = SSLType.SECURE if not slave_config.skipCertVerify else SSLType.SELF_SIGNED
        else:
            self.ssl_type = SSLType.NONE
        self.ws_scheme, self.verify_ssl = self.get_ws_opt()
        self._debug = debug
        self.SlaveRequest = slave_request
        if self.nodes and not slave_request.Nodes:
            self.SlaveRequest.Nodes = [SlaveRequestNode(str(i), str(node)) for i, node in enumerate(self.nodes)]

        self.check_slave_request()
        # if slave_config:
        #     self.SlaveRequest.Configs = slave_config
        # self.SlaveRequest.Nodes = self.slaveRequestNode
        self.tempinfo = {"节点名称": [], "类型": []}
        self.last_progress = 0
        self.realtime_flag = False
        self.realtime_flag2 = False

    def check_slave_request(self):
        if not self.SlaveRequest.Options.Matrices:
            raise ValueError(f"SlaveRequest.Options.Matrices is empty")
        # if not self.SlaveRequest.Nodes:
        #     raise ValueError(f"SlaveRequest.Nodes is empty")

    def hash_miaospeed(self, token: str, request: str):
        token = token or self.token
        request = request or self.SlaveRequest.to_json()
        buildTokens = [token] + self.buildtoken.strip().split('|')
        hasher = hashlib.sha512()
        hasher.update(request.encode())

        for t in buildTokens:
            if t == "":
                t = "SOME_TOKEN"

            copy = hasher.copy()
            copy.update(t.encode())
            copy.update(hasher.digest())
            hasher = copy

        hash_url_safe = base64.urlsafe_b64encode(hasher.digest()).decode().replace("+", "-").replace("/", "_")
        return hash_url_safe

    def sign_request(self):
        self.SlaveRequest.RandomSequence = "random"
        copysrt = deepcopy(self.SlaveRequest)  # 用深拷贝复制一份请求体数据，python拷贝行为涉及可变和不可变序列。
        copysrt.Challenge = ""  # 置为空是因为要与这个值进行比较，要是不为空，大概永远也过不了验证
        copysrt.Vendor = ""  # 因为miaospeed在这里拷贝的时候，并没有拷贝原来的Vendor值

        srt_json = copysrt.to_json()
        signed_req = self.hash_miaospeed(self.token, srt_json)
        self.SlaveRequest.Challenge = signed_req
        return signed_req

    async def start(self, slavereq: KoiSlaveRequest = None):
        start_time = time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())
        resdata = {}
        conn_key = f"{self.host}:{self.port}:{start_time}"
        ws_scheme, verify_ssl = self.get_ws_opt()
        if len(MS_CONN) > 100:  # 清理占用
            logger.warning("WebSocket连接资源已超过100条，请联系开发者优化。")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.ws_connect(f"{ws_scheme}://{self.host}:{self.port}{self.path}",
                                              verify_ssl=verify_ssl) as ws:
                    self.sign_request()  # 签名请求
                    time1 = time.time()
                    self.last_progress = time1
                    if conn_key not in MS_CONN:
                        MS_CONN[conn_key] = ws
                    await ws.send_str(self.SlaveRequest.to_json())
                    while True:
                        msg = await ws.receive()
                        if self._debug:
                            print(msg.data)
                        if msg.type in (aiohttp.WSMsgType.CLOSED,
                                        aiohttp.WSMsgType.ERROR):
                            logger.info("退出循环")
                            break
                        elif msg.type == WSMsgType.TEXT:
                            ms_data: dict = json.loads(msg.data)
                            print(msg.data)
                            if not ms_data:
                                continue
                            # 写下你的业务逻辑
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            pass
                    # await ws.close()
                    await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                                   message=b'(EOF)The connection is closed by the peer.')

            except ClientConnectorError as e:
                logger.error(str(e))
            except asyncio.TimeoutError:
                logger.error(f"TimeoutError: {self.host}:{self.port}")
            except Exception as e:
                logger.exception(str(e))
                logger.error(str(e))
            finally:
                if conn_key in MS_CONN:
                    conn: ClientWebSocketResponse = MS_CONN.pop(conn_key)
                    await conn.close()
                return resdata, start_time

    def get_ws_opt(self) -> Tuple[str, bool]:
        if self.ssl_type == SSLType.SECURE:
            ssl_context = ssl.create_default_context()
            verify_ssl = True
        elif self.ssl_type == SSLType.SELF_SIGNED:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            verify_ssl = False
        elif self.ssl_type == SSLType.NONE:
            ssl_context = None
            verify_ssl = None
        else:
            raise ValueError(f"ssl_type error: {type(self.ssl_type).__name__}:{self.ssl_type}")
        ws_scheme = "ws" if ssl_context is None else "wss"
        return ws_scheme, verify_ssl

    async def ping(self, session: aiohttp.ClientSession):
        ws_scheme, verify_ssl = self.get_ws_opt()
        try:
            async with session.ws_connect(f"{ws_scheme}://{self.host}:{self.port}{self.path}",
                                          verify_ssl=verify_ssl) as ws:
                self.sign_request()  # 签名请求
                await ws.send_str(self.SlaveRequest.to_json())
                while True:
                    msg = await ws.receive()
                    if msg.type in (aiohttp.WSMsgType.CLOSED,
                                    aiohttp.WSMsgType.ERROR):
                        return False
                    elif msg.type == WSMsgType.TEXT:
                        return True
        except (ClientConnectorError, asyncio.TimeoutError):
            return False
        except Exception as e:
            logger.error(str(e))
            return False

    @staticmethod
    async def stop(conn_key: str) -> str:
        if conn_key in MS_CONN:
            ws_conn = MS_CONN.get(conn_key, None)
            if isinstance(ws_conn, ClientWebSocketResponse):
                try:
                    MS_CONN.pop(conn_key, None)
                    await ws_conn.close(code=WSCloseCode.GOING_AWAY)
                    return ""
                except Exception as e:
                    logger.warning(str(e))
                    return str(e)
            return ""
        else:
            return "ws连接不存在"

    @staticmethod
    async def isalive(slave: MiaoSpeedSlave, session: aiohttp.ClientSession = None) -> bool:
        """
        检查此后端是否存活
        """
        if session is None:
            session = aiohttp.ClientSession()
            should_close = True
        else:
            should_close = False

        try:
            if slave.type == "miaospeed":
                srme_list = [SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_CONN, "")]
                slopt = SlaveRequestOptions(Matrices=srme_list)
                msreq = SlaveRequest(Options=slopt)
                try:
                    ms = MiaoSpeed(slave, msreq, [])
                except (TypeError, ValueError) as e:
                    logger.exception(e)
                    return False
                # ms = MiaoSpeed(msbuild_token, [], srme_list, host, ws_port, slave.token, ssl_opt, slave.path)
                ms.SlaveRequest.Basics.Invoker = slave.invoker or ""
                async with timeout(10):
                    res = await ms.ping(session)
                    return bool(res)
        except (asyncio.exceptions.TimeoutError, aiohttp.WSServerHandshakeError, ClientConnectorError):
            return False
        except Exception as e:
            logger.error(e)
            return False
        finally:
            if should_close:
                await session.close()


def build_req_matrix(items: List[ItemType] = None) -> List[SlaveRequestMatrixEntry]:
    if items is None or not isinstance(items[0], (BaseItem, ScriptItem)):
        return []
    srme_list = []
    for i in items:
        if i.name == "TEST_SCRIPT":
            srme_list.append(
                SlaveRequestMatrixEntry(
                    Type=SlaveRequestMatrixType.TEST_SCRIPT,
                    Params=i.script.name
                )
            )
        elif i.name == "TEST_PING_RTT":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_RTT, ""))
        elif i.name == "TEST_PING_MAX_RTT":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_MAX_RTT, ""))
        elif i.name == "TEST_PING_SD_RTT":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_SD_RTT, ""))
        elif i.name == "TEST_PING_SD_CONN":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_SD_CONN, ""))
        elif i.name == "TEST_PING_CONN":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_CONN, ""))
        elif i.name == "TEST_HTTP_CODE":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_HTTP_CODE, ""))
        elif i.name == "TEST_PING_TOTAL_CONN":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_TOTAL_CONN, ""))
        elif i.name == "TEST_PING_TOTAL_RTT":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.TEST_PING_TOTAL_RTT, ""))
        elif i.name == "SPEED_AVERAGE":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.SPEED_AVERAGE, "0"))
        elif i.name == "SPEED_MAX":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.SPEED_MAX, "0"))
        elif i.name == "SPEED_PER_SECOND":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.SPEED_PER_SECOND, "0"))
        elif i.name == "UDP_TYPE":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.UDP_TYPE, "0"))
        elif i.name == "GEOIP_INBOUND":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.GEOIP_INBOUND, i.script.name))
        elif i.name == "GEOIP_OUTBOUND":
            srme_list.append(SlaveRequestMatrixEntry(SlaveRequestMatrixType.GEOIP_OUTBOUND, i.script.name))
    return srme_list


async def miaospeed_client(slavereq: KoiSlaveRequest):
    if not isinstance(slavereq.slave, MiaoSpeedSlave):
        raise TypeError("slavereq.slave must be MiaoSpeedSlave")
    if slavereq.slave.path is None or not isinstance(slavereq.slave.path, str):
        slavereq.slave.path = "/"
    srme_list = build_req_matrix(slavereq.items)
    slave_option = slavereq.slave.option
    # if slavereq.runtime.speedThreads:
    #     slave_option.downloadThreading = slavereq.runtime.speedThreads
    # if slavereq.runtime.pingURL:
    #     slave_option.pingAddress = slavereq.runtime.pingURL
    # if slavereq.runtime.duration:
    #     slave_option.downloadDuration = slavereq.runtime.duration
    # if slavereq.runtime.speedFiles:
    #     slave_option.downloadURL = slavereq.runtime.speedFiles
    # if slavereq.runtime.stunURL:
    #     slave_option.stunURL = slavereq.runtime.stunURL

    # if slavereq.runtime.ipstack is None:
    #     slavereq.runtime.ipstack = CONFIG.runtime.ipstack
    # if slavereq.runtime.entrance is None:
    #     slavereq.runtime.entrance = CONFIG.runtime.entrance
    srcfg = SlaveRequestConfigs.from_option(slave_option).merge_runtime(slavereq.runtime)
    slopt = SlaveRequestOptions(Matrices=srme_list)
    msreq = SlaveRequest(
        SlaveRequestBasics(
            ID=slavereq.task.name,
            Slave=str(slavereq.slave.id),
            SlaveName=slavereq.slave.comment,
            Invoker=str(slavereq.slave.invoker) or f"miaolib/{__version__}",
            Version=f"miaolib/{__version__}"
        ),
        slopt,
        srcfg
    )
    for item in slavereq.items:
        if item.script and item.script.content:
            if item.script.name in GEO_ITEMS:
                msreq.Configs.Scripts.append(MSScript(ID=item.script.name, Type=ScriptType.STypeIP.value,
                                                      Content=item.script.content))
            else:
                msreq.Configs.Scripts.append(MSScript(ID=item.script.name, Content=item.script.content))
    ms = MiaoSpeed(slavereq.slave, msreq, slavereq.proxies)

    try:
        result, _ = await ms.start(slavereq)
        if 'error' in result:
            return
        # result = ResultCleaner(result, sf).start(slavereq.runtime.sort)
    except Exception as e:
        logger.error(str(e))
        return

    msg_id = slavereq.task.messageID
    chat_id = slavereq.task.botMsgChatID
    botmsg_id = slavereq.task.botMsgID

    if not msg_id and not botmsg_id and not chat_id:
        logger.warning("获取消息失败！")
        return
    if isinstance(result, dict) and result:
        print(result)
    elif isinstance(result, str):
        pass


if __name__ == '__main__':
    pass
