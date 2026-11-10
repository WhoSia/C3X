"use strict";
/* C3X 0.30 P3-V: genuine browser rendering, user click and native Stockfish. */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const browser = await chromium.launch({headless:true, args:["--no-sandbox"]});
  const dir=path.resolve(process.env.C3X_VISUAL_OUT || "public");
  fs.mkdirSync(dir,{recursive:true});
  const errors=[];
  const page=await browser.newPage({viewport:{width:1370,height:940},
                                    deviceScaleFactor:1,acceptDownloads:true});
  page.on("pageerror",e=>errors.push(e.message));
  try {
    const response=await page.goto("http://127.0.0.1:8765/",{waitUntil:"networkidle"});
    if(!response || response.status()!==200)throw Error("P3V_HOLD_BROWSER_HTML");
    await page.getByText(/20개 합법 수/).waitFor();
    if(await page.locator("#board > button.square").count()!==64)
      throw Error("P3V_HOLD_BOARD_NOT_EIGHT_BY_EIGHT");
    if(await page.locator("#moveA option").count()!==21)
      throw Error("P3V_HOLD_FULL_LEGAL_SAN_MENU");

    // Genuine user's two-square click selection, not merely API request.
    await page.locator('button.square[title^="e2"]').click();
    await page.locator('button.square[title^="e4"]').click();
    if(await page.locator("#moveA").inputValue()!=="e2e4")
      throw Error("P3V_HOLD_SQUARE_SELECTION_NOT_WRITTEN");
    await page.locator("#moveB").selectOption("d2d4");
    if(await page.locator("#analyze").isDisabled())
      throw Error("P3V_HOLD_CANDIDATES_NOT_ACCEPTED");
    await page.locator("#analyze").click();
    await page.getByText("실제 Stockfish와 체스 규칙 분석이 완료되었습니다.").waitFor({timeout:150000});
    if(await page.locator("#results").isHidden())
      throw Error("P3V_HOLD_RESULT_NOT_RENDERED");
    if(await page.locator("#scores tr").count()!==2)
      throw Error("P3V_HOLD_TWO_ACTUAL_DEPTH_ROWS");
    if(await page.locator("#branches .tile").count()!==2)
      throw Error("P3V_HOLD_TWO_ROOT_RESPONSE_TREES");
    const output=await page.locator("#raw").textContent();
    const parsed=JSON.parse(output);
    if(parsed.engine_report.root_candidates.map(x=>x.move_uci).join(",")!=="e2e4,d2d4")
      throw Error("P3V_HOLD_REAL_ENGINE_CANDIDATE_MISMATCH");
    if(!parsed.evidence.native_stockfish || parsed.evidence.source_engine_internal_causality_proven)
      throw Error("P3V_HOLD_EVIDENCE_TRUTH");

    const downloadPromise=page.waitForEvent("download");
    await page.locator("#export").click();
    const download=await downloadPromise;
    if(!download.suggestedFilename().endsWith(".md"))
      throw Error("P3V_HOLD_MARKDOWN_DOWNLOAD");
    const filepath=path.join(dir,"P3_BROWSER_CLICKED_DOWNLOADED_LEARNER.md");
    await download.saveAs(filepath);
    const markdown=fs.readFileSync(filepath,"utf8");
    if(!markdown.includes("두 후보 수의 차이는 무엇인가") ||
       !markdown.includes("선행연구에서 가져온"))
      throw Error("P3V_HOLD_DOWNLOADED_REPORT_NOT_REAL");
    // P4: actual second-opponent-layer product workflow, separate source
    // search from the simple P3 explanation. The independent Berserk
    // benchmark is an unrelated SHA-frozen offline adjudication; the local
    // interactive tree is always honest about using source Stockfish only.
    if(await page.locator("#strategy").isDisabled())
      throw Error("P4_HOLD_RECURSIVE_TREE_BUTTON_DISABLED");
    const strategyResponse=page.waitForResponse(r=>
      r.url().includes("/api/strategy") && r.request().method()==="POST",
      {timeout:150000});
    await page.locator("#strategy").click();
    const actualResponse=await strategyResponse;
    if(actualResponse.status()!==200)
      throw Error("P4_HOLD_REAL_STRATEGY_API_"+actualResponse.status());
    const tree=await actualResponse.json();
    if(tree.schema!=="c3x030-p4a-cui-inspired-two-opponent-layer-product-tree-v1"||
       tree.total_leaf_paths!==8||
       tree.roots.map(r=>r.root_uci).join(",")!=="e2e4,d2d4")
      throw Error("P4_HOLD_TWO_ROOT_EIGHT_REAL_LEAVES");
    if(tree.roots.some(r=>r.leaf_count!==4 ||
           r.source_work_estimate.opponent_queries!==3 ||
           r.source_work_estimate.player_queries!==6))
      throw Error("P4_HOLD_REAL_NATIVE_SEARCH_QUERY_CONTRACT");
    await page.getByText("두 번째 상대 응수까지 실제 전략나무 검색을 완료했습니다.")
      .waitFor({timeout:150000});
    if(await page.locator("#strategyResult").isHidden())
      throw Error("P4_HOLD_STRATEGY_TREE_HIDDEN");
    if(await page.locator("#strategyResult > .tile").count()!==2)
      throw Error("P4_HOLD_TWO_ROOT_PANELS");
    if(await page.locator("#strategyResult li").count()!==8)
      throw Error("P4_HOLD_EIGHT_BRANCHES_NOT_VISIBLE");
    // P6: genuine browser rendering of the source-SAN-replayed
    // Korean conditional strategy clauses, plus a real user download.
    const annotation=tree.evidence_verified_strategy_explanation;
    if(!annotation ||
       annotation.schema!=="c3x030-p6-evidence-linked-conditional-strategy-annotation-v1" ||
       annotation.fully_replay_verified_annotations!==8 ||
       !tree.evidence_verified_strategy_markdown)
      throw Error("P6_HOLD_MISSING_REPLAY_VERIFIED_STRATEGY_ANNOTATIONS");
    if(await page.locator("#strategyResult .evidence-strategy-clause").count()!==8)
      throw Error("P6_HOLD_EIGHT_ANNOTATIONS_NOT_SHOWN");
    if(await page.locator("#strategyExport").isDisabled())
      throw Error("P6_HOLD_KOREAN_STRATEGY_EXPORT_DISABLED");
    const planDownloadPromise=page.waitForEvent("download");
    await page.locator("#strategyExport").click();
    const planDownload=await planDownloadPromise;
    const planFile=path.join(dir,"P6_BROWSER_DOWNLOADED_REPLAY_VERIFIED_STRATEGY.md");
    await planDownload.saveAs(planFile);
    const planText=fs.readFileSync(planFile,"utf8");
    if(planText!==tree.evidence_verified_strategy_markdown ||
       !planText.includes("상대가") ||
       !planText.includes("인과성"))
      throw Error("P6_HOLD_DOWNLOADED_STRATEGY_DIFFERS_FROM_SOURCE_EVIDENCE");
    fs.writeFileSync(path.join(dir,"P4_BROWSER_ACTUAL_CUI_TWO_LAYER_TREE.json"),
                     JSON.stringify(tree,null,2)+"\\n");
    // P5 actual Martin mirror contrastive-gap robustness audit. This is
    // twelve ADDITIONAL native searches on the selected live original board.
    if(await page.locator("#mirror").isDisabled())
      throw Error("P5_HOLD_MIRROR_BUTTON_DISABLED");
    const mirrorResponse=page.waitForResponse(r=>
      r.url().includes("/api/mirror") && r.request().method()==="POST",
      {timeout:150000});
    await page.locator("#mirror").click();
    const actualMirrorResponse=await mirrorResponse;
    if(actualMirrorResponse.status()!==200)
      throw Error("P5_HOLD_REAL_MIRROR_API_"+actualMirrorResponse.status());
    const symmetry=await actualMirrorResponse.json();
    if(symmetry.original_root_candidates.join(",")!=="e2e4,d2d4"||
       !symmetry.same_semantic_root_player_perspective ||
       Object.keys(symmetry.per_depth).length!==3)
      throw Error("P5_HOLD_MIRROR_ROOT_PERSPECTIVE_OR_DEPTHS");
    await page.getByText("원본·대칭 국면의 평가 차이 민감도 검색을 완료했습니다.")
      .waitFor({timeout:150000});
    if(await page.locator("#mirrorResult").isHidden() ||
       await page.locator("#mirrorResult tbody tr").count()!==3)
      throw Error("P5_HOLD_MIRROR_THREE_DEPTH_ROWS_NOT_RENDERED");
    fs.writeFileSync(path.join(dir,"P5_BROWSER_REAL_MARTIN_MIRROR_GAP.json"),
                     JSON.stringify(symmetry,null,2)+"\\n");
    await page.screenshot({path:path.join(dir,"P3_BROWSER_NATIVE_ENGINE_SCREENSHOT.png"),
                           fullPage:true});
    if(errors.length)throw Error("P3V_HOLD_BROWSER_JS_ERRORS: "+errors.join("; "));

    // Also verify the narrow-screen board is still 64-clickable square UI.
    await page.setViewportSize({width:390,height:844});
    if(await page.locator("#board > button.square").count()!==64)
      throw Error("P3V_HOLD_MOBILE_BOARD_MISSING");
    await page.screenshot({path:path.join(dir,"P3_BROWSER_MOBILE_SCREENSHOT.png"),
                           fullPage:true});
    console.log("C3X_P3V_GENUINE_BROWSER_E2E_PASS",JSON.stringify({
      legal_moves:20,chessboard_squares:64,
      user_clicked_first_move:"e2e4",user_selected_second_move:"d2d4",
      real_root_gap:parsed.engine_report.candidate_A_minus_B_cp_by_depth_or_null,
      real_reply_counts:parsed.engine_report.root_candidates.map(x=>x.opponent_reply_probe.sampled_reply_count),
      rendered_tactical_and_concept_reports:true,
      downloaded_markdown_real:true,
      desktop_and_mobile_screenshots_saved:true,
      actual_p4_strategy_two_layer_leaves:8,
      actual_p4_tree_visible:true,
      actual_p6_rule_verified_korean_clauses:8,
      actual_p6_markdown_downloaded:true,
      actual_p5_mirror_depths:3,
      actual_p5_mirror_renderer:true,
      browser_exceptions:errors.length
    }));
  } finally {
    await browser.close();
  }
})().catch(err=>{console.error(err.stack||String(err));process.exit(1)});
