"""配置反序列化后得到的类，参数意义请参阅 ./resources/config.example.yaml"""
import os
import pathlib
from dataclasses import field, dataclass, fields
from enum import Enum
from os import PathLike

from pathlib import Path
from typing import List, Dict, Union, Type, TypeVar

from .manager import ConfigManager
from .translation import Translation

try:
    from loguru import logger
except ImportError:
    logger = None
from .base import DictCFG, BaseCFG, AdminList, UserList, ListCFG

HOME_DIR = os.getcwd()

DEFAULT_SPEEDFILE: str = "https://dl.google.com/dl/android/studio/install/3.4.1.0/" \
                         "android-studio-ide-183.5522156-windows.exe"
DEFAULT_PING_ADDRESS: str = "https://cp.cloudflare.com/generate_204"
DEFAULT_FONT_PATH: str = str(Path(HOME_DIR).joinpath("./resources/alibaba-Regular.ttf").absolute().as_posix())


@dataclass
class CoreCFG(DictCFG):
    vendor: str = None
    path: str = None


@dataclass
class ClashCFG(CoreCFG):
    vendor: str = "clash"
    branch: str = "origin"


@dataclass
class Mihomo(ClashCFG):
    vendor: str = "clash"
    branch: str = "meta"


@dataclass
class FullTCoreCFG(CoreCFG):
    vendor: str = "fulltcore"
    buildtoken: str = "c7004ded9db897e538405c67e50e0ef0c3dbad717e67a92d02f6ebcfd1022a5ad1d2c4419541f538ff623051759" \
                      "ec000d2f426e03f9709a6608570c5b9141a6b"


@dataclass
class SubConverterCFG(DictCFG):
    include: str = ""
    exclude: str = ""
    enable: bool = False
    address: str = "127.0.0.1:25500"
    tls: bool = False
    remoteConfig: str = None


@dataclass
class Command(DictCFG):
    name: str = ""
    pin: bool = False
    rule: str = None
    text: str = ""
    enable: bool = True
    attachToInvite: bool = True


@dataclass
class BotCFG(DictCFG):
    api_id: int = None
    api_hash: str = None
    bot_token: str = None
    proxy: str = None
    cacheTime: int = 60
    ipv6: bool = False
    antiGroup: bool = False
    strictMode: bool = False
    bypassMode: bool = False
    parseMode: str = None
    scriptText: str = ""
    analyzeText: str = ""
    speedText: str = ""
    bar: str = "="
    bleft: str = "["
    bright: str = "]"
    bspace: str = "  "
    inviteGroup: list = field(default_factory=list)
    inviteBlacklistURL: list = None
    inviteBlacklistDomain: list = None
    commands: List[Command] = field(default_factory=list)

    def from_obj(self, obj: dict) -> "BotCFG":
        if "commands" in obj:
            raw_v = obj.pop("commands")
            if isinstance(raw_v, list):
                self.from_list("commands", raw_v, Command)

        super().from_obj(obj)
        return self


class SortType:
    ORIGIN: str = "订阅原序"
    HTTP: str = "HTTP升序"
    HTTP_R: str = "HTTP降序"  # http降序
    AVERAGE_SPEED: str = "平均速度升序"
    AVERAGE_SPEED_R: str = "平均速度降序"  # 平均速度降序
    MAX_SPEED: str = "最大速度升序"
    MAX_SPEED_R: str = "最大速度降序"  # 最大速度降序


@dataclass
class RuntimeCFG(DictCFG):
    pingURL: str = "https://www.gstatic.com/generate_204"
    speedFiles: List[str] = field(default_factory=lambda: [DEFAULT_SPEEDFILE])
    speedNodes: int = 300
    speedThreads: int = 4
    ipstack: bool = True
    interval: int = 10
    entrance: bool = True
    includeFilter: str = ""
    excludeFilter: str = ""
    sort: str = SortType.ORIGIN
    output: str = None
    realtime: bool = None

    def from_list(self, attr: str, obj: list, cls=None) -> "RuntimeCFG":
        if isinstance(obj, list):
            self.speedFiles = obj
        elif isinstance(obj, str):
            self.speedFiles = [obj]
        return self

    def from_obj(self, obj: dict) -> "RuntimeCFG":
        if "speedFiles" in obj:
            self.from_list("speedFiles", obj.pop("speedFiles"))
        super().from_obj(obj)
        return self

    def null(self):
        for f in fields(self):
            setattr(self, f.name, None)
        return self


