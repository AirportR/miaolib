from dataclasses import field, dataclass

from .base import DictCFG
from .config import ImageCFG
from .task import SlaveRequest


@dataclass
class MatrixDrawCFG(DictCFG):
    matrixLine: int


@dataclass
class DrawFilter(DictCFG):
    include: str = ""
    exclude: str = ""


@dataclass
class DrawConfig:
    basedataNum: int = 0
    filter: DrawFilter = field(default_factory=lambda: DrawFilter())
    frontsize: int = 38
    linespace: int = 65
    xline_c: str = "#E1E1E1"
    yline_c: str = "#EAEAEA"
    timeused: str = "undefined"
    trafficused: int = 0
    sort: str = "undefined"
    slaveVersion: str = ""
    threadNum: int = 0
    lastIndexCompensation: int = 0
    ctofs: float = int(linespace / 2 - frontsize / 2)
    ftofs_y: float = 0  # 字体偏移
    speedBlockWidth: int = 20
    noFooter: bool = False
    noUnlockedStats: bool = False
    image: ImageCFG = field(default_factory=lambda: ImageCFG())
    slavereq: SlaveRequest = field(default_factory=lambda: SlaveRequest())
