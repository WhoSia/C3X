#ifndef C3X_P32_EVENT_TARGET_INC
#define C3X_P32_EVENT_TARGET_INC

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
  C3X_P32_CUTOFF=0,
  C3X_P32_MOVE=1,
  C3X_P32_EVAL=2,
  C3X_P32_VALUE_EVAL=3
};

typedef struct {
  char scope[12];
  int cls;
  unsigned long long key;
  int ply;
  int depth;
  unsigned long long move;
  int bound;
  long long payload;
  int occ;
  int seen;
  int fired;
} C3XP32Target;

static int c3x_p32_init=0;
static char c3x_p32_mode[24]="BASE";
static char c3x_p32_family[32]="NONE";
static int c3x_p32_frontier=8;
static C3XP32Target c3x_p32_targets[4096];
static int c3x_p32_ntarget=0;
static FILE *c3x_p32_f=NULL;
static unsigned long long c3x_p32_events=0,c3x_p32_blocked=0,c3x_p32_catalogued=0;

static const char* c3x_p32_cls_name(int cls){
  switch(cls){
    case C3X_P32_CUTOFF:return "CUTOFF";
    case C3X_P32_MOVE:return "MOVE_ORDER_SEED";
    case C3X_P32_EVAL:return "EVAL_REUSE";
    case C3X_P32_VALUE_EVAL:return "TT_VALUE_AS_EVAL";
    default:return "UNKNOWN";
  }
}
static int c3x_p32_family_has(int cls){
  if(!strcmp(c3x_p32_family,"CUTOFF")) return cls==C3X_P32_CUTOFF;
  if(!strcmp(c3x_p32_family,"MOVE_ORDER")) return cls==C3X_P32_MOVE;
  if(!strcmp(c3x_p32_family,"EVAL")) return cls==C3X_P32_EVAL||cls==C3X_P32_VALUE_EVAL;
  if(!strcmp(c3x_p32_family,"MOVE_ORDER+EVAL")) return cls==C3X_P32_MOVE||cls==C3X_P32_EVAL||cls==C3X_P32_VALUE_EVAL;
  return 0;
}
static void c3x_p32_flush(void){
  if(!c3x_p32_f)return;
  int fired=0;
  for(int i=0;i<c3x_p32_ntarget;i++) if(c3x_p32_targets[i].fired) fired++;
  fprintf(c3x_p32_f,"S,%llu,%llu,%llu,%d,%d\n",c3x_p32_events,c3x_p32_catalogued,c3x_p32_blocked,c3x_p32_ntarget,fired);
  for(int i=0;i<c3x_p32_ntarget;i++)
    fprintf(c3x_p32_f,"T,%d,%d,%d,%d\n",i,c3x_p32_targets[i].occ,c3x_p32_targets[i].seen,c3x_p32_targets[i].fired);
  fflush(c3x_p32_f);
}
static void c3x_p32_setup(void){
  if(c3x_p32_init)return;
  c3x_p32_init=1;
  const char *m=getenv("C3X_P32_MODE"); if(m&&*m) snprintf(c3x_p32_mode,sizeof(c3x_p32_mode),"%s",m);
  const char *fam=getenv("C3X_P32_FAMILY"); if(fam&&*fam) snprintf(c3x_p32_family,sizeof(c3x_p32_family),"%s",fam);
  const char *fr=getenv("C3X_P32_FRONTIER"); if(fr&&*fr)c3x_p32_frontier=atoi(fr);
  const char *tf=getenv("C3X_P32_TARGET_FILE");
  if(tf&&*tf){
    FILE *g=fopen(tf,"r");
    if(!g){perror("C3X_P32_TARGET_FILE");abort();}
    while(c3x_p32_ntarget<4096){
      C3XP32Target *t=&c3x_p32_targets[c3x_p32_ntarget];
      char keybuf[32]={0};
      int n=fscanf(g,"%11s\t%d\t%31s\t%d\t%d\t%llu\t%d\t%lld\t%d",
        t->scope,&t->cls,keybuf,&t->ply,&t->depth,&t->move,&t->bound,&t->payload,&t->occ);
      if(n==EOF)break;
      if(n!=9){fprintf(stderr,"C3X_P32_BAD_TARGET_LINE n=%d\n",n);abort();}
      t->key=strtoull(keybuf,NULL,16);t->seen=0;t->fired=0;c3x_p32_ntarget++;
    }
    fclose(g);
  }
  const char *tr=getenv("C3X_P32_TRACE");
  if(tr&&*tr){
    c3x_p32_f=fopen(tr,"w");
    if(!c3x_p32_f){perror("C3X_P32_TRACE");abort();}
    setvbuf(c3x_p32_f,NULL,_IOLBF,0);atexit(c3x_p32_flush);
  }
}
static int c3x_p32_measurement(void){c3x_p32_setup();return c3x_p31_tt_seq()==5ULL;}
static int c3x_p32_match(C3XP32Target *t,const char *scope,int cls,unsigned long long key,int ply,int depth,unsigned long long move,int bound,long long payload){
  return t->cls==cls && t->key==key && t->ply==ply && t->depth==depth && t->move==move && t->bound==bound && t->payload==payload && !strcmp(t->scope,scope);
}
static int c3x_p32_block(const char *scope,int cls,unsigned long long key,int ply,int depth,
                         int alpha,int beta,int ttval,int tteval,int bound,
                         unsigned long long move,long long payload){
  if(!c3x_p32_measurement() || !c3x_p32_family_has(cls))return 0;
  c3x_p32_events++;
  int selected=0;
  for(int i=0;i<c3x_p32_ntarget;i++){
    C3XP32Target *t=&c3x_p32_targets[i];
    if(c3x_p32_match(t,scope,cls,key,ply,depth,move,bound,payload)){
      t->seen++;
      if(t->seen==t->occ){t->fired=1;selected=1;}
    }
  }
  int block=0;
  if(!strcmp(c3x_p32_mode,"FRONTIER_NULL")) block=ply<=c3x_p32_frontier;
  else if(!strcmp(c3x_p32_mode,"REMOVE_SET")) block=selected;
  else if(!strcmp(c3x_p32_mode,"KEEP_SET")) block=(ply<=c3x_p32_frontier)&&!selected;
  else if(strcmp(c3x_p32_mode,"BASE")&&strcmp(c3x_p32_mode,"CATALOG")){fprintf(stderr,"C3X_P32_BAD_MODE %s\n",c3x_p32_mode);abort();}
  if(block)c3x_p32_blocked++;
  if(c3x_p32_f && ply<=8){
    c3x_p32_catalogued++;
    fprintf(c3x_p32_f,"E,%s,%s,%016llx,%d,%d,%d,%d,%d,%d,%d,%llu,%lld,%d,%d\n",
      scope,c3x_p32_cls_name(cls),key,ply,depth,alpha,beta,ttval,tteval,bound,move,payload,selected,block);
  }
  return block;
}
#endif
