
#include <stdio.h>
#include <string.h>

extern struct rtpkt {
  int source;       /* id of sending router sending this pkt */
  int dest;         /* id of router to which pkt being sent 
                         (must be an immediate neighbor) */
  int mincost[4];    /* min cost to node 0 ... 3 */
};

extern int TRACE;
extern int YES;
extern int NO;
extern float clocktime;

/**
 * Constants and definitions
 */
#define INFINITY 999
#define NODE_ID 3  /* Current router's ID */

/**
 * Distance table structure - stores costs to each destination via each neighbor
 * First index [i] represents destination, second index [j] represents neighbor
 */
struct distance_table {
  int costs[4][4];
} dt3;

/**
 * Global variables for routing
 */
int costs3[4] = { 7, 999, 2, 0 };  /* Direct link costs to each node */
struct rtpkt outPackets3[4];             /* Prepared packets for each neighbor */
int bestCost3[4];                        /* Current best cost to each destination */


/**
 * Helper function: Finds minimum value in an array
 */
int Min3(int values[4]) {
    int min = INFINITY;
    for (int i = 0; i < 4; i++) {
        if (values[i] < min) {
            min = values[i];
        }
    }
    return min;
}

/**
 * Prints the distance table in a formatted way
 * Shows costs to each destination via each neighbor
 */
