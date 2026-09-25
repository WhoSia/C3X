static void c3x_p30_hit(uint64_t hash, TTEntry* e){
  if(!c3x_graph_on())return;
  uint64_t b,idx;int s;idx=c3x_et_index(e,&b,&s);
  if(!C3XKeys[idx]||C3XKeys[idx]!=hash)return;
  fprintf(c3x_trace_file(),"H,%llu,%llu,%d,%016llx,%u\n",
    (unsigned long long)C3XSeq,(unsigned long long)b,s,(unsigned long long)hash,(unsigned)C3XStoreSeq[idx]);
}
static int c3x_p30_et_age_score(TTEntry* e){
  return (int)e->depth - (int)((259 + Table.generation - e->generation) & TT_MASK_AGE);
}
static void c3x_p30_victim(uint64_t requested, TTEntry* slots, TTEntry* actual, int hadShortMatch){
  if(!c3x_graph_on()||hadShortMatch)return;
  for(int i=0;i<TT_BUCKET_NB;i++)if((slots[i].generation & TT_MASK_BOUND)==BOUND_NONE)return;
  TTEntry* depthOnly=slots;
  for(int i=1;i<TT_BUCKET_NB;i++)if(depthOnly->depth>=slots[i].depth)depthOnly=&slots[i];
  uint64_t b,ai,di;int as,ds;ai=c3x_et_index(actual,&b,&as);uint64_t db;di=c3x_et_index(depthOnly,&db,&ds);
  fprintf(c3x_trace_file(),"V,%llu,%llu,%016llx,%d,%016llx,%d,%016llx,%d,%d,%d\n",
    (unsigned long long)C3XSeq,(unsigned long long)b,(unsigned long long)requested,
    as,(unsigned long long)C3XKeys[ai],ds,(unsigned long long)C3XKeys[di],
    c3x_p30_et_age_score(actual),(int)depthOnly->depth,1);
}
