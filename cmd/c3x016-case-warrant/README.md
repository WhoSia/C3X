# C3X 0.16 — Source-Exact Natural TT Case Warrant (Go)

**Active 0.16 only; inherited 0.15 evidence, not another 0.15 experiment.**

Executable Go source, tests and a source-SHA-locked machine JSON warrant are stored in the [private C3X 0.16 Drive reproducibility ZIP](https://drive.google.com/file/d/1yjYYlME8EBcyVE7Og6_NiK5hH9oZDLJD/view), original ZIP SHA-256 `85677f92ffa46f7c4df8f4ab68ee7e7eef58da0cfaa291dc05e84db9c24020d2`. [GitHub small scientific receipt](../../c3x/receipts/c3x-016-P0-natural-TT-case-warrant-go-verified-source-and-inherited-closure-20261009.json).

This directory documents the source package and exact reproducibility command; **Go code is delivered in the linked Drive ZIP rather than committed as text in this directory**. Do not confuse this README with an actual local Go module.

## Run

Extract the Drive ZIP into a temporary directory, then rename the two Go source files to `main.go` and `main_test.go`:

```sh
mv C3X016_natural_TT_case_warrant.go main.go
mv C3X016_natural_TT_case_warrant_test.go main_test.go
GO111MODULE=off go test -v .
```

For the original-source integration test, extract `C3X015_P11_EXACT_ROOT_CHILD_RELAY_48_NATIVE.json` **from the immutable [P11 original 48-native evidence ZIP](https://drive.google.com/file/d/1Gq9HwSbLdOkC9QziHjRa8UGszrNnHX4m/view)**. Expected JSON member SHA-256: `0a296860a26db3b8b5530a23eb7935f6f71f8fd9e809299ea39486133022a2f8`.

```sh
C3X016_P11_JSON_INPUT=./C3X015_P11_EXACT_ROOT_CHILD_RELAY_48_NATIVE.json GO111MODULE=off go test -v .
GO111MODULE=off go run main.go \
    -input ./C3X015_P11_EXACT_ROOT_CHILD_RELAY_48_NATIVE.json \
    -output ./C3X016_case_warrant_recomputed.json
```

The local original source experiment produced **6 synthetic fail-closed Go unit tests PASS + 1 original P11 member integration test PASS**. When the original member path is not set, the integration test is explicitly SKIPPED and not falsely counted as a native verification. The Go reader itself does not rerun SF16 or reconstruct the two cold native processes per unique arm.

It refuses swapped source-world identity, noncontact intervention with a changed result, sham contact, incomplete arms and altered source SHA. It explicitly labels both cases as **retrospectively post-P6 selected** and refuses promotion to 0.16 prospective independent validation. See the [formal case-partition theory](../../c3x/ontology/c3x-016-natural-TT-case-partition-warrant-v0.1.md).

**Current verdict:** `SOURCE_SCOPED_CASE_WARRANT_PASS / NATURAL_TT_CAUSAL_NECESSITY_HOLD / 0.15_CLOSED_0.16_ACTIVE`.
