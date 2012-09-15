/*
 * Broken out from dds.h
 * This file is the essential external "C" face to the dds.cpp file
 */
#ifndef __DDSINTERFACE_H__
#define __DDSINTERFACE_H__

#if 0
#define BENCH
#endif

#if defined(_WIN32)
#    define DLLEXPORT __declspec(dllexport)
#    define STDCALL __stdcall
#else
#if !defined(DLLEXPORT)
#    define DLLEXPORT
#endif
#    define STDCALL
#    define INT8 char
#endif

#ifdef __cplusplus
#    define EXTERN_C extern "C"
#else
#    define EXTERN_C
#endif

typedef unsigned short int holding_t;


struct diagram {
    holding_t cards[4][4];
};

struct deal {
    int trump;
    int first;
    int currentTrickSuit[3];
    int currentTrickRank[3];
    struct diagram remaining;
};

struct futureTricks {
    int nodes;
#ifdef BENCH
    int totalNodes;
#endif
    int cards;
    int suit[13];
    int rank[13];
    int equals[13];
    int score[13];
};

#include <string.h>

EXTERN_C int SolveBoard(struct deal dl, 
                        int target, int solutions, int mode, struct futureTricks *futp);

EXTERN_C void DDSInitStart();

EXTERN_C holding_t distinctUnplayedCards(holding_t origHolding, holding_t played,holding_t *sequence);
#endif