void printdt3(struct distance_table *dtptr) {
    printf("\n===== NODE %d DISTANCE TABLE =====\n", NODE_ID);
    printf("             via     \n");
    printf("   D3 |    0     2 \n");
    printf("  ----|-----------\n");
    printf("     0|  %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][2]);
    printf("dest 1|  %3d   %3d\n", dtptr->costs[1][0], dtptr->costs[1][2]);
    printf("     2|  %3d   %3d\n", dtptr->costs[2][0], dtptr->costs[2][2]);
    printf("================================\n");
}

/**
 * Prints the current minimum costs to all destinations
 */
void printcosts3() {
    printf("Node %d's minimum costs to other nodes: [%d %d %d %d]\n", 
           NODE_ID, bestCost3[0], bestCost3[1], bestCost3[2], bestCost3[3]);
}

/**
 * Recalculates the best cost to each destination
 * by finding the minimum cost across all neighbors
 */
void update_costs3() {
    /* For each destination, find minimum cost via any neighbor */
    for (int dest = 0; dest < 4; dest++) {
        bestCost3[dest] = INFINITY;
        for (int via = 0; via < 4; via++) {
            /* Skip node 1 which is not connected to node 3 */
            if (via != 1) {
                if (bestCost3[dest] > dt3.costs[dest][via]) {
                    bestCost3[dest] = dt3.costs[dest][via];
                }
            }
        }
    }
}

/**
 * Creates and sends routing update packets to all neighbors
 */
void broadcastUpdates3() {
    /* Prepare packets with current best costs */
    for (int neighID = 0; neighID < 4; neighID++) {
        outPackets3[neighID].source = NODE_ID;
        outPackets3[neighID].dest = neighID;
        memcpy(outPackets3[neighID].mincost, bestCost3, sizeof(bestCost3));
    }
    
    /* Send to all neighbors (except self and node 1 which is not connected) */
    for (int neighID = 0; neighID < 4; neighID++) {
        if (neighID != NODE_ID && neighID != 1 && costs3[neighID] < INFINITY) {
            tolayer2(outPackets3[neighID]);
            printf("TIME %.3f: Node %d sends update to node %d with costs [%d %d %d %d]\n",
                   clocktime, NODE_ID, neighID, 
                   bestCost3[0], bestCost3[1], bestCost3[2], bestCost3[3]);
        }
    }
}

/**
 * Checks if minimum costs have changed and broadcasts updates if needed
 */
void processAndBroadcast3() {
    /* Store previous costs */
    int previousCosts[4];
    memcpy(previousCosts, bestCost3, sizeof(bestCost3));
    
    /* Recalculate minimum costs */
    update_costs3();
    
    /* Check if any cost changed */
    int changed = 0;
    for (int i = 0; i < 4; i++) {
        if (previousCosts[i] != bestCost3[i]) {
            changed = 1;
            break;
        }
    }
    
    /* Send updates if costs changed */
    if (changed) {
        printf("\nNode %d: Routing costs updated, broadcasting changes.\n", NODE_ID);
        broadcastUpdates3();
    } else {
        printf("\nNode %d: No cost changes detected, no updates sent.\n", NODE_ID);
    }
}

/**
 * Initializes the router
 * Sets up distance table and broadcasts initial costs
 */
void rtinit3() {
    printf("\n==== INITIALIZING NODE %d at time %.3f ====\n", NODE_ID, clocktime);
    
    /* Initialize distance table with direct costs */
    for (int dest = 0; dest < 4; dest++) {
        for (int via = 0; via < 4; via++) {
            if (dest == via) {
                /* Direct link costs */
                dt3.costs[dest][via] = costs3[dest];
            } else {
                /* Unknown routes set to infinity */
                dt3.costs[dest][via] = INFINITY;
            }
        }
    }
    
    /* Display initial distance table */
    printdt3(&dt3);
    
    /* Calculate initial minimum costs */
    update_costs3();
    
    /* Send initial routing updates to neighbors */
    broadcastUpdates3();
}

/**
 * Processes a received routing update
 * Updates distance table and broadcasts changes if needed
 */
void rtupdate3(struct rtpkt *rcvdpkt) {
    int sourceRouter = rcvdpkt->source;
    int receivedCosts[4];
    
    /* Extract costs from received packet */
    memcpy(receivedCosts, rcvdpkt->mincost, sizeof(receivedCosts));
    
    printf("\n==== NODE %d RECEIVED UPDATE at time %.3f ====\n", 
           NODE_ID, clocktime);
    printf("From node %d with costs: [%d %d %d %d]\n", 
           sourceRouter, receivedCosts[0], receivedCosts[1], 
           receivedCosts[2], receivedCosts[3]);
    
    /* Update distance table with new information */
    int tableChanged = 0;
    for (int dest = 0; dest < 4; dest++) {
        /* Calculate new cost via the source router */
        int newCost = dt3.costs[sourceRouter][sourceRouter] + receivedCosts[dest];
        
        /* Update if this cost is valid */
        if (newCost < INFINITY) {
            /* Check if value changes before updating */
            if (dt3.costs[dest][sourceRouter] != newCost) {
                tableChanged = 1;
            }
            dt3.costs[dest][sourceRouter] = newCost;
        } else {
            dt3.costs[dest][sourceRouter] = INFINITY;
        }
    }
    
    /* Print updated distance table */
    printdt3(&dt3);
    
    /* Process changes and broadcast if needed */
    if (tableChanged) {
        printf("Distance table updated based on information from node %d\n", sourceRouter);
    }
    processAndBroadcast3();
}

/**
 * Handles link cost changes
 * Updates distance table and broadcasts changes if needed
 */
void linkhandler3(int linkid, int newcost) {
    printf("\n==== LINK COST CHANGE at time %.3f ====\n", clocktime);
    printf("Link from Node %d to Node %d changed to %d\n", NODE_ID, linkid, newcost);
    
    /* Store the old direct cost */
    int oldDirectCost = costs3[linkid];
    costs3[linkid] = newcost;
    
    /* Calculate the cost difference */
    int costDifference = newcost - oldDirectCost;
    
    /* Update all routes through this link */
    for (int dest = 0; dest < 4; dest++) {
        if (dt3.costs[dest][linkid] < INFINITY) {
            dt3.costs[dest][linkid] += costDifference;
        }
    }
    
    /* Print updated distance table */
    printdt3(&dt3);
    
    /* Process changes and broadcast if needed */
    processAndBroadcast3();
}