@dataclass
class Color(DictCFG):
    label: float = 0.0
    name: str = ""
    value: str = "#ffffff"
    alpha: int = 255
    end_color: str = "#ffffff"

    def from_obj(self, obj: dict) -> "DictCFG":
        if 'label' in obj:
            raw_v = obj.pop('label')
            if isinstance(raw_v, int):
                self.label = float(raw_v)
            elif isinstance(raw_v, float):
                self.label = raw_v
        if 'alpha' in obj:
            raw_v = obj.pop('alpha')
            if isinstance(raw_v, float):
                self.alpha = int(raw_v)
            elif isinstance(raw_v, int):
                self.alpha = raw_v
        super().from_obj(obj)
        return self


@dataclass
class BackGroundColor(DictCFG):
    """
    背景图颜色配置
    """
    script: Color = field(default_factory=Color)
    inbound: Color = field(default_factory=Color)
    outbound: Color = field(default_factory=Color)
    speed: Color = field(default_factory=Color)
    speedTitle: Color = field(default_factory=lambda: Color(value="#EAEAEA"))
    scriptTitle: Color = field(default_factory=lambda: Color(value="#EAEAEA"))
    topoTitle: Color = field(default_factory=lambda: Color(value="#EAEAEA"))


@dataclass
class ColorCFG(DictCFG):
    speed: List[Color] = field(default_factory=list)
    delay: List[Color] = field(default_factory=list)
    outColor: List[Color] = field(default_factory=list)
    yes: Color = field(default_factory=lambda: Color(value="#bee47e", end_color="#bee47e"))
    no: Color = field(default_factory=lambda: Color(value="#ee6b73", end_color="#ee6b73"))
    na: Color = field(default_factory=lambda: Color(value="#8d8b8e", end_color="#8d8b8e"))
    wait: Color = field(default_factory=lambda: Color(value="#dcc7e1", end_color="#dcc7e1"))
    ipriskLow: Color = field(default_factory=Color)
    ipriskMedium: Color = field(default_factory=Color)
    ipriskHigh: Color = field(default_factory=Color)
    ipriskVeryHigh: Color = field(default_factory=Color)
    warn: Color = field(default_factory=lambda: Color(value="#fcc43c", end_color="#fcc43c"))
    background: BackGroundColor = field(default_factory=lambda: BackGroundColor())

    def from_obj(self, obj: dict) -> "ColorCFG":
        def _temp(key: str, instance: BaseCFG):
            if key in obj:
                _raw_v = obj.pop(key)
                if isinstance(_raw_v, list):
                    self.from_list(key, _raw_v, instance)

        for k in ["speed", 'delay', 'outColor']:
            _temp(k, Color())

        super().from_obj(obj)
        return self


DEFAULT_SPEED_COLOR = [
    Color(0, "1", "#fae0e4"), Color(1, "2", "#f7cad0"), Color(10, "3", "#f9bec7"), Color(20, "4", "#ff85a1"),
    Color(50, "5", "#ff7096"), Color(80, "6", "#ff5c8a"), Color(100, "7", "#ff477e"),
]
DEFAULT_DELAY_COLOR = [
    Color(0, "1", "#8d8b8e"), Color(1, "2", "#e4f8f9"), Color(50, "3", "#e4f8f9"), Color(100, "4", "#bdedf1"),
    Color(200, "5", "#96e2e8"), Color(300, "6", "#78d5de"), Color(500, "7", "#67c2cf"), Color(1000, "8", "#61b2bd"),
    Color(2000, "9", "#466463"),
]


