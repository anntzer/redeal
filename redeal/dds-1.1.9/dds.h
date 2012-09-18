/* POrtability-macros header prefix */
#ifndef __DDS_H__
#define __DDS_H__
#ifdef __cplusplus
#include <iostream>
using namespace std;
#endif

#include "ddsInterface.h"
#include "ddsInline.h"
#include "ddsLookup.h"
#include "Holding.h"

#define LONGLONG long long

/* end of portability-macros section */

/*#define BENCH*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/*#define STAT*/	/* Define STAT to generate a statistics log, stat.txt */
/*#define TTDEBUG*/     /* Define TTDEBUG to generate transposition table debug information */
/*#define CANCEL*/    /* Define CANCEL to get support for cancelling ongoing search */

#ifdef  TTDEBUG
#define SEARCHSIZE  20000
#else
#define SEARCHSIZE  1
#endif

#define CANCELCHECK  200000

#if defined(INFINITY)
#    undef INFINITY
#endif
#define INFINITY    32000

#define MAXNODE     1
#define MINNODE     0

#define TRUE        1
#define FALSE       0

#define MOVESVALID  1
#define MOVESLOCKED 2

#define NSIZE	100000
#define WSIZE   100000
#define LSIZE   20000
#define NINIT	2*250000/*400000*/
#define WINIT	2*700000/*1000000*/
#define LINIT	2*50000

#define Max(x, y) (((x) >= (y)) ? (x) : (y))
#define Min(x, y) (((x) <= (y)) ? (x) : (y))


struct relRanksType {
    int aggrRanks;
    int winMask;
};

class RelativeRanksFinder {
 protected:
    struct {
        relRanksType suits[4];
    } relative[8192];

    struct diagram originalsBySuitFirst;

 public:
    inline RelativeRanksFinder() {
        for (int suit=0; suit<4; suit++) {
            for (int seat=0; seat<4; seat++) {
                originalsBySuitFirst.cards[suit][seat]=0;
            }
        }
    }

    inline const struct relRanksType &operator ()(int suit,holding_t index) const {
        return relative[index&8191].suits[suit];
    }

    inline void initialize(const struct diagram &diagram) {
        int newDiagram = 0;
        int seat, suit;

        for (suit=0; suit<4; suit++) {
            for (seat=0; seat<4; seat++) {
                if (diagram.cards[seat][suit] != originalsBySuitFirst.cards[suit][seat]) {
                    newDiagram = 1;
                }
                originalsBySuitFirst.cards[suit][seat]=diagram.cards[seat][suit];
            }
        }

        if (newDiagram) {
            holding_t topBitRank = 1;
            for (int suit=0; suit<4; suit++) {
                relative[0].suits[suit].aggrRanks = 0;
                relative[0].suits[suit].winMask   = 0;
            }

            for (int ind=1; ind<8192; ind++) {
                if (ind&(topBitRank<<1)) {
                    topBitRank <<= 1;
                }
                compute(ind, topBitRank);
            }
        }
    }

 protected:
    inline void compute(const holding_t ind,const holding_t topBitRank) {
        int seat, suit;
    
        relative[ind] = relative[ind^topBitRank];

        for (suit=0; suit<=3; suit++) {
            struct relRanksType &relRanks = relative[ind].suits[suit];

            for (seat=0; seat<=3; seat++) {
                if (originalsBySuitFirst.cards[suit][seat] & topBitRank) {
                    relRanks.aggrRanks = (relRanks.aggrRanks >> 2) | (seat << 24);
                    relRanks.winMask   = (relRanks.winMask >> 2)   | (3   << 24);
                    break;
                }
            }
        }
    }

};

extern const RelativeRanksFinder &rel;

struct gameInfo  {          /* All info of a particular deal */
    int vulnerable;
    int declarer;
    int contract;
    int leadSeat;
    int leadSuit;
    int leadRank;
    int first;
    int noOfCards;
    struct diagram diagram;
    /* 1st index is seat id, 2nd index is suit id */
};

