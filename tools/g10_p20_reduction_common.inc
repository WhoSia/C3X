#ifndef C3X_P20_REDUCTION_INC
#define C3X_P20_REDUCTION_INC
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {
  int ply,depth,move_index,reduction,new_depth,reduced_depth,occ,seen,fired;
} C3XP20RedTarget;
static FILE *c3x_p20_red_f=NULL;
static unsigned long long c3x_p20_red_n=0;
static int c3x_p20_red_init=0;
static int c3x_p20_red_off=0;
static int c3x_p20_red_target_mode=0;
static C3XP20RedTarget c3x_p20_red_targets[2048];
static int c3x_p20_red_ntarget=0;
static void c3x_p20_red_flush(void){
  if(!c3x_p20_red_f)return;
  int fired=0;for(int i=0;i<c3x_p20_red_ntarget;i++)if(c3x_p20_red_targets[i].fired)fired++;
  fprintf(c3x_p20_red_f,"S,%llu,%d,%d\n",c3x_p20_red_n,c3x_p20_red_ntarget,fired);
  fflush(c3x_p20_red_f);
}
static void c3x_p20_red_setup(void){
  if(c3x_p20_red_init)return;
  c3x_p20_red_init=1;
  const char *m=getenv("C3X_P20_REDUCTION_MODE");
  if(!m||!*m||!strcmp(m,"BASE")){}
  else if(!strcmp(m,"NO_REDUCTION"))c3x_p20_red_off=1;
  else if(!strcmp(m,"TARGET_REMOVE"))c3x_p20_red_target_mode=1;
  else {fprintf(stderr,"C3X_P20_BAD_REDUCTION_MODE %s\n",m);abort();}
  const char *tf=getenv("C3X_P20_REDUCTION_TARGET_FILE");
  if(tf&&*tf){
    FILE *g=fopen(tf,"r");if(!g){perror("C3X_P20_REDUCTION_TARGET_FILE");abort();}
    while(c3x_p20_red_ntarget<2048){
      C3XP20RedTarget *t=&c3x_p20_red_targets[c3x_p20_red_ntarget];
      int n=fscanf(g,"%d\t%d\t%d\t%d\t%d\t%d\t%d",&t->ply,&t->depth,&t->move_index,&t->reduction,&t->new_depth,&t->reduced_depth,&t->occ);
      if(n==EOF)break;
      if(n!=7){fprintf(stderr,"C3X_P20_BAD_REDUCTION_TARGET %d\n",n);abort();}
      t->seen=0;t->fired=0;c3x_p20_red_ntarget++;
    }
    fclose(g);
  }
  const char *p=getenv("C3X_P20_REDUCTION_TRACE");
  if(p&&*p){
    c3x_p20_red_f=fopen(p,"w");if(!c3x_p20_red_f){perror("C3X_P20_REDUCTION_TRACE");abort();}
    setvbuf(c3x_p20_red_f,NULL,_IOLBF,0);atexit(c3x_p20_red_flush);
  }
}
static int c3x_p20_no_reduction(void){c3x_p20_red_setup();return c3x_p20_red_off;}
static int c3x_p20_target_reduction(int ply,int depth,int move_index,int reduction,int new_depth,int reduced_depth){
  c3x_p20_red_setup();if(!c3x_p20_red_target_mode)return 0;int selected=0;
  for(int i=0;i<c3x_p20_red_ntarget;i++){
    C3XP20RedTarget *t=&c3x_p20_red_targets[i];
    if(t->ply==ply&&t->depth==depth&&t->move_index==move_index&&t->reduction==reduction&&t->new_depth==new_depth&&t->reduced_depth==reduced_depth){
      t->seen++;if(t->seen==t->occ){t->fired=1;selected=1;}
    }
  }
  return selected;
}
static void c3x_p20_reduction_decision(const char *scope,int ply,int depth,int move_index,int reduction,int new_depth,int reduced_depth,int alpha,int beta,int quiet){
  c3x_p20_red_setup();
  if(!c3x_p20_red_f||c3x_p20_red_n>=2048)return;
  fprintf(c3x_p20_red_f,"D,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",scope,ply,depth,move_index,reduction,new_depth,reduced_depth,alpha,beta,quiet);
  c3x_p20_red_n++;
}
static void c3x_p20_reduction_research(const char *scope,int ply,int depth,int move_index,int reduced_depth,int full_depth,int alpha,int beta){
  c3x_p20_red_setup();
  if(!c3x_p20_red_f||c3x_p20_red_n>=2048)return;
  fprintf(c3x_p20_red_f,"F,%s,%d,%d,%d,%d,%d,%d,%d\n",scope,ply,depth,move_index,reduced_depth,full_depth,alpha,beta);
  c3x_p20_red_n++;
}
#endif
