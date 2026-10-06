#ifndef C3X_P20_REDUCTION_INC
#define C3X_P20_REDUCTION_INC
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static FILE *c3x_p20_red_f=NULL;
static unsigned long long c3x_p20_red_n=0;
static int c3x_p20_red_init=0;
static int c3x_p20_red_off=0;
static void c3x_p20_red_setup(void){
  if(c3x_p20_red_init)return;
  c3x_p20_red_init=1;
  const char *m=getenv("C3X_P20_REDUCTION_MODE");
  if(!m||!*m||!strcmp(m,"BASE"))c3x_p20_red_off=0;
  else if(!strcmp(m,"NO_REDUCTION"))c3x_p20_red_off=1;
  else {fprintf(stderr,"C3X_P20_BAD_REDUCTION_MODE %s\n",m);abort();}
  const char *p=getenv("C3X_P20_REDUCTION_TRACE");
  if(p&&*p){
    c3x_p20_red_f=fopen(p,"w");
    if(!c3x_p20_red_f){perror("C3X_P20_REDUCTION_TRACE");abort();}
    setvbuf(c3x_p20_red_f,NULL,_IOLBF,0);
  }
}
static int c3x_p20_no_reduction(void){c3x_p20_red_setup();return c3x_p20_red_off;}
static void c3x_p20_reduction_decision(const char *scope,int ply,int depth,int move_index,int reduction,int new_depth,int reduced_depth,int alpha,int beta,int quiet){
  c3x_p20_red_setup();
  if(!c3x_p20_red_f||c3x_p20_red_n>=512)return;
  fprintf(c3x_p20_red_f,"D,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",scope,ply,depth,move_index,reduction,new_depth,reduced_depth,alpha,beta,quiet);
  c3x_p20_red_n++;
}
static void c3x_p20_reduction_research(const char *scope,int ply,int depth,int move_index,int reduced_depth,int full_depth,int alpha,int beta){
  c3x_p20_red_setup();
  if(!c3x_p20_red_f||c3x_p20_red_n>=512)return;
  fprintf(c3x_p20_red_f,"F,%s,%d,%d,%d,%d,%d,%d,%d\n",scope,ply,depth,move_index,reduced_depth,full_depth,alpha,beta);
  c3x_p20_red_n++;
}
#endif
