#!/usr/bin/env python

from base64 import b64encode


def to_base64(data: str):
    bd = data.encode("ascii")
    b64 = b64encode(bd)
    return b64.decode("ascii")
