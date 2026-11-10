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
      browser_exceptions:errors.length
    }));
  } finally {
    await browser.close();
  }
})().catch(err=>{console.error(err.stack||String(err));process.exit(1)});