@dataclass
class WMCFG(DictCFG):
    """
    水印配置
    """
    enable: bool = False
    text: str = "只是一个水印"
    color: Color = field(default_factory=lambda: Color(value="#000000", alpha=16))
    alpha: int = 16
    size: int = 64
    angle: Union[float, int] = -16.0
    row_spacing: int = 1
    start_y: int = 0
    shadow: bool = False
    trace: bool = False

    def from_obj(self, obj: dict) -> "WMCFG":
        _temp = obj.pop('angle', None)
        if isinstance(_temp, (float, int)):
            self.angle = _temp
        super().from_obj(obj)
        return self


@dataclass
class EmojiCFG(DictCFG):
    enable: bool = True
    source: str = "TwemojiLocalSource"


class SpeedFormat(Enum):
    BYTE_BINARY = "byte/binary"
    BYTE_DECIMAL = "byte/decimal"
    BIT_BINARY = "bit/binary"
    BIT_DECIMAL = "bit/decimal"


@dataclass
class ImageCFG(DictCFG):
    title: str = "Koipy"
    speedFormat: str = SpeedFormat.BYTE_DECIMAL.value
    font: str = DEFAULT_FONT_PATH
    emoji: EmojiCFG = field(default_factory=lambda: EmojiCFG())
    speedEndColorSwitch: bool = False
    endColorsSwitch: bool = False
    compress: bool = False
    color: ColorCFG = field(default_factory=lambda: ColorCFG())
    watermark: WMCFG = field(default_factory=lambda: WMCFG())
    nonCommercialWatermark: WMCFG = field(default_factory=lambda: WMCFG(text="请勿用于商业用途"))


@dataclass
class EmojiCFG(DictCFG):
    enable: bool = True
    source: str = "TwemojiLocalSource"


@dataclass
class SlaveOption(DictCFG):
    pass


class MiaoSpeedBranch(Enum):
    Origin: int = 0
    MoShaoLi: int = Origin
    PMN: int = Origin
    FullTClash: int = 1


@dataclass
class MiaoSpeedOption(SlaveOption):
    downloadDuration: int = 8
    downloadThreading: int = 4
    pingAverageOver: int = 5
    taskRetry: int = 3
    downloadURL: str = DEFAULT_SPEEDFILE
    pingAddress: str = DEFAULT_PING_ADDRESS
    stunURL: str = "udp://stunserver2024.stunprotocol.org:3478"
    taskTimeout: int = 5000
    dnsServer: List[str] = field(default_factory=list)
    apiVersion: int = 1

    def from_obj(self, obj: dict) -> "MiaoSpeedOption":
        if "dnsServer" in obj:
            raw_v = obj.pop("dnsServer")
            if raw_v and isinstance(raw_v, list):
                self.dnsServer = [v for v in raw_v if isinstance(v, str)]
        super().from_obj(obj)
        return self


@dataclass
class Slave(DictCFG):
    id: str = None
    comment: str = ""
    hidden: bool = False
    token: str = None
    type: str = None
    address: str = None
    option: SlaveOption = field(default_factory=lambda: SlaveOption())


@dataclass
class BotSlave(Slave):
    type: str = "bot"
    username: str = None


@dataclass
class LocalSlave(Slave):
    id: str = "default"
    type: str = None
    username: str = "local"


@dataclass
class AiohttpWSSlave(Slave):
    type: str = "websocket"
    path: str = "/"


@dataclass
class MiaoSpeedSlave(Slave):
    type: str = "miaospeed"
    skipCertVerify: bool = True
    tls: bool = True
    invoker: str = None
    buildtoken: str = None
    path: str = None
    option: MiaoSpeedOption = field(default_factory=lambda: MiaoSpeedOption())


@dataclass
class SubInfoCFG(DictCFG):
    owner: int = None
    password: str = None
    url: str = None
    share: List[int] = field(default_factory=list)

    def from_obj(self, obj: dict) -> "SubInfoCFG":
        if "share" in obj:
            raw_v = obj.pop("share")
            self.share = [i for i in raw_v if isinstance(i, int)]
        super().from_obj(obj)
        return self


@dataclass
class UserbotCFG(DictCFG):
    enable: bool = False
    uid: int = None
    whitelist: List[int] = field(default_factory=list)

    def from_obj(self, obj: dict) -> "UserbotCFG":
        if "whitelist" in obj:
            raw_v = obj.pop("whitelist")
            self.whitelist = [i for i in raw_v if isinstance(i, int)]
        super().from_obj(obj)
        return self


