/*
 * rdseed.c — CPU の RDSEED 命令でハードウェアエントロピーを取り出す。
 *   コンパイル(FreeBSD/clang, Linux/gcc 共通):
 *     cc -O2 -mrdseed -shared -fPIC -o librdseed.so rdseed.c
 *   RDSEED 対応 CPU が必要(Intel Broadwell 以降 / AMD Zen 以降)。
 */
#include <immintrin.h>
#include <stdint.h>

/* 成功で1、エントロピー未準備で0(=要リトライ)を返す。 */
int rdseed64(uint64_t *out){
    return _rdseed64_step((unsigned long long *)out);
}