struct moveType {
    unsigned char suit;
    unsigned char rank;
    holding_t sequence;          /* Whether or not this move is
                                    the first in a sequence */
    short int weight;                     /* Weight used at sorting */

    inline moveType() {
        suit=0;
        rank=0;
        sequence=0;
        weight=0;
    }
};

struct movePlyType {
    struct moveType move[14];             
    int current;
    int last;
};

struct highCardType {
    int rank;
    int seat;
};

struct makeType {
    holding_t winRanks[4];
};

struct nodeCardsType {
    char ubound;	/* ubound and
                           lbound for the N-S side */
    char lbound;
    char bestMoveSuit;
    char bestMoveRank;
    char leastWin[4];
};

struct posStackItem {
    int first;                 /* Seat that leads the trick for each ply*/
    int high;                  /* Seat that is presently winning the trick */
    struct moveType move;      /* Presently winning move */              
    holding_t winRanks[4];  /* Cards that win by rank, index by suit */
};

struct pos {
    struct posStackItem stack[50];
    struct diagram diagram;   /* 1st index is seat, 2nd index is
                                 suit id */
    int orderSet[4];
    int winOrderSet[4];
    int winMask[4];
    int leastWin[4];
    holding_t removedRanks[4];    /* Ranks removed from board,
                                     index is suit */
    unsigned char length[4][4];
    holding_t aggregate[4];
    char ubound;
    char lbound;
    char bestMoveSuit;
    char bestMoveRank;
    int seatRelFirst;              /* The current seat, relative first seat */
    int tricksMAX;                 /* Aggregated tricks won by MAX */
    struct highCardType winner[4]; /* Winning rank of the trick,
                                      index is suit id. */
    struct highCardType secondBest[4]; /* Second best rank, index is suit id. */

    inline void removeBitRank(int suit,holding_t bitRank) {
        removedRanks[suit] |= bitRank;
    }

    inline void removeRank(int suit,int rank) {
        removeBitRank(suit,BitRank(rank));
    }

    inline void restoreBitRank(int suit, holding_t bitRank) {
        removedRanks[suit] &= (~bitRank);
    }

    inline void restoreRank(int suit,int rank) {
        restoreBitRank(suit,BitRank(rank));
    }

    inline int isRemovedBitRank(int suit, holding_t bitRank) const {
        return (removedRanks[suit] & bitRank);
    }

    inline int isRemoved(int suit, int rank) const {
        return isRemovedBitRank(suit,BitRank(rank));
    }

    inline int hasCardBitRank(int seat, int suit, holding_t bitRank) const {
        return (diagram.cards[seat][suit] & bitRank);
    }

    inline int hasCard(int seat,int suit, int rank) const {
        return hasCardBitRank(seat,suit,BitRank(rank));
    }

    inline void getSuitLengths(LONGLONG &lengths,int relSeat = 0) const {
        int seat, suit;
        lengths = 0;
        for (suit=0; suit<=2; suit++) {
            for (seat=0; seat<=3; seat++) {
                lengths = lengths << 4;
                lengths |= length[(relSeat+seat)%4][suit];
            }
        }
    }

    inline void computeOrderSet() {
        for (int suit=0; suit<4; suit++) {
            holding_t aggr = 0;
            for (int seat=0; seat<4; seat++) {
                aggr |= diagram.cards[seat][suit];
            }
            aggregate[suit] = aggr;
            orderSet[suit] = rel(suit,aggr).aggrRanks;
        }
    }

    inline void computeWinData(int suit, holding_t winners) {
        holding_t aggr = 0;
        holding_t w = smallestRankInSuit(winners);
        int seat, wm;
        for (seat=0; seat<4; seat++) {
            aggr |= (diagram.cards[seat][suit] & (-w));
        }

        winMask[suit] = rel(suit,aggr).winMask;
        winOrderSet[suit] = rel(suit,aggr).aggrRanks;

        wm = smallestBitInInteger(winMask[suit]);
        leastWin[suit] = InvWinMask(wm);

    }

