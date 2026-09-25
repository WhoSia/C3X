struct C3XTraceStats {
    unsigned long long probes=0, signatureHits=0, fullHits=0, signatureCollisions=0;
    unsigned long long emptySignatureMatches=0, shadowUnknown=0, crossHits=0;
    unsigned long long origin[6]{};
    unsigned long long storeAttempts=0, storeCommits=0, initialStores=0, sameKeyUpdates=0;
    unsigned long long replacements=0, storeRejects=0;
    unsigned long long ageAttempts=0, ageChanges=0, ageTrueKey=0, ageCollisionKey=0;
};
struct C3XShadow {
    Key key=0;
    unsigned long long storeSeq=0;
    usize bucket=0;
    int slot=0;
};
static std::unordered_map<const TTEntry*,C3XShadow> c3xShadow;
static C3XTraceStats c3xStats{};
static unsigned long long c3xSeq=0;

static bool c3x_trace_enabled() {
    static const bool on = std::getenv("C3X_TT_TRACE") != nullptr;
    return on;
}
static unsigned long long c3x_graph_seq() {
    static const unsigned long long s = [](){
        const char* x=std::getenv("C3X_TT_GRAPH_SEQ");
        return x ? std::strtoull(x,nullptr,10) : 0ULL;
    }();
    return s;
}
static FILE* c3x_trace_file() {
    static FILE* f=nullptr;
    static bool init=false;
    if (!init) {
        init=true;
        const char* p=std::getenv("C3X_TT_TRACE");
        if (p && *p) {
            f=std::fopen(p,"w");
            if (!f) { std::perror("C3X_TT_TRACE"); std::abort(); }
            std::setvbuf(f,nullptr,_IOLBF,0);
        }
    }
    return f;
}
static bool c3x_graph_on() { return c3x_trace_enabled() && c3xSeq==c3x_graph_seq(); }
static void c3x_loc(const TTEntry* e,usize bucket,int slot) {
    if (!c3x_trace_enabled()) return;
    auto& z=c3xShadow[e]; z.bucket=bucket; z.slot=slot;
}
static void c3x_emit_summary() {
    FILE* f=c3x_trace_file(); if (!f || !c3xSeq) return;
    std::fprintf(f,
      "S,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\n",
      c3xSeq,c3xStats.probes,c3xStats.signatureHits,c3xStats.fullHits,
      c3xStats.signatureCollisions,c3xStats.emptySignatureMatches,c3xStats.shadowUnknown,
      c3xStats.crossHits,c3xStats.origin[1],c3xStats.origin[2],c3xStats.origin[3],
      c3xStats.origin[4],c3xStats.origin[5],c3xStats.storeAttempts,c3xStats.storeCommits,
      c3xStats.initialStores,c3xStats.sameKeyUpdates,c3xStats.replacements,c3xStats.storeRejects,
      c3xStats.ageAttempts,c3xStats.ageChanges,c3xStats.ageTrueKey,c3xStats.ageCollisionKey);
}
static void c3x_begin_search() {
    if (!c3x_trace_enabled()) return;
    c3x_trace_file();
    if (c3xSeq) c3x_emit_summary();
    c3xStats=C3XTraceStats{};
    ++c3xSeq;
}
static void c3x_trace_reset() {
    if (!c3x_trace_enabled()) return;
    c3x_trace_file(); c3xShadow.clear(); c3xStats=C3XTraceStats{}; c3xSeq=0;
}
static void c3x_probe_start() {
    if (c3x_trace_enabled()) ++c3xStats.probes;
}
static void c3x_probe_result(const TTEntry* e,Key requested,bool occupied) {
    if (!c3x_trace_enabled() || !occupied) return;
    ++c3xStats.signatureHits;
    auto it=c3xShadow.find(e);
    if (it==c3xShadow.end() || !it->second.key) { ++c3xStats.shadowUnknown; return; }
    const auto& z=it->second;
    if (z.key==requested) {
        ++c3xStats.fullHits;
        if (z.storeSeq<c3xSeq) {
            ++c3xStats.crossHits;
            unsigned long long d=c3xSeq-z.storeSeq;
            if (d>=5) d=5;
            ++c3xStats.origin[d];
        }
    } else {
        ++c3xStats.signatureCollisions;
        if (c3x_graph_on()) std::fprintf(c3x_trace_file(),
          "C,%llu,%zu,%d,%016llx,%016llx,%llu\n",
          c3xSeq,z.bucket,z.slot,(unsigned long long)requested,(unsigned long long)z.key,z.storeSeq);
    }
}
static void c3x_store(const TTEntry* e,Key key,bool commit) {
    if (!c3x_trace_enabled()) return;
    ++c3xStats.storeAttempts;
    auto& z=c3xShadow[e];
    if (!commit) { ++c3xStats.storeRejects; return; }
    ++c3xStats.storeCommits;
    if (!z.key) ++c3xStats.initialStores;
    else if (z.key==key) ++c3xStats.sameKeyUpdates;
    else {
        ++c3xStats.replacements;
        if (c3x_graph_on()) std::fprintf(c3x_trace_file(),
          "R,%llu,%zu,%d,%016llx,%016llx,%llu\n",
          c3xSeq,z.bucket,z.slot,(unsigned long long)z.key,(unsigned long long)key,z.storeSeq);
    }
    z.key=key; z.storeSeq=c3xSeq;
}
static void c3x_age(const TTEntry* e,Key requested,u8 oldv,u8 newv) {
    if (!c3x_trace_enabled()) return;
    ++c3xStats.ageAttempts;
    if (oldv!=newv) ++c3xStats.ageChanges;
    auto it=c3xShadow.find(e);
    Key resident=(it==c3xShadow.end()?Key(0):it->second.key);
    if (resident && resident==requested) ++c3xStats.ageTrueKey;
    else if (resident) ++c3xStats.ageCollisionKey;
    if (c3x_graph_on() && it!=c3xShadow.end()) std::fprintf(c3x_trace_file(),
      "A,%llu,%zu,%d,%016llx,%016llx,%d\n",
      c3xSeq,it->second.bucket,it->second.slot,(unsigned long long)requested,
      (unsigned long long)resident,oldv!=newv);
}
static void c3x_vacate(const TTEntry* e) {
    if (!c3x_trace_enabled()) return;
    auto it=c3xShadow.find(e);
    if (it!=c3xShadow.end()) { it->second.key=0; it->second.storeSeq=0; }
}
