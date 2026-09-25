args<-commandArgs(trailingOnly=TRUE)
if(length(args)!=3)stop("usage: Rscript p22_balance_audit.R census.tsv selected.txt audit.json")
d<-read.delim(args[1],check.names=FALSE,stringsAsFactors=FALSE)
sel<-scan(args[2],what="character",quiet=TRUE)
x<-d[d$sha%in%sel,,drop=FALSE]
if(nrow(x)!=96||length(unique(sel))!=96)stop("P22_R_SELECTED_COUNT")
q<-table(x$family,x$side);if(any(q!=6)||length(q)!=16)stop("P22_R_QUOTA")
if(any(x$inanis_tt_main<=0)||any(x$inanis_pawn_q<=0))stop("P22_R_ENGAGEMENT")
f<-c("sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare")
h<-x[x$square=="HEAVY_HEAVY",,drop=FALSE];m<-x[x$square=="MINOR_MINOR",,drop=FALSE]
if(nrow(h)!=48||nrow(m)!=48)stop("P22_R_RELATION_COUNT")
smd<-function(a,b){den<-sqrt((var(a)+var(b))/2);if(!is.finite(den)||den<1e-15)return(if(abs(mean(a)-mean(b))<1e-12)0 else 1e9);abs(mean(a)-mean(b))/den}
vr<-function(a,b){va<-var(a);vb<-var(b);if(va<1e-15&&vb<1e-15)return(0);if(va<1e-15||vb<1e-15)return(1e9);abs(log(va/vb))}
ds<-sapply(f,function(k)smd(h[[k]],m[[k]]));vrs<-sapply(f,function(k)vr(h[[k]],m[[k]]));mx<-max(ds);pass<-mx<=0.5+1e-12
esc<-function(s)gsub('"','\\\\"',s,fixed=TRUE)
arr<-function(v)paste(format(v,digits=17,scientific=FALSE,trim=TRUE),collapse=",")
out<-paste0('{\n  "schema": "c3x-p22-r-balance-audit-v1",\n  "selected_count": 96,\n  "heavy_count": 48,\n  "minor_count": 48,\n  "quota_pass": true,\n  "inanis_engagement_pass": true,\n  "threshold": 0.5,\n  "max_abs_smd": ',format(mx,digits=17),' ,\n  "mean_abs_smd": ',format(mean(ds),digits=17),',\n  "max_abs_log_variance_ratio": ',format(max(vrs),digits=17),',\n  "smd": [',arr(ds),'],\n  "abs_log_variance_ratio": [',arr(vrs),'],\n  "gate_pass": ',tolower(as.character(pass)),'\n}\n')
writeLines(out,args[3]);cat(sprintf("P22_R_AUDIT max_smd=%.9f pass=%s\n",mx,pass));if(!pass)quit(status=42)