    inline void winAdapt(const int depth, const struct nodeCardsType *cp, const holding_t aggr[]) {
        int ss;
        for (ss=0; ss<=3; ss++) {
            stack[depth].winRanks[ss] = getTopCards(aggr[ss],(int)cp->leastWin[ss]);
        }
    
    }

};

struct posSearchType {
    struct winCardType * posSearchPoint; 
    LONGLONG suitLengths;
    struct posSearchType * left;
    struct posSearchType * right;
};


struct winCardType {
    int orderSet;
    int winMask;
    struct nodeCardsType * first;
    struct winCardType * prevWin;
    struct winCardType * nextWin;
    struct winCardType * next;
}; 


struct evalType {
    int tricks;
    unsigned short int winRanks[4];
};

struct ttStoreType {
    struct nodeCardsType * cardsP;
    char tricksLeft;
    char target;
    char ubound;
    char lbound;
    unsigned char first;
    unsigned short int suit[4][4];
};

struct ContractInfo {
    const static int nextSuitArray[4][4];
    int trumpContract;
    int trump;
    int _firstSuit;
    const int *_nextSuit;
  

    inline void initialize(int trumpContract,int trump) {
        this->trumpContract = trumpContract;
        this->trump = trump;
        if (!trumpContract ) {
            _firstSuit = 0;
            _nextSuit = nextSuitArray[0];
        } else {
            _firstSuit = trump;
            _nextSuit = nextSuitArray[trump];
        }

    }

    inline ContractInfo() {
        initialize(0,-1);
    }

    inline ContractInfo(const ContractInfo &contract) {
        trumpContract = contract.trumpContract;
        trump         = contract.trump;
        _firstSuit     = contract._firstSuit;
        _nextSuit      = contract._nextSuit;
    }

    inline int isTrump(int suit) const {
        return (trumpContract && (trump==suit));
    }

    inline int notTrumpWithTrump(int suit) const {
        return (trumpContract && (trump!=suit));
    }

    inline int firstSuit() const {
        return _firstSuit;
    }

    inline int nextSuit(int suit) const {
        return _nextSuit[suit];
    }

    inline int betterMove(const struct moveType &nextMove,const struct moveType &bestMove) const {
        if (bestMove.suit==nextMove.suit) {
            if (nextMove.rank>bestMove.rank) {
                return TRUE;
            } else {
                return FALSE;
            }
        } else if (isTrump(nextMove.suit)) {
            return TRUE;
        } else {
            return FALSE;
        }
    }

};

struct GLOBALS {
protected:
public:
    ContractInfo _contract;
    RelativeRanksFinder rel;

    inline void setContract(int trump=-1) {
        _contract.initialize(trump>=0 && trump<=3,trump);
    }

    inline const ContractInfo &getContract() const {
        return _contract;
    }

};

extern struct gameInfo game;
extern struct gameInfo * gameStore;
extern struct ttStoreType * ttStore;
extern struct nodeCardsType * nodeCards;
extern struct winCardType * winCards;
extern struct pos lookAheadPos;
/* extern struct moveType move[13]; */
extern struct movePlyType movePly[50];
extern struct posSearchType * posSearch;
extern struct searchType searchData;
extern struct moveType forbiddenMoves[14];  /* Initial depth moves that will be 
					       excluded from the search */
extern struct moveType initialMoves[4];
extern struct moveType highMove;
extern struct moveType * bestMove;
extern struct winCardType **pw;
extern struct nodeCardsType **pn;
extern struct posSearchType **pl;


extern holding_t iniRemovedRanks[4];
extern holding_t relRankInSuit[4][4];
extern int sum;
extern int score1Counts[50], score0Counts[50];
extern int c1[50], c2[50], c3[50], c4[50], c5[50], c6[50], c7[50],
    c8[50], c9[50];
