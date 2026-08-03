#!/usr/bin/env python3
"""公布/公告文件定位测试：在临时目录搭假树验证 find_publication_file。不连网络。
  cd scripts/oa && python3 test_publication_file.py
"""
import os
import sys
import shutil
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from oainfo_cli import find_publication_file

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _touch(base, *parts):
    path = os.path.join(base, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("x")
    return path


def main():
    base = tempfile.mkdtemp(prefix="pubtest_")
    try:
        # 列出客户(韶音) US：文件名大写 Publication
        us_pub = _touch(base, "20608-韶音", "20608-0010", "20608-0010US00", "2.官方文件",
                        "20608-0010US00-Publication.pdf")
        _touch(base, "20608-韶音", "20608-0010", "20608-0010US00", "2.官方文件", "官方文件.pdf")
        # 其他客户(Amica) CN：多一层「其他客户」，关键词=公告文件
        cn_pub = _touch(base, "其他客户", "20243-Amica", "20243-0005", "20243-0005CN00", "2.官方文件",
                        "20243-0005CN00-公告文件.pdf")
        # 其他客户 CN 里额外放一个 publication.pdf（CN 应按公告文件匹配，不该命中它）
        _touch(base, "其他客户", "20243-Amica", "20243-0005", "20243-0005CN00", "2.官方文件",
               "somepublication.pdf")

        ok(find_publication_file("20608-0010US00", "US", base_dir=base) == us_pub,
           "列出客户 US → 找到 Publication(大小写不限)")
        ok(find_publication_file("20608-0010EP00", "EP", base_dir=base) is None,
           "EP 同结构但无该案目录 → None")
        ok(find_publication_file("20243-0005CN00", "CN", base_dir=base) == cn_pub,
           "其他客户 CN → 其他客户\\ 下按公告文件命中")

        # CN 关键词不匹配 publication
        _touch(base, "20618-联影", "20618-0001", "20618-0001CN00", "2.官方文件", "publication.pdf")
        ok(find_publication_file("20618-0001CN00", "CN", base_dir=base) is None,
           "CN 只认公告文件，publication.pdf 不命中")

        # 无公布文件
        _touch(base, "20633-大华", "20633-0001", "20633-0001US00", "2.官方文件", "只有官文.pdf")
        ok(find_publication_file("20633-0001US00", "US", base_dir=base) is None,
           "目录里无 publication 文件 → None")

        # 非 PDF 的 publication 文件被忽略
        _touch(base, "20615-滴滴", "20615-0001", "20615-0001US00", "2.官方文件", "publication.docx")
        ok(find_publication_file("20615-0001US00", "US", base_dir=base) is None,
           "publication.docx(非PDF) → 忽略")

        # 多份取字典序第一
        _touch(base, "20735-蚂蚁金服", "20735-0001", "20735-0001US00", "2.官方文件", "b-publication.pdf")
        first = _touch(base, "20735-蚂蚁金服", "20735-0001", "20735-0001US00", "2.官方文件", "a-publication.pdf")
        ok(find_publication_file("20735-0001US00", "US", base_dir=base) == first,
           "多份 → 取字典序第一(a-)")

        # 官方文件目录名变体：2官方文件（无点）
        v1 = _touch(base, "20608-韶音", "20608-0020", "20608-0020US00", "2官方文件",
                    "Publication.pdf")
        ok(find_publication_file("20608-0020US00", "US", base_dir=base) == v1,
           "目录名 2官方文件(无点) 也命中")
        # 官方文件目录名变体：直接「官方文件」
        v2 = _touch(base, "20608-韶音", "20608-0021", "20608-0021US00", "官方文件",
                    "Publication.pdf")
        ok(find_publication_file("20608-0021US00", "US", base_dir=base) == v2,
           "目录名 官方文件(无前缀) 也命中")

        # 案号过短
        ok(find_publication_file("2060", "US", base_dir=base) is None, "案号过短 → None")
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()
    print(f"\n全部通过：{_passed} 项断言")
