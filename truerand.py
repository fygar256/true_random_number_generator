#!/usr/bin/env python3
#
# truerand.py
#   CPU の RDSEED 命令から直接ハードウェアエントロピーを引く真性乱数モジュール。
#   /dev/random(Fortuna)を経由せず、1バイトごとにエントロピー源から新規取得する。
#   要: RDSEED 対応 CPU と、同じディレクトリにコンパイル済みの librdseed.so。
#     cc -O2 -mrdseed -shared -fPIC -o librdseed.so rdseed.c
#
import os
import ctypes

# --- RDSEED スタブの読み込み ---------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_lib  = ctypes.CDLL(os.path.join(_here, "librdseed.so"))
_lib.rdseed64.argtypes = [ctypes.POINTER(ctypes.c_uint64)]
_lib.rdseed64.restype  = ctypes.c_int

_RDSEED_RETRY = 1000   # RDSEED は一時的に失敗しうるのでリトライ上限を設ける

def _rdseed64():
    """RDSEED で 64bit のハードウェアエントロピーを1個取得して返す。"""
    v = ctypes.c_uint64()
    for _ in range(_RDSEED_RETRY):
        if _lib.rdseed64(ctypes.byref(v)):
            return v.value
    raise RuntimeError("RDSEED が連続失敗しました(ハードウェアエントロピー枯渇?)")

# n byte の RAND_MAX を返す
def rand_max(n):
    v = 0
    for _ in range(n):
        v = v*256 + 0xff
    return v

# n byte の真性乱数(正の整数)を返す。1バイトごとに RDSEED から新規取得。
def rand(n):
    r = 0
    for _ in range(n):
        b = _rdseed64() & 0xff      # 一々エントロピー源から引く
        r = r*256 + b
    return r

# [0,1] の実数乱数(割り算のため厳密には真性乱数ではない)
def rand_f(n):
    return rand(n) / rand_max(n)

# 0〜k-1 の整数乱数(剰余のため厳密には真性乱数ではない)
def randomint(k, n):
    return rand(n) % k

if __name__ == "__main__":
    b = 8
    times = 20
    print(f"{b*8}bit正の真性整数乱数")
    for _ in range(times):
        print(rand(b), end=" ")
    print("\n実数[0,1]の範囲の実数乱数")
    for _ in range(times):
        print(rand_f(b), end=" ")
    print("\n整数0〜99の乱数")
    for _ in range(times):
        print(randomint(100, b), end=" ")
    print("")
