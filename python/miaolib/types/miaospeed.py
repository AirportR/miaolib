#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: www
@Date: 2024/6/26 下午2:09
@Description: 
"""
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .config import DEFAULT_PING_ADDRESS, DEFAULT_SPEEDFILE, MiaoSpeedOption, DictCFG
from .task import SlaveRuntimeOption


class ScriptType(Enum):
    STypeMedia: str = "media"
    STypeIP: str = "ip"


class SSLType(Enum):
    NONE: int = 0
    SECURE: int = 1
    SELF_SIGNED: int = 2


@dataclass
class Script(DictCFG):
    ID: str
    Type: str = ScriptType.STypeMedia
    Content: str = ""
    TimeoutMillis: int = 0

    def from_obj(self, obj: dict) -> "Script":
        if 'Type' in obj:
            raw_v = obj.pop('Type')
            try:
                self.Type = ScriptType(raw_v).value
            except ValueError:
                self.Type = ScriptType.STypeMedia.value
        super().from_obj(obj)
        return self


@dataclass
class SlaveRequestConfigs(DictCFG):
    STUNURL: str = 'udp://stunserver2024.stunprotocol.org:3478'
    DownloadURL: str = DEFAULT_SPEEDFILE
    DownloadDuration: int = 8
    DownloadThreading: int = 4
    PingAverageOver: int = 5
    PingAddress: str = DEFAULT_PING_ADDRESS
    TaskRetry: int = 3
    DNSServers: list = field(default_factory=lambda: [])
    TaskTimeout: int = 2500
    Scripts: List[Script] = field(default_factory=lambda: [])
    ApiVersion: int = 1

    def from_obj(self, obj: dict) -> "DictCFG":
        if 'Scripts' in obj:
            raw_v = obj.pop('Scripts')
            self.from_list('Scripts', raw_v, Script)
        super().from_obj(obj)
        return self

    @staticmethod
    def from_option(slave_option: MiaoSpeedOption) -> "SlaveRequestConfigs":
        srcfg = SlaveRequestConfigs()
        if not isinstance(slave_option, MiaoSpeedOption):
            return srcfg
        srcfg.DownloadURL = slave_option.downloadURL
        srcfg.STUNURL = slave_option.stunURL
        srcfg.DownloadDuration = slave_option.downloadDuration
        srcfg.DownloadThreading = slave_option.downloadThreading
        srcfg.PingAverageOver = slave_option.pingAverageOver
        srcfg.PingAddress = slave_option.pingAddress
        srcfg.TaskRetry = slave_option.taskRetry
        srcfg.TaskTimeout = slave_option.taskTimeout
        srcfg.DNSServers = slave_option.dnsServer
        srcfg.ApiVersion = slave_option.apiVersion
        srcfg.patch_version()
        return srcfg

    def merge_runtime(self, runtime_cfg: SlaveRuntimeOption) -> "SlaveRequestConfigs":
        if runtime_cfg.speedThreads:
            self.DownloadThreading = runtime_cfg.speedThreads
        if runtime_cfg.pingURL:
            self.PingAddress = runtime_cfg.pingURL
        if runtime_cfg.duration:
            self.DownloadDuration = runtime_cfg.duration
        if runtime_cfg.speedFiles:
            self.DownloadURL = runtime_cfg.speedFiles
        if runtime_cfg.stunURL:
            self.STUNURL = runtime_cfg.stunURL
        return self

    def patch_version(self):
        if self.ApiVersion == 0 or self.ApiVersion == 1:
            # patch the class
            delattr(self, "ApiVersion")
        return self


@dataclass
class SlaveRequestBasics(DictCFG):
    ID: str
    Slave: str
    SlaveName: str
    Invoker: str
    Version: str


class SlaveRequestMatrixType(Enum):
    SPEED_AVERAGE = "SPEED_AVERAGE"
    SPEED_MAX = "SPEED_MAX"
    SPEED_PER_SECOND = "SPEED_PER_SECOND"
    UDP_TYPE = "UDP_TYPE"
    GEOIP_INBOUND = "GEOIP_INBOUND"
    GEOIP_OUTBOUND = "GEOIP_OUTBOUND"
    TEST_SCRIPT = "TEST_SCRIPT"
    TEST_PING_CONN = "TEST_PING_CONN"
    TEST_PING_RTT = "TEST_PING_RTT"
    TEST_PING_MAX_CONN = "TEST_PING_MAX_CONN"
    TEST_PING_MAX_RTT = "TEST_PING_MAX_RTT"
    TEST_PING_SD_CONN = "TEST_PING_SD_CONN"
    TEST_PING_SD_RTT = "TEST_PING_SD_RTT"
    TEST_HTTP_CODE = "TEST_HTTP_CODE"
    TEST_PING_TOTAL_RTT = "TEST_PING_TOTAL_RTT"
    TEST_PING_TOTAL_CONN = "TEST_PING_TOTAL_CONN"
    INVALID = "INVALID"


class VendorType(Enum):
    VendorLocal: str = "Local"
    VendorClash: str = "Clash"
    VendorInvalid: str = "Invalid"


@dataclass
class SlaveRequestMatrixEntry(DictCFG):
    Type: SlaveRequestMatrixType = SlaveRequestMatrixType.INVALID
    Params: str = ""  # 这个值的作用是配合Script.ID 的，设置为一致即可

    def from_obj(self, obj: dict) -> "SlaveRequestMatrixEntry":
        if 'Type' in obj:
            raw_v = obj.pop('Type')
            try:
                self.Type = SlaveRequestMatrixType(raw_v)
            except ValueError:
                self.Type = SlaveRequestMatrixType.INVALID
        super().from_obj(obj)
        return self


@dataclass
class SlaveRequestOptions(DictCFG):
    Filter: str = ""
    Matrices: List[SlaveRequestMatrixEntry] = field(default_factory=lambda: [])

    def from_obj(self, obj: dict) -> "SlaveRequestOptions":
        if 'Matrices' in obj:
            self.from_list('Matrices', obj.pop('Matrices'), SlaveRequestMatrixEntry)
        super().from_obj(obj)
        return self


@dataclass
class SlaveRequestNode(DictCFG):
    Name: str = ""
    Payload: str = ""


@dataclass
class SlaveRequest(DictCFG):
    Basics: SlaveRequestBasics = field(default_factory=lambda: SlaveRequestBasics(
        ID="114514",
        Slave="114514miaospeed",
        SlaveName="slave1",
        Invoker="114514",
        Version="1.0"
    ))
    Options: SlaveRequestOptions = field(default_factory=lambda: SlaveRequestOptions())
    Configs: SlaveRequestConfigs = field(default_factory=lambda: SlaveRequestConfigs())
    Vendor: VendorType = VendorType.VendorClash
    Nodes: List[SlaveRequestNode] = field(default_factory=lambda: [])
    RandomSequence: str = ""
    Challenge: str = ""

    def from_obj(self, obj: dict) -> "SlaveRequest":
        if 'Vendor' in obj:
            raw_v = obj.pop('Vendor')
            try:
                self.Vendor = VendorType(raw_v)
            except ValueError:
                self.Vendor = VendorType.VendorInvalid
        if 'Nodes' in obj:
            raw_v = obj.pop('Nodes')
            self.from_list('Nodes', raw_v, SlaveRequestNode)
        super().from_obj(obj)
        return self

    def to_json(self):
        json_str = json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else o.__dict__,
                              ensure_ascii=False, separators=(',', ':'))
        json_str = json_str.replace('<', r'\u003c').replace('>', r'\u003e').replace('&', r'\u0026')
        return json_str


@dataclass
class ProxyInfo(DictCFG):
    Name: str = None
    Address: str = None
    Type: str = None


@dataclass
class MatrixResponse(DictCFG):
    Type: SlaveRequestMatrixType = None
    Payload: str = None

    def from_obj(self, obj: dict) -> "MatrixResponse":
        raw_v = obj.pop('Type', None)
        if raw_v is not None:
            try:
                self.Type = SlaveRequestMatrixType(raw_v)
            except ValueError:
                self.Type = SlaveRequestMatrixType.INVALID
        super().from_obj(obj)
        return self


@dataclass
class SlaveEntrySlot(DictCFG):
    Grouping: str = ''
    ProxyInfo: ProxyInfo = field(default_factory=lambda: ProxyInfo())
    InvokeDuration: int = 0
    Matrices: List[MatrixResponse] = field(default_factory=list)

    def from_obj(self, obj: dict) -> "SlaveEntrySlot":
        if 'Matrices' in obj:
            raw_v = obj.pop('Matrices')
            self.from_list('Matrices', raw_v, MatrixResponse)
        super().from_obj(obj)
        return self


@dataclass
class SlaveTask(DictCFG):
    Request: SlaveRequest = field(default_factory=lambda: SlaveRequest())
    Results: List[SlaveEntrySlot] = field(default_factory=list)

    def from_obj(self, obj: dict) -> "SlaveTask":
        if 'Results' in obj:
            raw_v = obj.pop('Results')
            self.from_list('Results', raw_v, SlaveEntrySlot)
        super().from_obj(obj)
        return self


@dataclass
class SlaveProgress(DictCFG):
    Index: int = 0
    Record: SlaveEntrySlot = field(default_factory=lambda: SlaveEntrySlot())
    Queuing: int = 0


@dataclass
class SlaveResponse(DictCFG):
    ID: str = ""
    MiaoSpeedVersion: str = ""
    Error: str = ""
    Result: SlaveTask = field(default_factory=lambda: SlaveTask())
    Progress: SlaveProgress = field(default_factory=lambda: SlaveProgress())
