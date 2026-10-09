// P9 STS Source Audit is an original-byte, score-blind category census.
// It does not treat bm/c0 annotations as causal evidence or chess truth.
package main

import (
 "bufio"
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "errors"
 "flag"
 "fmt"
 "os"
 "regexp"
 "sort"
 "strings"
)

const expectedRawSHA = "d7a33ae6cf2fb5f3f18ef1b904cca07dce2cd0458edcf60644f59d4d9e28c07b"
var idRegex = regexp.MustCompile("(?i)\\bid\\s+\"STS\\(v([0-9]+)\\.[0-9]+\\) ([^.\"]+)\\.([0-9]+)\"")
type Section struct {
 Number int
 Name string
 Count int
}
type Receipt struct {
 Schema string
 Status string
 SourceSHA256 string
 OriginalFileBytes int
 TotalSourceEPD int
 UniqueFourFieldFENs int
 DuplicateFourFieldFENs int
 Sections []Section
 AnonymousScoreBlindLabelAccess bool
 Limits []string
}
func audit(raw []byte) (Receipt,error) {
 digest := sha256.Sum256(raw)
 got:=hex.EncodeToString(digest[:])
 if got!=expectedRawSHA{return Receipt{},fmt.Errorf("input byte SHA mismatch: %s",got)}
 count:=map[int]int{}
 sections:=map[int]string{}
 duplicate:=0
 seen:=map[string]bool{}
 lineNo:=0
 sc:=bufio.NewScanner(strings.NewReader(string(raw)))
 sc.Buffer(make([]byte,64*1024),2*1024*1024)
 for sc.Scan(){
  lineNo++
  line:=sc.Text()
  // Only parse opening EPD four fields and id; consciously DO NOT read bm/c0/c7/c8/c9.
  fields:=strings.Fields(line)
  if len(fields)<7{return Receipt{},fmt.Errorf("short EPD line %d",lineNo)}
  board:=fields[0]
  if len(strings.Split(board,"/"))!=8{return Receipt{},fmt.Errorf("wrong board rows line %d",lineNo)}
  if fields[1]!="w" && fields[1]!="b"{return Receipt{},fmt.Errorf("bad side to move %d",lineNo)}
  for _,piece:=range board{
   if strings.ContainsRune("12345678PNBRQKpnbrqk/",piece){continue}
   return Receipt{},fmt.Errorf("bad FEN piece char line %d",lineNo)
  }
  for _,rank:=range strings.Split(board,"/"){
   w:=0
   for _,c:=range rank {
    if c>='1'&&c<='8'{w+=int(c-'0')}else{w++}
   }
   if w!=8{return Receipt{},fmt.Errorf("bad EPD rank width line %d",lineNo)}
  }
  if fields[3]!="-" && len(fields[3])!=2{return Receipt{},fmt.Errorf("bad ep field line %d",lineNo)}
  beforeID:=strings.SplitN(line," id ",2)
  if len(beforeID)!=2{return Receipt{},fmt.Errorf("missing EPD id line %d",lineNo)}
  match:=idRegex.FindStringSubmatch("id "+beforeID[1])
  if len(match)!=4{return Receipt{},fmt.Errorf("bad STS section id line %d",lineNo)}
  var group,serial int
  if _,err:=fmt.Sscanf(match[1],"%d",&group);err!=nil{return Receipt{},err}
  if _,err:=fmt.Sscanf(match[3],"%d",&serial);err!=nil{return Receipt{},err}
  if group<1||group>15||serial<1||serial>100 {return Receipt{},fmt.Errorf("unexpected group/ordinal line %d",lineNo)}
  if name,ok:=sections[group];ok&&name!=match[2] {
    // One known section can contain a synonym; expose as drift rather than invent normalization.
    if group!=3{return Receipt{},fmt.Errorf("unregistered name variation group %d",group)}
  }else if !ok{sections[group]=match[2]}
  key:=strings.Join(fields[:4]," ")
  if seen[key]{duplicate++}
  seen[key]=true
  count[group]++
 }
 if err:=sc.Err();err!=nil{return Receipt{},err}
 if lineNo!=1500 || len(count)!=15 {return Receipt{},errors.New("not 1500 lines and 15 sections")}
 ordered:=[]Section{}
 for i:=1;i<=15;i++ {
  if count[i]!=100{return Receipt{},fmt.Errorf("section %d not 100 items",i)}
  ordered=append(ordered,Section{Number:i,Name:sections[i],Count:count[i]})
 }
 sort.Slice(ordered,func(i,j int)bool{return ordered[i].Number<ordered[j].Number})
 return Receipt{
  Schema:"c3x015-p9-go-scoreblind-STS-source-census-v1",
  Status:"SOURCE_ONLY_LEXICAL_CENSUS_PASS_CHESS_LAW_AND_ORACLE_AUTHORITY_HOLD",
  SourceSHA256:got,
  OriginalFileBytes:len(raw),
  TotalSourceEPD:lineNo,
  UniqueFourFieldFENs:len(seen),
  DuplicateFourFieldFENs:duplicate,
  Sections:ordered,
  AnonymousScoreBlindLabelAccess:false,
  Limits:[]string{
   "This program deliberately ignores bm, c0 and move-score annotations; no engine score seen.",
   "Lexical FEN board validation is not proof of legal reachability, rule50 history or source rights.",
   "Original STS annotations are external preferences, not verified optimal chess or causal treatment labels.",
   "C3X P1 primary accuracy failure stays unchanged.",
  },
 },nil
}
func main(){
 input:=flag.String("input","","source EPD")
 output:=flag.String("output","","receipt JSON")
 flag.Parse()
 if *input==""||*output==""{fmt.Fprintln(os.Stderr,"provide -input and -output");os.Exit(2)}
 raw,err:=os.ReadFile(*input)
 if err!=nil{fmt.Fprintln(os.Stderr,err);os.Exit(2)}
 r,err:=audit(raw)
 if err!=nil{fmt.Fprintln(os.Stderr,"FAIL_CLOSED_STS_SOURCE_CENSUS:",err);os.Exit(2)}
 data,err:=json.MarshalIndent(r,"","  ")
 if err!=nil{panic(err)}
 if err:=os.WriteFile(*output,append(data,10),0644);err!=nil{panic(err)}
 fmt.Printf("P9_STS_GO_SCOREBLIND_SOURCE_AUDIT_PASS sections=%d positions=%d duplicate_fen=%d\n",len(r.Sections),r.TotalSourceEPD,r.DuplicateFourFieldFENs)
}
