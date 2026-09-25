static void c3x_p30_hit(uint64_t hash, TTEntry* e){
  if(!c3x_graph_on())return;
  uint64_t b,idx;int s;idx=c3x_be_index(e,&b,&s);
  if(!C3XKeys[idx]||C3XKeys[idx]!=hash)return;
  fprintf(c3x_trace_file(),"H,%llu,%llu,%d,%016llx,%u\n",
    (unsigned long long)C3XSeq,(unsigned long long)b,s,(unsigned long long)hash,(unsigned)C3XStoreSeq[idx]);
}
static void c3x_p30_victim(uint64_t requested, TTEntry* bucket, TTEntry* actual){
  if(!c3x_graph_on())return;
  for(int i=0;i<BUCKET_SIZE;i++)if(!bucket[i].depth)return;
  TTEntry* depthOnly=bucket;
  for(int i=1;i<BUCKET_SIZE;i++)if(TTDepth(depthOnly)>TTDepth(bucket+i))depthOnly=bucket+i;
  uint64_t b,ai,di;int as,ds;ai=c3x_be_index(actual,&b,&as);uint64_t db;di=c3x_be_index(depthOnly,&db,&ds);
  int actualScore=(int)actual->depth-(int)TTAge(actual)/2;
  int depthOnlyScore=(int)TTDepth(depthOnly);
  fprintf(c3x_trace_file(),"V,%llu,%llu,%016llx,%d,%016llx,%d,%016llx,%d,%d,%d\n",
    (unsigned long long)C3XSeq,(unsigned long long)b,(unsigned long long)requested,
    as,(unsigned long long)C3XKeys[ai],ds,(unsigned long long)C3XKeys[di],actualScore,depthOnlyScore,1);
}
