package main

import "testing"

func fixture() Receipt {
	return Receipt{
		Schema:"c3x-015-independent-rust-p6s1-verifier-v1",
		Status:"INDEPENDENT_ROWS_AND_SHA_PASS_SCOPED",
		SourceSHA:sourceR2, NativeSHA:p6Native,
		Rows:64,Games:64,FENs:64,NoTarget:13,Eligible:51,Joint:44,Effects:2,
		Cases:[]BoundedCase{
			{Ordinal:2,NormalOFF:"d1e2",NormalSEE:"d1e2",BlockOFF:"d1e2",BlockSEE:"d1d2",
				OffEdgeDelivered:1,SeeEdgeDelivered:1,WriterClass:6,StoredBound:1,FullKey:4456240012406920917},
			{Ordinal:29,NormalOFF:"d1e2",NormalSEE:"f3e5",BlockOFF:"f3e5",BlockSEE:"f3e5",
				OffEdgeDelivered:1,SeeEdgeDelivered:1,WriterClass:6,StoredBound:1,FullKey:17758216835838653357},
		},
	}
}
func TestAuthorityCertificatesPermitOnlyNarrowClaims(t *testing.T){
	a,e:=certificate(fixture(),"a-generated-rust-receipt-sha")
	if e!=nil {t.Fatal(e)}
	if len(a.Authorized)!=2 || len(a.Abstained)!=5 {t.Fatalf("bad claims: %+v",a)}
	for _,c:=range a.Abstained {if c.Decision!="ABSTAIN"{t.Fatalf("must refuse unsupported claim %s",c.Key)}}
}
func TestRejectOverbroadOrAlteredEvidence(t *testing.T){
	r:=fixture();r.Effects=3
	if validate(r)==nil {t.Fatal("tampered effect count accepted")}
	r=fixture();r.Games=63
	if validate(r)==nil {t.Fatal("missing source game accepted")}
	r=fixture();r.Cases[0].NormalSEE="d1d2"
	if validate(r)==nil {t.Fatal("changed intended effect accepted")}
	r=fixture();r.Cases[1].SeeEdgeDelivered=0
	if validate(r)==nil {t.Fatal("target unexposed but outcome attributed")}
	r=fixture();r.NativeSHA="unverified"
	if validate(r)==nil {t.Fatal("mismatched native P6 SHA accepted")}
}
