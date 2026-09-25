#ifndef C3X_P31_SEMANTIC_INC
#define C3X_P31_SEMANTIC_INC

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" uint64_t c3x_p31_tt_seq(void);
#else
uint64_t c3x_p31_tt_seq(void);
#endif

enum {
  C3X_P31_CUTOFF=0,
  C3X_P31_MOVE=1,
  C3X_P31_EVAL=2,
  C3X_P31_VALUE_EVAL=3,
  C3X_P31_PV=4,
  C3X_P31_NCLASS=5
};

static FILE *c3x_p31_f=NULL;
static unsigned long long c3x_p31_count[C3X_P31_NCLASS]={0};
static unsigned long long c3x_p31_witness=0;
static int c3x_p31_init=0;
static int c3x_p31_mask_bits=0;

static void c3x_p31_flush(void){
  if(!c3x_p31_f)return;
  fprintf(c3x_p31_f,"Z,%llu,%llu,%llu,%llu,%llu\n",
    c3x_p31_count[C3X_P31_CUTOFF],c3x_p31_count[C3X_P31_MOVE],
    c3x_p31_count[C3X_P31_EVAL],c3x_p31_count[C3X_P31_VALUE_EVAL],
    c3x_p31_count[C3X_P31_PV]);
  fflush(c3x_p31_f);
}

static void c3x_p31_setup(void){
  if(c3x_p31_init)return;
  c3x_p31_init=1;
  const char *m=getenv("C3X_TT_USE_MODE");
  if(!m||!*m||!strcmp(m,"BASE"))c3x_p31_mask_bits=0;
  else if(!strcmp(m,"NO_CUTOFF"))c3x_p31_mask_bits=1;
  else if(!strcmp(m,"NO_MOVE"))c3x_p31_mask_bits=2;
  else if(!strcmp(m,"NO_EVAL"))c3x_p31_mask_bits=4;
  else if(!strcmp(m,"NO_CUTOFF_MOVE"))c3x_p31_mask_bits=3;
  else if(!strcmp(m,"NO_CUTOFF_EVAL"))c3x_p31_mask_bits=5;
  else if(!strcmp(m,"NO_MOVE_EVAL"))c3x_p31_mask_bits=6;
  else if(!strcmp(m,"NO_ALL"))c3x_p31_mask_bits=7;
  else {fprintf(stderr,"C3X_P31_BAD_MODE %s\n",m);abort();}
  const char *p=getenv("C3X_TT_USE_TRACE");
  if(p&&*p){
    c3x_p31_f=fopen(p,"w");
    if(!c3x_p31_f){perror("C3X_TT_USE_TRACE");abort();}
    setvbuf(c3x_p31_f,NULL,_IOLBF,0);
    atexit(c3x_p31_flush);
  }
}

static int c3x_p31_measurement(void){
  c3x_p31_setup();
  return c3x_p31_tt_seq()==5ULL;
}
static int c3x_p31_no_cutoff(void){return c3x_p31_measurement()&&(c3x_p31_mask_bits&1);}
static int c3x_p31_no_move(void){return c3x_p31_measurement()&&(c3x_p31_mask_bits&2);}
static int c3x_p31_no_eval(void){return c3x_p31_measurement()&&(c3x_p31_mask_bits&4);}

static void c3x_p31_event(const char *scope,int cls,unsigned long long key,int ply,int depth,
                          int alpha,int beta,int ttval,int tteval,int bound,
                          unsigned long long move,long long payload){
  if(!c3x_p31_measurement())return;
  if(cls<0||cls>=C3X_P31_NCLASS)return;
  c3x_p31_count[cls]++;
  if(!c3x_p31_f||ply>4||c3x_p31_witness>=128)return;
  static const char *names[]={"CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL","PV_PROMOTION"};
  fprintf(c3x_p31_f,"U,%s,%s,%016llx,%d,%d,%d,%d,%d,%d,%d,%llu,%lld\n",
    scope,names[cls],key,ply,depth,alpha,beta,ttval,tteval,bound,move,payload);
  c3x_p31_witness++;
}
#endif