extern int nodeTypeStore[4];            /* Look-up table for determining if
                                           node is MAXNODE or MINNODE */
#if 0
extern int lho[4], rho[4], partner[4];                                        
#endif
extern int nodes;                       /* Number of nodes searched */
extern int no[50];                      /* Number of nodes searched on each
                                           depth level */
extern int payOff;
extern int iniDepth;
extern int treeDepth;
extern int tricksTarget;                /* No of tricks for MAX in order to
                                           meet the game goal, e.g. to make the
                                           contract */
extern int tricksTargetOpp;             /* Target no of tricks for MAX
                                           opponent */
extern int targetNS;
extern int targetEW;
extern int seatToPlay;
extern int nodeSetSize;
extern int winSetSize;
extern int lenSetSize;
extern int lastTTstore;
extern int searchTraceFlag;
extern int countMax;
extern int depthCount;
extern int highSeat;
extern int nodeSetSizeLimit;
extern int winSetSizeLimit;
extern int lenSetSizeLimit;
extern int estTricks[4];
extern int recInd; 
extern int suppressTTlog;
extern unsigned char suitChar[4];
extern unsigned char rankChar[15];
extern unsigned char seatChar[4];
extern int cancelOrdered;
extern int cancelStarted;
extern int threshold;
extern unsigned char cardRank[15], cardSuit[5], cardSeat[4];

extern FILE * fp2, *fp7, *fp11;
/* Pointers to logs */

void InitStart(void);
void InitGame(int gameNo, int moveTreeFlag, int first, int seatRelFirst,struct pos &position);
void InitSearch(struct pos * posPoint, int depth,
                struct moveType startMoves[], int first, int mtd);
int ABsearch(struct pos * posPoint, int target, int depth);
struct makeType Make(struct pos * posPoint, int depth);
int MoveGen(const struct pos * posPoint, int depth);
void InsertSort(int n, int depth);
void UpdateWinner(struct pos * posPoint, int suit);
void UpdateSecondBest(struct pos * posPoint, int suit);
inline int WinningMove(const struct moveType &mvp1,const struct moveType &mvp2);
inline unsigned short int CountOnes(unsigned short int b);
int AdjustMoveList(void);
int QuickTricks(struct pos * posPoint, int seat, 
                int depth, int target, int *result);
int LaterTricksMIN(struct pos *posPoint, int seat, int depth, int target); 
int LaterTricksMAX(struct pos *posPoint, int seat, int depth, int target);
struct nodeCardsType * CheckSOP(struct pos * posPoint, struct nodeCardsType
                                * nodep, int target, int tricks, int * result, int *value);
struct nodeCardsType * UpdateSOP(struct pos * posPoint, struct nodeCardsType
                                 * nodep);  
struct nodeCardsType * FindSOP(struct pos * posPoint,
                               struct winCardType * nodeP, int firstSeat, 
                               int target, int tricks, int * valp);  
struct nodeCardsType * BuildPath(struct pos * posPoint, 
                                 struct posSearchType *nodep, int * result);
void BuildSOP(struct pos * posPoint, int tricks, int firstSeat, int target,
              int depth, int scoreFlag, int score);
struct posSearchType * SearchLenAndInsert(struct posSearchType
                                          * rootp, LONGLONG key, int insertNode, int *result);  
void Undo(struct pos * posPoint, int depth);
int CheckDeal(struct moveType * cardp);
inline int InvBitMapRank(holding_t bitMap);
int InvWinMask(int mask);
void ReceiveTTstore(struct pos *posPoint, struct nodeCardsType * cardsP, int target, int depth);
int NextMove(struct pos *posPoint, int depth); 
int DumpInput(int errCode, struct deal dl, int target, int solutions, int mode); 
void Wipe(void);
void AddNodeSet(void);
void AddLenSet(void);
void AddWinSet(void);
#endif
