typedef struct {
  uint64_t probes,signatureHits,fullHits,signatureCollisions,emptySignatureMatches,shadowUnknown,crossHits;
  uint64_t origin[6];
  uint64_t storeAttempts,storeCommits,initialStores,sameKeyUpdates,replacements,storeRejects;
  uint64_t ageAttempts,ageChanges,ageTrueKey,ageCollisionKey;
} C3XTraceStats;

static C3XTraceStats C3XS;
static uint64_t C3XSeq=0,*C3XKeys=NULL;
static uint8_t *C3XStoreSeq=NULL;
static uint64_t C3XSlots=0;
static FILE *C3XF=NULL;
static int C3XInit=-1;

static int c3x_trace_enabled(void){
  if(C3XInit<0) C3XInit=getenv("C3X_TT_TRACE")?1:0;
  return C3XInit;
}
static uint64_t c3x_graph_seq(void){
  static int init=0; static uint64_t v=0;
  if(!init){const char*x=getenv("C3X_TT_GRAPH_SEQ");v=x?strtoull(x,NULL,10):0;init=1;}
  return v;
}
static FILE* c3x_trace_file(void){
  if(!c3x_trace_enabled())return NULL;
  if(!C3XF){
    const char*p=getenv("C3X_TT_TRACE");
    C3XF=fopen(p,"w");
    if(!C3XF){perror("C3X_TT_TRACE");abort();}
    setvbuf(C3XF,NULL,_IOLBF,0);
  }
  return C3XF;
}
static int c3x_graph_on(void){return c3x_trace_enabled()&&C3XSeq==c3x_graph_seq();}
static void c3x_trace_alloc(uint64_t n){
  if(!c3x_trace_enabled())return;
  if(C3XSlots!=n){
    free(C3XKeys);free(C3XStoreSeq);
    C3XKeys=calloc(n,sizeof(uint64_t));C3XStoreSeq=calloc(n,sizeof(uint8_t));
    if(!C3XKeys||!C3XStoreSeq)abort();
    C3XSlots=n;
  }
}
static void c3x_emit_summary(void){
  FILE*f=c3x_trace_file();if(!f||!C3XSeq)return;
  fprintf(f,"S,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\n",
   (unsigned long long)C3XSeq,(unsigned long long)C3XS.probes,(unsigned long long)C3XS.signatureHits,
   (unsigned long long)C3XS.fullHits,(unsigned long long)C3XS.signatureCollisions,
   (unsigned long long)C3XS.emptySignatureMatches,(unsigned long long)C3XS.shadowUnknown,
   (unsigned long long)C3XS.crossHits,(unsigned long long)C3XS.origin[1],(unsigned long long)C3XS.origin[2],
   (unsigned long long)C3XS.origin[3],(unsigned long long)C3XS.origin[4],(unsigned long long)C3XS.origin[5],
   (unsigned long long)C3XS.storeAttempts,(unsigned long long)C3XS.storeCommits,
   (unsigned long long)C3XS.initialStores,(unsigned long long)C3XS.sameKeyUpdates,
   (unsigned long long)C3XS.replacements,(unsigned long long)C3XS.storeRejects,
   (unsigned long long)C3XS.ageAttempts,(unsigned long long)C3XS.ageChanges,
   (unsigned long long)C3XS.ageTrueKey,(unsigned long long)C3XS.ageCollisionKey);
}
static void c3x_trace_begin_search(void){
  if(!c3x_trace_enabled())return;
  c3x_trace_file();
  if(C3XSeq)c3x_emit_summary();
  memset(&C3XS,0,sizeof(C3XS));C3XSeq++;
}
static void c3x_trace_reset_common(uint64_t n){
  if(!c3x_trace_enabled())return;
  c3x_trace_file();c3x_trace_alloc(n);
  memset(C3XKeys,0,n*sizeof(uint64_t));
  memset(C3XStoreSeq,0,n*sizeof(uint8_t));
  memset(&C3XS,0,sizeof(C3XS));C3XSeq=0;
}
static uint64_t c3x_be_index(TTEntry*e,uint64_t*bucket,int*slot){
  uintptr_t off=(uintptr_t)((unsigned char*)e-(unsigned char*)TT.buckets);
  *bucket=off/sizeof(TTBucket);
  *slot=(int)((off%sizeof(TTBucket))/sizeof(TTEntry));
  return (*bucket)*BUCKET_SIZE+(uint64_t)(*slot);
}

void c3x_tt_trace_probe_start(uint64_t hash){
  (void)hash;if(c3x_trace_enabled())C3XS.probes++;
}
void c3x_tt_trace_probe_result(uint64_t hash,TTEntry*e,int hit){
  if(!c3x_trace_enabled())return;
  uint64_t b,idx;int s;idx=c3x_be_index(e,&b,&s);
  if(!hit)return;
  C3XS.signatureHits++;
  uint64_t resident=C3XKeys[idx];
  if(!resident){C3XS.shadowUnknown++;return;}
  if(resident==hash){
    C3XS.fullHits++;
    if(C3XStoreSeq[idx]<C3XSeq){
      uint64_t d=C3XSeq-C3XStoreSeq[idx];C3XS.crossHits++;if(d>=5)d=5;C3XS.origin[d]++;
    }
  }else{
    C3XS.signatureCollisions++;
    if(c3x_graph_on())fprintf(c3x_trace_file(),"C,%llu,%llu,%d,%016llx,%016llx,%u\n",
      (unsigned long long)C3XSeq,(unsigned long long)b,s,(unsigned long long)hash,
      (unsigned long long)resident,(unsigned)C3XStoreSeq[idx]);
  }
}
void c3x_tt_trace_store(TTEntry*e,uint64_t hash,int commit){
  if(!c3x_trace_enabled())return;
  uint64_t b,idx;int s;idx=c3x_be_index(e,&b,&s);C3XS.storeAttempts++;
  if(!commit){C3XS.storeRejects++;return;}
  C3XS.storeCommits++;
  uint64_t old=C3XKeys[idx];
  if(!old)C3XS.initialStores++;
  else if(old==hash)C3XS.sameKeyUpdates++;
  else{
    C3XS.replacements++;
    if(c3x_graph_on())fprintf(c3x_trace_file(),"R,%llu,%llu,%d,%016llx,%016llx,%u\n",
      (unsigned long long)C3XSeq,(unsigned long long)b,s,(unsigned long long)old,
      (unsigned long long)hash,(unsigned)C3XStoreSeq[idx]);
  }
  C3XKeys[idx]=hash;C3XStoreSeq[idx]=(uint8_t)C3XSeq;
}
void c3x_tt_trace_age(TTEntry*e,uint64_t requested,uint8_t oldv,uint8_t newv){
  if(!c3x_trace_enabled())return;
  uint64_t b,idx;int s;idx=c3x_be_index(e,&b,&s);
  C3XS.ageAttempts++;if(oldv!=newv)C3XS.ageChanges++;
  uint64_t resident=C3XKeys[idx];
  if(resident&&resident==requested)C3XS.ageTrueKey++;
  else if(resident)C3XS.ageCollisionKey++;
  if(c3x_graph_on())fprintf(c3x_trace_file(),"A,%llu,%llu,%d,%016llx,%016llx,%d\n",
    (unsigned long long)C3XSeq,(unsigned long long)b,s,(unsigned long long)requested,
    (unsigned long long)resident,oldv!=newv);
}
