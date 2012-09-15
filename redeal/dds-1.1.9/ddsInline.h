#ifndef __DDS_INLINE_H__
#define __DDS_INLINE_H__

#include "ddsInterface.h"

/**
 * Repository for simple inline functions used by DDS
 */

inline int RelativeSeat(int seat, int relative) {
    return (seat + relative)&3;
}

inline int partner(int seat) {
    return (seat^2); /* slightly faster than calling RelativeSeat */
}

inline int lho(int seat) {
    return RelativeSeat(seat,1);
}

inline int rho(int seat) {
    return RelativeSeat(seat,3);
}

inline holding_t BitRank(int rank) {
    /*
     * Trick calculation
     * Equivalent to 1<<(rank-2) for rank>=2, and 0 for rank<2.
     */
    return (1<<rank)>>2;
}

template<class INT> inline INT smallestBitInInteger(INT value) {
    return value & (-value);
}

inline holding_t smallestRankInSuit(holding_t h) {
    return smallestBitInInteger<holding_t>(h);
}

inline int InvBitMapRank(holding_t bitMap) {

    switch (bitMap) {
    case 0x1000: return 14;
    case 0x0800: return 13;
    case 0x0400: return 12;
    case 0x0200: return 11;
    case 0x0100: return 10;
    case 0x0080: return 9;
    case 0x0040: return 8;
    case 0x0020: return 7;
    case 0x0010: return 6;
    case 0x0008: return 5;
    case 0x0004: return 4;
    case 0x0002: return 3;
    case 0x0001: return 2;
    default: return 0;
    }
}

inline int InvWinMask(int mask) {

    switch (mask) {
    case 0x01000000: return 1;
    case 0x00400000: return 2;
    case 0x00100000: return 3;
    case 0x00040000: return 4;
    case 0x00010000: return 5;
    case 0x00004000: return 6;
    case 0x00001000: return 7;
    case 0x00000400: return 8;
    case 0x00000100: return 9;
    case 0x00000040: return 10;
    case 0x00000010: return 11;
    case 0x00000004: return 12;
    case 0x00000001: return 13;
    default: return 0;
    }
}

#endif
