#!/usr/bin/env python3
"""importlib 隔离加载工具。

email_pipeline 要同时用到 oa/ 和 report/ 两个子目录的脚本，二者都有同名模块
（read_email / db_query / us_deadline 等）。直接 import 会因 sys.modules 缓存
互相串味（先入者赢）。

本模块提供 `Pipeline` 上下文管理器：进入时把本子目录"拥有"的模块装回 sys.modules
（遮蔽另一子目录的同名模块，并保存被遮蔽者），并把目录放到 sys.path[0]；退出时
卸下、恢复现场。这样 oa/ 和 report/ 的代码（含函数内的延迟 import）始终解析到
自己目录的同名文件，互不干扰。

用法：
    oa  = Pipeline(".../scripts/oa")
    rpt = Pipeline(".../scripts/report")
    with rpt as RPT:                      # 进入 report 上下文
        emails, results = RPT.read_and_classify()
    with oa as OA:                        # 进入 oa 上下文
        OA.dispatch_oa(results)
"""
import os
import sys
import importlib


class Pipeline:
    """隔离加载某个子目录的 read_email 模块，并在其目录上下文中调用它。"""

    def __init__(self, dir_path, entry="read_email"):
        self.dir = os.path.abspath(dir_path)
        self.entry = entry
        self._mod = None          # 缓存的入口模块对象
        self.owned = {}           # 本目录拥有的模块：bare_name -> module
        self._saved = {}          # 进入时被遮蔽的同名模块，退出时还原

    def _capture_owned(self):
        """扫描 sys.modules，把 __file__ 落在本目录下的模块都记为自己拥有。
        覆盖延迟 import（函数体里 import 的 us_deadline / oainfo_cli 等）。"""
        prefix = self.dir + os.sep
        for name, mod in list(sys.modules.items()):
            f = getattr(mod, "__file__", None)
            if f and os.path.abspath(f).startswith(prefix):
                self.owned[name] = mod

    def __enter__(self):
        # 1) 用本目录拥有的模块遮蔽 sys.modules 中的同名项（保存被遮蔽者）
        self._saved = {}
        for name, mod in self.owned.items():
            if name in sys.modules and sys.modules[name] is not mod:
                self._saved[name] = sys.modules[name]
            sys.modules[name] = mod
        # 2) 目录放到搜索路径最前，保证裸 import 解析到本目录
        sys.path.insert(0, self.dir)
        # 3) 首次进入时真正加载入口模块
        if self._mod is None:
            # 确保入口名没有被别的目录缓存占用
            stale = sys.modules.pop(self.entry, None)
            self._mod = importlib.import_module(self.entry)
            if stale is not None and self.entry not in self._saved:
                self._saved[self.entry] = stale
            self._capture_owned()
        return self._mod

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 捕获本次上下文里新产生的延迟 import，纳入 owned，供下次进入复用
        self._capture_owned()
        # 撤掉路径
        try:
            sys.path.remove(self.dir)
        except ValueError:
            pass
        # 卸下本目录模块，还原被遮蔽的同名项
        for name in list(self.owned):
            if sys.modules.get(name) is self.owned[name]:
                sys.modules.pop(name, None)
        sys.modules.update(self._saved)
        self._saved = {}
        return False  # 不吞异常
