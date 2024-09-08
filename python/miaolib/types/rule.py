#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: www
@Date: 2024/7/25 下午1:33
@Description: 
"""
from dataclasses import field, dataclass
from typing import List

from .base import DictCFG
from .config import SortType, Script


@dataclass
class Rule(DictCFG):
    name: str = ""
    enable: bool = False
    script: List[Script] = field(default_factory=list)
    slaveid: str = "local"
    sort: str = SortType.ORIGIN
