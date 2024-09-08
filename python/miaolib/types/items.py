#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: www
@Date: 2024/6/25 下午5:29
@Description: 
"""
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TypeVar

from .config import Script, DictCFG, KoiConfig, ScriptType

DEFAULT_GEOSCRIPT = r"""const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36';
const RETRY = 1;
const TIMEOUT = 3000;
function ip_resolve() {
    const endpoints = ["https://1.1.1.1/cdn-cgi/trace", "https://[2606:4700:4700::1111]/cdn-cgi/trace"];
    const ret = [];
    for (let i = 0; i < endpoints.length; i++) {
        const url = endpoints[i];
        const content = (get(fetch(url, {
            headers: {
                'User-Agent': UA,
            },
            retry: RETRY,
            timeout: 2000,
        }), "body") || "").trim();
        const ip = (content.split('\n').filter(s => s.startsWith('ip='))[0] || 'ip=').substr(3);
        if (ip) ret.push(ip);
    }
    return ret;
}
function handler_ipsb(ip) {
    const content = fetch("https://api.ip.sb/geoip/"+ip, {
        headers: {
            'User-Agent': UA
        },
        retry: RETRY,
        timeout: TIMEOUT
    })
    return safeParse(get(content, "body"));
}
function handler_bgptools(ip) {
    if (!ip) {
        ip = ip_resolve()[0]
    }
    const ret = netcat("bgp.tools:43", `begin\n${ip}\nend\n`);
    if (ret.error) {
        println("NetCat Error:", ret.error);
    }
    const data = get(ret, "data", "").split("|");
    const as = parseInt((data[0] || "").trim(), 10) || 0;
    const ipaddr = (data[1] || "").trim();
    const region = (data[3] || "").trim();
    const org = (data[6] || "").trim();
    return {
        "ip": ipaddr,
        "isp": org,
        "organization": org,
        "asn": as,
        "asn_organization": org,
        "region": region,
        "country": region,
        "country_code": region,
    }
}
function handler_ipinfo(ip) {
    const content = fetch("https://ipinfo.io/"+ip,{
        headers: {
            'User-Agent': UA
        },
        retry: RETRY,
        timeout: TIMEOUT
    })
    const ret = safeParse(get(content, "body"));
    const asInfo = get(ret, "org", "").split(" ");
    const asn = asInfo.shift();
    const org = asInfo.join(" ");
    const loc = get(ret, "loc", "").split(",");
    return {
        "ip": get(ret, "ip", ""),
        "isp": org,
        "organization": org,
        "latitude": parseFloat(loc[0]),
        "longitude": parseFloat(loc[1]),
        "asn": parseInt(asn.replace("AS", ""), 10),
        "asn_organization": org,
        "timezone": get(ret, "timezone", ""),
        "region": get(ret, "region", ""),
        "city": get(ret, "city", ""),
        "country": get(ret, "country", ""),
        "country_code": get(ret, "country", ""),
        "hostname": get(ret, "hostname", ""),
    }
}
function handler_ipleak(ip) {
    const isv6 = ip.includes(":")
    let geoip_api = `https://ipv4.ipleak.net/json/${ip}`
    if (isv6){
        geoip_api = `https://ipv6.ipleak.net/json/${ip}`
    }
    const content = fetch(geoip_api, {
        headers: {
            'User-Agent': UA,
        },
        retry: 0,
        timeout: TIMEOUT,
    });
    const ret = safeParse(get(content, "body"));
    return {
        "ip": get(ret, "query", ""),
        "isp": get(ret, "isp_name", ""),
        "organization": get(ret, "isp_name", ""),
        "latitude": get(ret, "latitude", 0),
        "longitude": get(ret, "longitude", 0),
        "asn": parseInt(get(ret, "as_number", 0), 10) || 0,
        "asn_organization": get(ret, "isp_name", ""),
        "timezone": get(ret, "time_zone", ""),
        "region": get(ret, "region_name", ""),
        "city": get(ret, "city", ""),
        "country": get(ret, "city_name", ""),
        "country_code": get(ret, "country_code", ""),
    }
}
function handler_ipapi(ip) {
    const content = fetch(`http://ip-api.com/json/${ip}?lang=en-US`, {
        headers: {
            'User-Agent': UA,
        },
        retry: RETRY,
        timeout: TIMEOUT,
    });
    const ret = safeParse(get(content, "body"));
    const asInfo = get(ret, "as", "").split(" ");
    const asn = (asInfo.shift() || "").substr(2);
    const asnorg = asInfo.join(" ");
    return {
        "ip": get(ret, "query", ""),
        "isp": get(ret, "isp", ""),
        "organization": get(ret, "org", ""),
        "latitude": get(ret, "lat", 0),
        "longitude": get(ret, "lon", 0),
        "asn": parseInt(asn, 10) || 0,
        "asn_organization": asnorg,
        "timezone": get(ret, "timezone", ""),
        "region": get(ret, "region", ""),
        "city": get(ret, "city", ""),
        "country": get(ret, "country", ""),
        "country_code": get(ret, "countryCode", ""),
    }
}
function handler_findmyip(ip) {
    const content = fetch(`https://findmyip.net/api/ipinfo.php?ip=${ip}`, {
        headers: {
            'User-Agent': UA,
        },
        retry: 1,
        timeout: 5000,
    });
    if (!content){
        return ''
    }
    if (content.statusCode !== 200) {
        return '';
    }
    const ipdata = JSON.parse(content.body);

    const API_1 = ipdata?.data?.API_1 || {};
    const API_2 = ipdata?.data?.API_2 || {};
    const api_info = Object.keys(API_1).length ? API_1 : API_2;

    const a1 = api_info.province || "";
    const a2 = api_info.city || "";
    const a3 = api_info.county || "";
    const a4 = api_info.isp || "";

    let region = `${a1}${a2}${a3}`;
    if (a4) {
        region += ` ${a4}`;
    }
    return region
}
const handler_array = [handler_ipsb,handler_ipinfo,handler_ipapi,handler_bgptools,handler_ipleak]
function handler(ip) {
    let ret = {};
    handler_array.some(handler_func => {
        ret = handler_func(ip);
        if (ret && ret.ip && ret.asn_organization && get(ret, "asn", 0)) {
            return ret;
        }
    });
    
    if (ret){
        if (ret.country_code && ret.country_code.trim().toUpperCase() !== "CN"){
            ret.country_code += "国际入口";
            return ret;
        }
        region2 = handler_findmyip(ip);
        if (region2) {
           ret.country_code += region2;
        }

    }
    return ret;
}
"""


@dataclass
class BaseItem(DictCFG):
    name: str = "BASE"
    script: Script = None


ItemType = TypeVar('ItemType', bound='BaseItem')


@dataclass
class ScriptItem(BaseItem):
    name: str = "TEST_SCRIPT"
    script: Script = None

    def from_str(self, itemstr: str, koicfg: KoiConfig) -> "ScriptItem":
        for script in koicfg.scriptConfig.scripts:
            if script.name == itemstr:
                self.script = deepcopy(script)
                self.script.resolve(self.script.content)  # 将文件路径转化成具体内容
        return self

    def from_script(self, script: Script):
        if not isinstance(script, Script):
            return self

        copyscript = deepcopy(script)
        self.script = copyscript
        if copyscript.type == ScriptType.GoBuiltin:
            if copyscript.name == "TEST_PING_RTT":
                return TCPTest(script=copyscript)
            elif copyscript.name == "TEST_PING_CONN":
                return HTTPTest(script=copyscript)
            elif copyscript.name == "SPEED_AVERAGE":
                return AvgSpeed(script=copyscript)
            elif copyscript.name == "SPEED_MAX":
                return MaxSpeed(script=copyscript)
            elif copyscript.name == "SPEED_PER_SECOND":
                return PerSecond(script=copyscript)
            elif copyscript.name == "UDP_TYPE":
                return UDPType(script=copyscript)
            elif copyscript.name == "GEOIP_INBOUND":
                return InboundScript(script=copyscript)
            elif copyscript.name == "GEOIP_OUTBOUND":
                return OutboundScript(script=copyscript)
            elif copyscript.name == "TEST_PING_MAX_RTT":
                return TCPTestMAX(script=copyscript)
            elif copyscript.name == "TEST_PING_SD_RTT":
                return TCPTestSD(script=copyscript)
            elif copyscript.name == "TEST_PING_SD_CONN":
                return HTTPTestSD(script=copyscript)
            elif copyscript.name == "TEST_HTTP_CODE":
                return HTTPCode(script=copyscript)
            elif copyscript.name == "TEST_PING_TOTAL_RTT":
                return TotalRTT(script=copyscript)
            elif copyscript.name == "TEST_PING_TOTAL_CONN":
                return TotalHTTP(script=copyscript)
            print("Can not match the script item: ", copyscript.name)
        elif copyscript.type == ScriptType.GoJajs:
            self.script.resolve(copyscript.content)
        else:
            print("Can not match the script type: ", copyscript.type)
        if self.script and self.script.name in GEO_ITEMS:
            self.name = self.script.name
        return self


@dataclass
class SpeedItem(BaseItem):
    name: str = "SPEED"
    script: Script = None


@dataclass
class AvgSpeed(SpeedItem):
    name: str = "SPEED_AVERAGE"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="SPEED_AVERAGE", rank=-98))


@dataclass
class MaxSpeed(BaseItem):
    name: str = "SPEED_MAX"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="SPEED_MAX", rank=-97))


@dataclass
class PerSecond(BaseItem):
    name: str = "SPEED_PER_SECOND"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="SPEED_PER_SECOND", rank=-96))


@dataclass
class HTTPTest(BaseItem):
    name: str = "TEST_PING_CONN"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_CONN", rank=-99))


@dataclass
class TCPTest(BaseItem):
    name: str = "TEST_PING_RTT"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_RTT", rank=-100))


@dataclass
class TCPTestMAX(BaseItem):
    name: str = "TEST_PING_MAX_RTT"
    script: Script = field(
        default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_MAX_RTT", rank=-100))


@dataclass
class TCPTestSD(BaseItem):
    name: str = "TEST_PING_SD_RTT"
    script: Script = field(
        default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_SD_RTT", rank=-100))


@dataclass
class HTTPTestSD(BaseItem):
    name: str = "TEST_PING_SD_CONN"
    script: Script = field(
        default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_SD_CONN", rank=-100))


@dataclass
class TotalRTT(BaseItem):
    name: str = "TEST_PING_TOTAL_RTT"
    script: Script = field(
        default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_TOTAL_RTT", rank=-100))


@dataclass
class TotalHTTP(BaseItem):
    name: str = "TEST_PING_TOTAL_CONN"
    script: Script = field(
        default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_PING_TOTAL_CONN", rank=-100))


@dataclass
class HTTPCode(BaseItem):
    name: str = "TEST_HTTP_CODE"
    script: Script = field(
        default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="TEST_HTTP_CODE", rank=-100))


@dataclass
class UDPType(BaseItem):
    name: str = "UDP_TYPE"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="UDP_TYPE", rank=100))


@dataclass
class UDPType(BaseItem):
    name: str = "UDP_TYPE"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="UDP_TYPE", rank=100))


@dataclass
class Inbound(ScriptItem):
    name: str = "GEOIP_INBOUND"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="GEOIP_INBOUND", rank=1))


@dataclass
class Outbound(ScriptItem):
    name: str = "GEOIP_OUTBOUND"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoBuiltin, name="GEOIP_OUTBOUND", rank=1))


@dataclass
class InboundScript(ScriptItem):
    name: str = "GEOIP_INBOUND"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoJajs, name="GEOIP_INBOUND", rank=1,
                                                          content=DEFAULT_GEOSCRIPT))


@dataclass
class OutboundScript(ScriptItem):
    name: str = "GEOIP_OUTBOUND"
    script: Script = field(default_factory=lambda: Script(type=ScriptType.GoJajs, name="GEOIP_OUTBOUND", rank=1,
                                                          content=DEFAULT_GEOSCRIPT))


SPEED_ITEMS = ["SPEED_AVERAGE", "SPEED_MAX", "SPEED_PER_SECOND"]
GEO_ITEMS = ["GEOIP_INBOUND", "GEOIP_OUTBOUND"]
PING_ITEMS = ["TEST_PING_CONN", "TEST_PING_RTT", "TEST_PING_MAX_RTT", "TEST_PING_SD_RTT", "TEST_PING_SD_CONN"]
