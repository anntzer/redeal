#include <cstdlib>
  #include <cstdio>
#include "ddsInline.h"
#ifndef __DDS_LOOKUP_H__
#define __DDS_LOOKUP_H__
/*
 * This header defines some inline functions which do global lookups for DDS
 * These functions are:
 *
 *  CountOnes(holding_t) - counts the cards in a holding
 *
 *  getHighestRank(holding_t) - returns the rank (2-14) of the highest
 *     card in the holding
 *
 *  getTopCards(holding_t h,int n) - returns a holding consisting of the top n cards
 *     in holding h   
 *
 * Your application must call initializeDDSLookup() to use these lookup tables
 */

/*
  struct topCardsType {
  holding_t topCards[14];
  };
*/

/* In dds code, counttable is local, but since I've already got a counttable in
   Deal, I reference that table instead */
//extern "C" unsigned short int counttable[];

// Copied back from source of v1.1.12.  Antony Lee
extern unsigned short int counttable[8192];
// End of insert.  Antony Lee

extern int highestRankLookup[8192];

extern holding_t topCardsLookup[14][8192];

inline unsigned short int CountOnes(holding_t holding) {
    return counttable[holding];
}

inline int getHighestRank(holding_t holding) {
    return highestRankLookup[holding];
}

inline holding_t getTopCards(holding_t holding, int count) {
    return topCardsLookup[count][holding];
}

inline void initializeDDSLookup() {
    // Copied back from source of v1.1.12.  Antony Lee
    /* The use of the counttable to give the number of bits set to
    one in an integer follows an implementation by Thomas Andrews. */
    int i, j;
    for (i=0; i<8192; i++) {	
        counttable[i]=0;
        for (j=0; j<13; j++) {
            if (i & (1<<j)) {counttable[i]++;}
        }
    }
    // End of insert.  Antony Lee

    int n,rank;
    holding_t holding;
    highestRankLookup[0] = 0;
    for (n=0; n<14; n++) { topCardsLookup[n][0] = 0; }

    for (rank=2; rank<=14; rank++) {
        holding_t highestBitRank = BitRank(rank);
        for (holding=highestBitRank; holding<2*highestBitRank; holding++) {
            highestRankLookup[holding] = rank;
            holding_t rest = holding & (~highestBitRank);
            topCardsLookup[0][holding] = 0;
            for (n=1; n<14; n++) {
                topCardsLookup[n][holding] = 
                    highestBitRank | topCardsLookup[n-1][rest];
            }
        }
    }
}

#endif
