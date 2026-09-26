#ifndef C3X_P34_CONE_TARGET_INC
#define C3X_P34_CONE_TARGET_INC

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct {
  int scope, cls, ply_bucket, bound, payload_bucket, depth_bucket, move_presence, window_relation;
} C3XP34Cone;

static int c3x_p34_init=0;
static char c3x_p34_mode[24]="BASE";
static int c3x_p34_level=0;
static C3XP34Cone c3x_p34_selected[512];
static int c3x_p34_nselected=0;
static FILE *c3x_p34_f=NULL;
static unsigned long long c3x_p34_events=0,c3x_p34_seed_blocked=0,c3x_p34_extra_blocked=0;

static int c3x_p34_scope(const char *scope){return !strcmp(scope,"QSEARCH")?1:0;}
static int c3x_p34_ply_bucket(int ply){
  if(ply<=0)return 0;if(ply==1)return 1;if(ply==2)return 2;if(ply<=4)return 3;if(ply<=8)return 4;return 5;
}
static int c3x_p34_depth_bucket(int depth){
  if(depth<=0)return 0;if(depth<=4)return 1;if(depth<=8)return 2;if(depth<=12)return 3;if(depth<=16)return 4;if(depth<=24)return 5;return 6;
}
static int c3x_p34_payload_bucket(long long payload){
  if(payload==0)return 0;if(payload==1)return 1;if(payload==-1)return 2;if(payload>0)return 3;return 4;
}
static int c3x_p34_window_relation(int ttval,int alpha,int beta){
  if(ttval<=alpha)return 0;if(ttval>=beta)return 2;return 1;
}
static int c3x_p34_same(const C3XP34Cone *a,const C3XP34Cone *b,int level){
  if(a->scope!=b->scope||a->cls!=b->cls||a->ply_bucket!=b->ply_bucket)return 0;
  if(level>=1 && (a->bound!=b->bound||a->payload_bucket!=b->payload_bucket))return 0;
  if(level>=2 && (a->depth_bucket!=b->depth_bucket||a->move_presence!=b->move_presence))return 0;
  if(level>=3 && a->window_relation!=b->window_relation)return 0;
  return 1;
}
static void c3x_p34_flush(void){
  if(!c3x_p34_f)return;
  fprintf(c3x_p34_f,"S34,%llu,%llu,%llu,%d,%d\n",
    c3x_p34_events,c3x_p34_seed_blocked,c3x_p34_extra_blocked,c3x_p34_level,c3x_p34_nselected);
  fflush(c3x_p34_f);
}
static void c3x_p34_setup(void){
  if(c3x_p34_init)return;c3x_p34_init=1;
  const char *m=getenv("C3X_P34_MODE");if(m&&*m)snprintf(c3x_p34_mode,sizeof(c3x_p34_mode),"%s",m);
  const char *l=getenv("C3X_P34_LEVEL");if(l&&*l)c3x_p34_level=atoi(l);
  if(c3x_p34_level<0||c3x_p34_level>3){fprintf(stderr,"C3X_P34_BAD_LEVEL %d\n",c3x_p34_level);abort();}
  const char *sf=getenv("C3X_P34_SET_FILE");
  if(sf&&*sf){
    FILE *g=fopen(sf,"r");if(!g){perror("C3X_P34_SET_FILE");abort();}
    while(c3x_p34_nselected<512){
      C3XP34Cone *q=&c3x_p34_selected[c3x_p34_nselected];
      int n=fscanf(g,"%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d",
        &q->scope,&q->cls,&q->ply_bucket,&q->bound,&q->payload_bucket,&q->depth_bucket,&q->move_presence,&q->window_relation);
      if(n==EOF)break;if(n!=8){fprintf(stderr,"C3X_P34_BAD_SET_LINE n=%d\n",n);abort();}
      c3x_p34_nselected++;
    }
    fclose(g);
  }
  const char *tr=getenv("C3X_P34_TRACE");
  if(tr&&*tr){
    c3x_p34_f=fopen(tr,"w");if(!c3x_p34_f){perror("C3X_P34_TRACE");abort();}
    setvbuf(c3x_p34_f,NULL,_IOLBF,0);atexit(c3x_p34_flush);
  }
}
static int c3x_p34_block(const char *scope,int cls,unsigned long long key,int ply,int depth,
                         int alpha,int beta,int ttval,int tteval,int bound,
                         unsigned long long move,long long payload){
  c3x_p34_setup();
  int seed=c3x_p32_block(scope,cls,key,ply,depth,alpha,beta,ttval,tteval,bound,move,payload);
  if(!c3x_p32_measurement() || !c3x_p32_family_has(cls))return seed;
  C3XP34Cone q;
  q.scope=c3x_p34_scope(scope);q.cls=cls;q.ply_bucket=c3x_p34_ply_bucket(ply);q.bound=bound;
  q.payload_bucket=c3x_p34_payload_bucket(payload);q.depth_bucket=c3x_p34_depth_bucket(depth);
  q.move_presence=move?1:0;q.window_relation=c3x_p34_window_relation(ttval,alpha,beta);
  int selected=0;
  for(int i=0;i<c3x_p34_nselected;i++)if(c3x_p34_same(&q,&c3x_p34_selected[i],c3x_p34_level)){selected=1;break;}
  int extra=0;
  if(!strcmp(c3x_p34_mode,"REMOVE_ALL"))extra=ply<=c3x_p32_frontier;
  else if(!strcmp(c3x_p34_mode,"REMOVE_SET"))extra=(ply<=c3x_p32_frontier)&&selected;
  else if(!strcmp(c3x_p34_mode,"KEEP_SET"))extra=(ply<=c3x_p32_frontier)&&!selected;
  else if(strcmp(c3x_p34_mode,"BASE")&&strcmp(c3x_p34_mode,"CATALOG")&&strcmp(c3x_p34_mode,"SEED_ONLY")){
    fprintf(stderr,"C3X_P34_BAD_MODE %s\n",c3x_p34_mode);abort();
  }
  c3x_p34_events++;if(seed)c3x_p34_seed_blocked++;if(extra)c3x_p34_extra_blocked++;
  if(c3x_p34_f && ply<=8){
    fprintf(c3x_p34_f,"C,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%016llx,%d,%d,%llu,%lld,%d,%d,%d,%d,%d\n",
      c3x_p34_level,q.scope,q.cls,q.ply_bucket,q.bound,q.payload_bucket,q.depth_bucket,q.move_presence,q.window_relation,
      selected,seed,extra,key,ply,depth,move,payload,alpha,beta,ttval,tteval,bound);
  }
  return seed||extra;
}
#endif
