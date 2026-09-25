static void c3x_p30_hit(const TTEntry* e, Key requested) {
    if (!c3x_graph_on()) return;
    auto it=c3xShadow.find(e);
    if (it==c3xShadow.end() || it->second.key!=requested) return;
    const auto& z=it->second;
    std::fprintf(c3x_trace_file(),"H,%llu,%zu,%d,%016llx,%llu\n",
      c3xSeq,z.bucket,z.slot,(unsigned long long)requested,z.storeSeq);
}
static void c3x_p30_victim(Key requested, TTEntry* base, TTEntry* actual, usize bucket, u8 generation) {
    if (!c3x_graph_on()) return;
    bool all=true;
    for (int i=0;i<ClusterSize;i++) if (!base[i].is_occupied()) all=false;
    if (!all) return;
    TTEntry* depthOnly=base;
    for (int i=1;i<ClusterSize;i++)
        if (depthOnly->read().depth > base[i].read().depth) depthOnly=&base[i];
    auto ak=c3xShadow.find(actual), dk=c3xShadow.find(depthOnly);
    const Key actualKey=ak==c3xShadow.end()?Key(0):ak->second.key;
    const Key depthKey=dk==c3xShadow.end()?Key(0):dk->second.key;
    const int actualSlot=int(actual-base), depthSlot=int(depthOnly-base);
    const int actualScore=int(actual->read().depth)-8*int(actual->relative_age(generation));
    const int depthOnlyScore=int(depthOnly->read().depth);
    std::fprintf(c3x_trace_file(),"V,%llu,%zu,%016llx,%d,%016llx,%d,%016llx,%d,%d,%d\n",
      c3xSeq,bucket,(unsigned long long)requested,actualSlot,(unsigned long long)actualKey,
      depthSlot,(unsigned long long)depthKey,actualScore,depthOnlyScore,1);
}
