#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: koipy-org
@Date: 2024/6/17 下午1:05
@Description: 
"""
import time
from typing import List
from .config import SlaveType, RuntimeCFG
from .items import *


@dataclass
class Task:
    url: str = ""
    site: str = ""
    name: str = "连通性测试"
    creator: int = None
    messageID: int = None
    chatID: int = None
    botMsgID: int = None
    botMsgChatID: int = None
    createTime: float = field(default_factory=lambda: time.time())

    def ready(self):
        return all([
            self.url != "",
            self.site != "",
            self.creator is not None,
            self.messageID is not None,
            self.chatID is not None
        ])


class OutputType:
    CSV: str = "csv"
    JSON: str = "json"
    HTML: str = "html"
    IMAGE: str = "image"


@dataclass
class SlaveRuntimeOption:
    pingURL: str = None
    speedFiles: str = None
    speedThreads: int = None
    stunURL: str = None
    ipstack: bool = None
    duration: int = None
    entrance: bool = None
    includeFilter: str = ""
    excludeFilter: str = ""
    sort: str = None
    output: str = None
    realtime: bool = False

    def from_runtime(self, runtime: RuntimeCFG):
        if not runtime or not isinstance(runtime, RuntimeCFG):
            return self
        if runtime.pingURL:
            self.pingURL = runtime.pingURL
        if runtime.speedFiles:
            self.speedFiles = runtime.speedFiles[0]
        if runtime.sort:
            self.sort = runtime.sort
        if runtime.speedThreads:
            self.speedThreads = runtime.speedThreads
        if runtime.includeFilter:
            self.includeFilter = runtime.includeFilter
        if runtime.excludeFilter:
            self.excludeFilter = runtime.excludeFilter
        if runtime.ipstack:
            self.ipstack = runtime.ipstack
        if runtime.entrance:
            self.entrance = runtime.entrance
        if runtime.realtime:
            self.realtime = runtime.realtime
        if runtime.interval:
            self.duration = runtime.interval
        if runtime.output:
            self.output = runtime.output
        # not found
        # if runtime.stunURL:
        #     self.stunURL = runtime.stunURL
        return self


@dataclass
class SlaveRequest:
    slave: SlaveType = None
    command: str = None
    items: List[ItemType] = field(default_factory=list)
    task: Task = field(default_factory=lambda: Task())
    runtime: SlaveRuntimeOption = field(default_factory=lambda: SlaveRuntimeOption())
    proxies: List[dict] = field(default_factory=list)
    _ready: bool = False  # 当所有数据都准备好时， 将其设置为 True
    error: str = None

    def ready(self) -> bool:
        if self.slave is None or not self.items or not self.task.ready():
            self._ready = False
            return False
        self._ready = True
        return True

    def merge_items(self, items_list: List[str], cfg: KoiConfig):
        if not isinstance(items_list, list):
            return
        for i_str in items_list:
            script: Script = next(filter(lambda s: s.name == i_str, cfg.scriptConfig.scripts), None)
            if isinstance(script, Script):
                sptitem = ScriptItem().from_script(script)
                self.items.append(sptitem)
            elif i_str == "TEST_PING_RTT":
                self.items.append(TCPTest())
            elif i_str == "TEST_PING_MAX_RTT":
                self.items.append(TCPTestMAX())
            elif i_str == "TEST_PING_SD_RTT":
                self.items.append(TCPTestSD())
            elif i_str == "TEST_PING_SD_CONN":
                self.items.append(HTTPTestSD())
            elif i_str == "TEST_HTTP_CODE":
                self.items.append(HTTPCode())
            elif i_str == "TEST_PING_TOTAL_RTT":
                self.items.append(TotalRTT())
            elif i_str == "TEST_PING_TOTAL_CONN":
                self.items.append(TotalHTTP())
            elif i_str == "TEST_PING_CONN":
                self.items.append(HTTPTest())
            elif i_str == "SPEED_AVERAGE":
                self.items.append(AvgSpeed())
            elif i_str == "SPEED_MAX":
                self.items.append(MaxSpeed())
            elif i_str == "SPEED_PER_SECOND":
                self.items.append(PerSecond())
            elif i_str == "UDP_TYPE":
                self.items.append(UDPType())
            elif i_str == "GEOIP_INBOUND":
                self.items.append(InboundScript())
            elif i_str == "GEOIP_OUTBOUND":
                self.items.append(OutboundScript())
        if self.items:
            self.items = sorted(self.items, key=lambda x: x.script.rank)

    def contain_speed(self):
        for i in self.items:
            if i.name in SPEED_ITEMS:
                return True
        return False

    def contain_geo(self):
        for i in self.items:
            if i.name in GEO_ITEMS or i.script.name in GEO_ITEMS:
                return True

        return False

    def contain_script(self):
        for i in self.items:
            if i.name == "TEST_SCRIPT":
                return True
        return False

    def contain_ping(self):
        for i in self.items:
            if i.name in PING_ITEMS or i.script.name in PING_ITEMS:
                return True
        return False

    def set_slave(self, slave_id: str, slaves_list: List[SlaveType], slave_comment: str = None):
        if not isinstance(slave_id, str) or not slave_id:
            return
        for s in slaves_list:
            if s.id != slave_id:
                continue
            if slave_comment and slave_comment != s.comment:
                continue
            self.slave = deepcopy(s)
            break

    def copy(self):
        sr = deepcopy(self)
        sr.task.createTime = time.time()  # 重新构建时间
        return sr