class ScriptType:
    CPython: str = "cpython"
    GoJajs: str = "gojajs"
    GoBuiltin: str = "gofunc"


@dataclass
class Script(DictCFG):
    type: str = ScriptType.GoJajs
    name: str = ""
    rank: int = 0
    content: str = ""

    def resolve(self, path_or_content: str):
        if isinstance(path_or_content, str) and path_or_content:
            is_path = False
            try:
                is_path = pathlib.Path(path_or_content).exists()
            except (FileNotFoundError, RuntimeError, Exception):
                pass
            if is_path:
                try:
                    with open(path_or_content, 'r', encoding="utf-8") as fp:
                        self.content = fp.read()
                except Exception as e:
                    if logger:
                        logger.error(str(e))
                    else:
                        print(e)
                    self.content = ""
            else:
                self.content = path_or_content


SlaveType = TypeVar('SlaveType', bound='Slave')


@dataclass
class SlaveConfig(DictCFG):
    default: str = ""
    showID: bool = True
    slaves: List[SlaveType] = None

    def from_obj(self, obj: dict) -> "DictCFG":
        self.convert(obj)
        super().from_obj(obj)
        return self

    def convert(self, obj: dict):
        """
        转换基类到子类
        :param obj:
        :return:
        """
        if "slaves" in obj:
            self.slaves = []
            raw_v = obj.pop("slaves")
            if not isinstance(raw_v, list):
                return self
            for slave_c in raw_v:
                if not isinstance(slave_c, dict):
                    continue
                slave_type = slave_c.get("type", "")
                if slave_type == "miaospeed":
                    slave = MiaoSpeedSlave()
                    slave.from_obj(slave_c)
                    self.slaves.append(slave)
                elif slave_type == "fulltclash":
                    slave = AiohttpWSSlave()
                    slave.from_obj(slave_c)
                    self.slaves.append(slave)


@dataclass
class Rule(DictCFG):
    name: str = None
    url: str = None
    script: List[str] = field(default_factory=list)
    slaveid: str = None
    runtime: RuntimeCFG = None
    owner: int = None

    def from_obj(self, obj: dict) -> "Rule":
        if not isinstance(obj, dict):
            return self
        raw_v = obj.pop("script", None)
        if isinstance(raw_v, list):
            self.script = [v for v in raw_v if isinstance(v, str)]
        rt = obj.pop("runtime", None)
        if rt and isinstance(rt, dict):
            self.runtime = RuntimeCFG().null()
            self.runtime.from_obj(rt)
        super().from_obj(obj)
        return self

    def __str__(self):
        return (f"Rule.name: `{self.name}`\n"
                f"Rule.url: `{self.url}`\n"
                f"Rule.script: `{str(self.script)}`\n"
                f"Rule.slaveid: `{self.slaveid}`\n"
                f"Rule.runtime: `{str(self.runtime)}`\n"
                f"Rule.owner: `{self.owner}`")

    def invite_print(self):
        return (f"Rule.name: `{self.name}`\n"
                f"Rule.script: `{str(self.script)}`\n"
                f"Rule.slaveid: `{self.slaveid}`\n"
                f"Rule.runtime: `{str(self.runtime)}`\n")


@dataclass
class RuleList(list, ListCFG):
    def from_obj(self, obj: list) -> "RuleList":
        self.clear()
        # raw_v = obj.pop("rules", None)
        if isinstance(obj, list):
            self.extend(Rule().from_obj(v) for v in obj)
        return self

    def get(self, rulename: str):
        if not rulename:
            return None
        try:
            rule: Rule = next(filter(lambda r: r.name == rulename, self))
            if rule:
                return rule
            else:
                return None
        except StopIteration:
            return None


