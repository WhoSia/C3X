// c3x-cswp-authority refuses unsupported chess-engine causal explanations.
// The Go program checks a Rust-verified native-result certificate's claim scope.
// It is not a replacement for the native C++ or Rust source/byte verification.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"sort"
)

const sourceR2 = "1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534"
const p6Native = "c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11"

type BoundedCase struct {
	Ordinal          int    `json:"ordinal"`
	NormalOFF        string `json:"normal_off"`
	NormalSEE        string `json:"normal_see"`
	BlockOFF         string `json:"one_TT_block_off"`
	BlockSEE         string `json:"one_TT_block_see"`
	OffEdgeDelivered int    `json:"off_edge_delivered"`
	SeeEdgeDelivered int    `json:"see_edge_delivered"`
	WriterClass      int    `json:"selected_writer_class"`
	StoredBound      int    `json:"selected_stored_bound"`
	FullKey          uint64 `json:"selected_full_key"`
}

type Receipt struct {
	Schema        string        `json:"schema"`
	Status        string        `json:"status"`
	SourceSHA     string        `json:"original_r2_source_sha256"`
	NativeSHA     string        `json:"p6s1_native_json_sha256"`
	Rows          int           `json:"rows_checked"`
	Games         int           `json:"distinct_games"`
	FENs          int           `json:"distinct_fens"`
	NoTarget      int           `json:"no_target_negative_controls"`
	Eligible      int           `json:"targeted_TT_return_eligible"`
	Joint         int           `json:"edge_delivered_in_both"`
	Effects       int           `json:"change_in_SEE_response_identity_worlds"`
	Cases         []BoundedCase `json:"opposing_bounded_cases"`
}

type Claim struct {
	Key       string `json:"key"`
	Decision  string `json:"decision"`
	Rationale string `json:"rationale"`
}
type Authority struct {
	Schema           string  `json:"schema"`
	SourceReceiptSHA string  `json:"rust_receipt_bytes_sha256"`
	Authorized       []Claim `json:"authorized"`
	Abstained        []Claim `json:"abstain"`
	MaximumTier      string  `json:"maximum_tier"`
	Scope            string  `json:"scope"`
}

func validate(r Receipt) error {
	if r.Schema != "c3x-015-independent-rust-p6s1-verifier-v1" ||
		r.Status != "INDEPENDENT_ROWS_AND_SHA_PASS_SCOPED" {
		return errors.New("not an independently verified Rust P6 original-data certificate")
	}
	if r.SourceSHA != sourceR2 || r.NativeSHA != p6Native {
		return errors.New("original immutable source/native SHA mismatch")
	}
	if r.Rows != 64 || r.Games != 64 || r.FENs != 64 ||
		r.NoTarget != 13 || r.Eligible != 51 || r.Joint != 44 || r.Effects != 2 {
		return errors.New("independent Rust native population and exposure counts changed")
	}
	if len(r.Cases) != 2 {
		return errors.New("two opposing bounded causal edge cases not present")
	}
	ids := make([]int, 0, 2)
	appeared,disappeared := 0,0
	for _, c := range r.Cases {
		ids = append(ids,c.Ordinal)
		if c.OffEdgeDelivered != 1 || c.SeeEdgeDelivered != 1 ||
			c.FullKey == 0 || c.WriterClass == 0 {
			return errors.New("single-edge exact exposure/source writer identity missing")
		}
		before := c.NormalOFF != c.NormalSEE
		after := c.BlockOFF != c.BlockSEE
		if before == after {
			return fmt.Errorf("case %d does not change source SEE-response identity", c.Ordinal)
		}
		if !before && after { appeared++ } else { disappeared++ }
	}
	sort.Ints(ids)
	if ids[0] != 2 || ids[1] != 29 || appeared != 1 || disappeared != 1 {
		return errors.New("required oppositely oriented two-world intervention not preserved")
	}
	return nil
}

func certificate(r Receipt, sha string) (Authority,error) {
	if err:=validate(r);err!=nil{return Authority{},err}
	return Authority{
		Schema:"c3x-015-go-explanation-authority-gate-v1",
		SourceReceiptSHA:sha,
		MaximumTier:"BOUNDED_NATIVE_SINGLE_TT_RETURN_SOFTWARE_CONTRAST",
		Scope:"Stockfish16 classical depth12, original TWIC R2 64 frozen games; two single-event examples; no external universal validity",
		Authorized:[]Claim{
			{"SOURCE_COHORT_AND_NATIVE_RECEIPT_CONSISTENCY","ALLOW","Independent Rust compared native P2, presealed P6S0, and P6S1 byte-SHA identities and case-level outcomes."},
			{"TWO_BOUNDED_SINGLE_TT_RETURN_EFFECTS","ALLOW","Original native case 2 gains and case 29 loses source SEE bestmove sensitivity with one declared TT-return bypass."},
		},
		Abstained:[]Claim{
			{"FULL_NATURAL_TT_MEDIATION","ABSTAIN","Exact one-edge software perturbation is not identification of a natural indirect effect or unique causal mediator."},
			{"SEARCH_WINDOW_BOUND_AS_CHESS_TRUTH","ABSTAIN","Selective-engine TT LOWER/UPPER/EXACT tags do not certify perfect-chess minimax bound truth."},
			{"GENERAL_STRATEGY_OR_TACTIC_LAW","ABSTAIN","Two source- and engine-specific contrasts cannot certify a source-independent chess concept law."},
			{"NNUE_LEARNED_PIN_FEATURE","ABSTAIN","Source trials used classical Use NNUE=false; no NNUE feature intervention exists."},
			{"HUMAN_EXPLANATION_OF_MOVE_AS_INTENTION","ABSTAIN","A source-code preference change is not evidence the engine has a human intention or belief."},
		},
	},nil
}

func run(args []string) error {
	if len(args)!=3{return errors.New("usage: c3x-cswp-authority RUST_RECEIPT.json OUTPUT.json")}
	raw,err:=os.ReadFile(args[1]);if err!=nil{return err}
	h:=sha256.Sum256(raw)
	var r Receipt
	if err:=json.Unmarshal(raw,&r);err!=nil{return err}
	a,err:=certificate(r,hex.EncodeToString(h[:]));if err!=nil{return err}
	out,err:=json.MarshalIndent(a,"","  ");if err!=nil{return err}
	if err:=os.WriteFile(args[2],append(out,'
'),0644);err!=nil{return err}
	fmt.Printf("C3X015_GO_CSWP_AUTHORITY_ABSTAIN_GATE_PASS allowed=%d abstained=%d
",len(a.Authorized),len(a.Abstained))
	return nil
}
func main(){if err:=run(os.Args);err!=nil {fmt.Fprintln(os.Stderr,"C3X015_GO_AUTHORITY_GATE_FAIL",err);os.Exit(2)}}