@dataclass
class TranslationCFG(DictCFG):
    lang: str = "zh_CN"
    resources: Dict[str, str] = field(default_factory=dict)

    def from_obj(self, obj: dict) -> "TranslationCFG":
        if "resources" in obj:
            raw_v = obj.pop("resources")
            if not isinstance(raw_v, dict):
                return self
            for k, v in raw_v.items():
                if not isinstance(v, str):
                    continue
                self.resources[k] = v
        super().from_obj(obj)
        return self


@dataclass
class ScriptCFG(DictCFG):
    scripts: List[Script] = field(default_factory=list)

    def from_obj(self, obj: dict) -> "ScriptCFG":
        if "scripts" in obj:
            raw_v = obj.pop("scripts")
            if isinstance(raw_v, list):
                self.from_list("scripts", raw_v, Script)
        self.scripts = sorted(self.scripts, key=lambda x: x.rank)
        super().from_obj(obj)
        return self


@dataclass
class NetworkCFG(DictCFG):
    socks5Proxy: str = None
    httpProxy: str = None
    userAgent: str = "ClashMetaForAndroid/2.8.9.Meta Mihomo/0.16"


class LogLevel:
    DISABLE: str = "DISABLE"
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"
    CRITICAL: str = "CRITICAL"

    @classmethod
    def is_valid_level(cls, level: str):
        return level in cls.get_levels()

    @classmethod
    def get_levels(cls):
        return [getattr(cls, attr) for attr in dir(cls) if not attr.startswith("__") and
                isinstance(getattr(cls, attr), str)]


@dataclass
class KoiConfig(DictCFG, ConfigManager):
    license: str = ""
    admin: AdminList = field(default_factory=AdminList)
    user: UserList = field(default_factory=UserList)
    network: NetworkCFG = field(default_factory=lambda: NetworkCFG())
    bot: BotCFG = field(default_factory=lambda: BotCFG())
    # core: CoreCFG = field(default_factory=lambda: FullTCoreCFG())
    subconverter: SubConverterCFG = field(default_factory=lambda: SubConverterCFG())
    runtime: RuntimeCFG = field(default_factory=lambda: RuntimeCFG())
    slaveConfig: SlaveConfig = field(default_factory=lambda: SlaveConfig())
    # userConfig: Dict[str, Any] = field(default_factory=lambda: {"rule": {}, "usageRanking": {}})
    # subinfo: Dict[str, SubInfoCFG] = field(default_factory=dict)
    translation: TranslationCFG = field(default_factory=lambda: TranslationCFG())
    scriptConfig: ScriptCFG = field(default_factory=lambda: ScriptCFG())
    # userbot: UserbotCFG = field(default_factory=lambda: UserbotCFG())
    image: ImageCFG = field(default_factory=lambda: ImageCFG())
    rules: RuleList = field(default_factory=lambda: RuleList())
    log_level: str = LogLevel.INFO
    _raw_config: dict = field(default_factory=dict)

    def from_obj(self, obj: dict) -> "KoiConfig":
        if not isinstance(obj, dict):
            return self
        # if "rules" in obj:
        #     raw_v = obj.pop("rules")
        #     if isinstance(raw_v, list):
        #         self.from_list("rules", raw_v, Rule)
        super().from_obj(obj)
        return self

    def from_file(self, path: Union[str, bytes, PathLike]) -> "KoiConfig":
        super().from_file(path)
        return self


@dataclass
class SystemCFG(DictCFG, ConfigManager):
    translation: Dict[str, Translation] = field(default_factory=dict)

    def from_obj(self, obj: dict) -> "SystemCFG":
        if not isinstance(obj, dict):
            return self
        super().from_obj(obj)
        return self

    def load_tr_config(self, obj: Dict[str, str], _class_or_instance: Union[Type[BaseCFG], BaseCFG]) -> "SystemCFG":
        if isinstance(_class_or_instance, Translation):
            trclass = _class_or_instance.__class__
        elif issubclass(_class_or_instance, Translation):
            trclass = _class_or_instance
        else:
            return self
        self.translation['zh_CN'] = Translation()
        if not isinstance(obj, dict):
            return self
        for k, v in obj.items():
            if not isinstance(k, str) or not isinstance(v, str):
                continue
            self.translation[k] = trclass().from_file(v)
        return self


if __name__ == "__main__":
    pass
