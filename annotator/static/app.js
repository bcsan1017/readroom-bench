/* 读人 Bench 标注工具前端（无框架，原生 JS） */
"use strict";

const $ = (sel) => document.querySelector(sel);
const state = {
  items: [],
  itemId: null,
  banned: [],
  truth: null,
  tlEvents: [],
  atEvents: [],
  tlMeta: null,
  mask: null,
  hallu: [],
};

const FIELDS6 = ["gaze", "posture", "hands", "speech", "chips", "face"];
const video = $("#video");

// ---------------- 中文显示映射（底层 JSON 存储保持英文枚举） ----------------
const CN = {
  street: { preflop: "翻前", flop: "翻牌", turn: "转牌", river: "河牌" },
  actor: { hero: "主角", villain: "对手", dealer: "荷官", other: "其他" },
  action: { deal: "发牌", check: "过牌", bet: "下注", raise: "加注", call: "跟注",
    fold: "弃牌", allin: "全下", showdown: "摊牌", pot_awarded: "收池" },
  who: { villain: "对手", hero: "主角", both: "双方", other: "其他" },
  field: { gaze: "视线", posture: "姿态", hands: "手部", speech: "言语",
    chips: "筹码", face: "表情", note: "备注" },
  source: { doubao: "豆包初稿", human: "人工" },
};
const FIELD_BY_CN = {}; // 中文字段名 → 英文 key（含英文自身，解析用）
for (const [k, v] of Object.entries(CN.field)) { FIELD_BY_CN[v] = k; FIELD_BY_CN[k] = k; }

function cn(map, v) { return (CN[map] && CN[map][v]) || String(v == null ? "" : v); }
// 下拉框：值存英文，显示中文
function selCN(options, mapName, value, onchange) {
  const s = el("select", { onchange });
  for (const o of options) s.append(el("option", { value: o, text: cn(mapName, o) }));
  s.value = value;
  return s;
}
function autosize(ta) {
  ta.style.height = "auto";
  ta.style.height = (ta.scrollHeight + 2) + "px";
}

// ---------------- 通用 ----------------
async function api(path, opts) {
  const res = await fetch(path, opts);
  let data = null;
  try { data = await res.json(); } catch (e) { /* ignore */ }
  if (!res.ok) {
    const msg = (data && data.error) ? data.error : `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}
function postJSON(path, body) {
  return api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
function setMsg(sel, text, ok) {
  const el = $(sel);
  el.textContent = text || "";
  el.className = "msg " + (text ? (ok ? "ok" : "err") : "");
  if (text && ok) setTimeout(() => { if (el.textContent === text) { el.textContent = ""; el.className = "msg"; } }, 4000);
}
function el(tag, attrs, ...children) {
  const e = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "text") e.textContent = v;
    else e.setAttribute(k, v);
  }
  for (const c of children) if (c != null) e.append(c);
  return e;
}
function seekTo(t, row) {
  if (!isNaN(t)) { video.currentTime = t; video.pause(); }
  if (row) {
    row.classList.add("flash");
    setTimeout(() => row.classList.remove("flash"), 900);
  }
}
function fmtT(t) {
  const n = Number(t);
  return isNaN(n) ? String(t) : (Math.round(n * 10) / 10).toFixed(1);
}
function checkBanned(text) {
  if (!text || text === "-") return [];
  const low = String(text).toLowerCase();
  return state.banned.filter((w) => low.includes(w.toLowerCase()));
}

// ---------------- 顶部 / 视频 ----------------
video.addEventListener("timeupdate", () => { $("#cur-time").textContent = fmtT(video.currentTime); });

$("#item-select").addEventListener("change", (e) => loadItem(e.target.value));

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === "panel-" + btn.dataset.tab));
  });
});

async function init() {
  try { state.banned = await api("/api/banned"); } catch (e) { state.banned = []; }
  try {
    state.items = await api("/api/items");
  } catch (e) {
    $("#global-msg").textContent = "无法加载 items：" + e.message;
    return;
  }
  const sel = $("#item-select");
  sel.replaceChildren();
  for (const it of state.items) {
    const flags = [];
    if (it.truth_human_verified) flags.push("真值✓");
    if (it.timeline_human_verified) flags.push("轴✓");
    if (it.mask_checked) flags.push("罩✓");
    sel.append(el("option", { value: it.id, text: it.id + (flags.length ? "  [" + flags.join(" ") + "]" : "") }));
  }
  if (state.items.length) loadItem(state.items[0].id);
  else $("#global-msg").textContent = "items/ 下没有条目";
  loadHallu();
}

async function loadItem(id) {
  state.itemId = id;
  $("#item-select").value = id;
  const info = state.items.find((x) => x.id === id) || {};
  $("#video-missing").classList.toggle("hidden", !!info.has_video);
  video.src = "/video/" + id + ".mp4";
  await Promise.all([loadTruth(), loadL0(), loadActionTL(), loadTimeline(), loadMask()]);
  renderCue(); // cue 面板高亮当前 item 无关，但统计不变；只需重绘一次即可
}

// ---------------- 1. 手牌信息核对 ----------------
const POSITIONS = ["", "UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN", "SB", "BB", "straddle"];
const TRUTH_FIELDS = [
  { path: "item_id", label: "条目编号", ro: true },
  // 人数（豆包预填，待人工确认；数不清留空）
  { path: "table_size", label: "桌上人数（豆包预填，待确认）", num: true },
  { path: "players_in_hand", label: "本手入池人数（豆包预填，待确认）", num: true },
  // 位置与开局筹码（Byron 要求：独立可编辑字段，放最上方）
  { path: "hero_position", label: "主角位置（UTG/HJ/CO/BTN/SB/BB…）", datalist: POSITIONS },
  { path: "villain_position", label: "对手位置（UTG/HJ/CO/BTN/SB/BB…）", datalist: POSITIONS },
  { path: "hero_stack_start", label: "主角开局筹码($)", num: true },
  { path: "villain_stack_start", label: "对手开局筹码($)", num: true },
  { path: "hero_cards", label: "主角底牌" },
  { path: "villain_cards", label: "对手底牌" },
  { path: "board", label: "公共牌" },
  { path: "pot_before_allin", label: "全下前底池($)", num: true },
  { path: "to_call", label: "需跟注($)", num: true },
  { path: "bb", label: "大盲($)", num: true },
  { path: "players.hero", label: "主角姓名" },
  { path: "players.villain", label: "对手姓名" },
  { path: "actual.hero_action", label: "实际行动", sel: ["", "call", "fold"], selMap: { "": "（未填）", call: "跟注", fold: "弃牌" } },
  { path: "actual.hero_invested_usd", label: "实际投入($)", num: true },
  { path: "actual.hero_result_usd", label: "实际盈亏($)", num: true },
  { path: "actual.note", label: "实际结果备注", wide: true },
  { path: "difficulty_tier", label: "难度档" },
  { path: "street", label: "全下所在街", ro: true, roMap: "street" },
  { path: "method", label: "胜率算法", ro: true },
  { path: "hero_equity", label: "主角胜率", ro: true },
  { path: "win", label: "赢概率", ro: true },
  { path: "tie", label: "平概率", ro: true },
  { path: "lose", label: "输概率", ro: true },
  { path: "required_equity", label: "所需胜率", ro: true },
  { path: "correct_call", label: "正解=跟注？", ro: true },
  { path: "ev_call_bb", label: "跟注EV(bb)", ro: true },
  { path: "ev_fold_bb", label: "弃牌EV(bb)", ro: true },
  { path: "pot_after_allin", label: "跟注后总底池($)", ro: true },
];
function getPath(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}
function setPath(obj, path, val) {
  const keys = path.split(".");
  let o = obj;
  for (const k of keys.slice(0, -1)) {
    if (typeof o[k] !== "object" || o[k] === null) o[k] = {};
    o = o[k];
  }
  o[keys[keys.length - 1]] = val;
}

async function loadTruth() {
  const form = $("#truth-form");
  form.replaceChildren();
  state.truth = null;
  try {
    state.truth = await api(`/api/item/${state.itemId}/truth`);
  } catch (e) {
    setMsg("#truth-msg", "truth.json 加载失败：" + e.message, false);
    $("#truth-verified-badge").classList.add("hidden");
    return;
  }
  setMsg("#truth-msg", "");
  $("#truth-verified-badge").classList.toggle("hidden", !state.truth.human_verified_truth);
  for (const f of TRUTH_FIELDS) {
    const v = getPath(state.truth, f.path);
    const id = "tf-" + f.path.replace(/\./g, "-");
    let input;
    if (f.sel) {
      input = el("select", { id });
      for (const o of f.sel) input.append(el("option", { value: o, text: (f.selMap && f.selMap[o]) || o }));
      input.value = v == null ? "" : String(v);
    } else {
      input = el("input", {
        type: "text", id,
        value: v === undefined || v === null ? "" : String(v),
      });
      if (f.datalist) {
        const dlId = id + "-dl";
        input.setAttribute("list", dlId);
        const dl = el("datalist", { id: dlId });
        for (const o of f.datalist) if (o) dl.append(el("option", { value: o }));
        input._dl = dl; // datalist 挂在 field 里
      }
    }
    if (f.ro) {
      input.readOnly = true; input.classList.add("readonly");
      if (f.roMap && v != null && CN[f.roMap] && CN[f.roMap][v]) input.value = `${cn(f.roMap, v)}（${v}）`;
    }
    const fieldDiv = el("div", { class: "field" + (f.wide ? " wide" : "") },
      el("label", { text: f.label }), input);
    if (input._dl) fieldDiv.append(input._dl);
    form.append(fieldDiv);
  }
  state.tablePlayers = Array.isArray(state.truth._table_players) ? state.truth._table_players : [];
  state.internalNames = (state.truth._internal_names && typeof state.truth._internal_names === "object")
    ? state.truth._internal_names : {};
  renderTablePlayers();
  renderBettingLine();
}

// ---- 在座玩家与筹码（存 item.json：table_players 角色+筹码；internal_names 姓名仅核对） ----
const TP_ROLES = ["hero", "villain", "other_1", "other_2", "other_3", "other_4", "other_5", "other_6", "other_7"];
function tpRoleLabel(r) {
  if (r === "hero") return "主角";
  if (r === "villain") return "对手";
  const m = /^other_(\d+)$/.exec(r || "");
  return m ? "其他" + m[1] : String(r || "");
}
function renderTablePlayers() {
  const tbody = $("#tp-tbody");
  tbody.replaceChildren();
  const list = state.tablePlayers || [];
  const names = state.internalNames || {};
  list.forEach((p, i) => {
    const tr = el("tr");
    const roleSel = el("select", { onchange: (e) => { p.role = e.target.value; } });
    for (const r of TP_ROLES) roleSel.append(el("option", { value: r, text: tpRoleLabel(r) }));
    roleSel.value = TP_ROLES.includes(p.role) ? p.role : "other_1";
    tr.append(el("td", null, roleSel));
    tr.append(el("td", null, el("input", { type: "text", value: names[p.role] || "",
      placeholder: "（豆包没读出）",
      oninput: (e) => { state.internalNames[p.role] = e.target.value; } })));
    tr.append(el("td", null, el("input", { class: "amt-input", type: "text",
      value: p.stack == null ? "" : String(p.stack),
      oninput: (e) => { const n = Number(e.target.value); p.stack = e.target.value === "" || isNaN(n) ? null : n; } })));
    tr.append(el("td", null, el("button", { class: "danger", text: "删", onclick: () => {
      list.splice(i, 1); renderTablePlayers();
    } })));
    tbody.append(tr);
  });
  if (!list.length)
    tbody.append(el("tr", null, el("td", { colspan: "4", text: "（暂无，豆包读不出时请人工补）" })));
}
$("#btn-tp-add").addEventListener("click", () => {
  state.tablePlayers = state.tablePlayers || [];
  const used = new Set(state.tablePlayers.map((p) => p.role));
  const role = TP_ROLES.find((r) => !used.has(r)) || "other_1";
  state.tablePlayers.push({ role, stack: null });
  renderTablePlayers();
});

// ---- 下注线按街分块（存 truth.betting_line，英文枚举，显示中文） ----
const BL_ACTIONS = ["check", "bet", "raise", "call", "fold", "allin"];
function renderBettingLine() {
  const wrap = $("#bl-blocks");
  wrap.replaceChildren();
  if (!state.truth) return;
  if (typeof state.truth.betting_line !== "object" || state.truth.betting_line === null || Array.isArray(state.truth.betting_line)) {
    state.truth.betting_line = {};
  }
  const bl = state.truth.betting_line;
  for (const st of ACT_STREETS) {
    if (typeof bl[st] !== "object" || bl[st] === null) bl[st] = { board: "", actions: [], l0_text: null, source: null };
    const blk = bl[st];
    if (!Array.isArray(blk.actions)) blk.actions = [];
    const head = el("div", { class: "bl-head" },
      el("b", { text: cn("street", st) }),
      el("span", { class: "bl-board", text: blk.board ? "牌面 " + blk.board : (st === "preflop" ? "" : "牌面 未知") }),
      blk.source ? el("span", { class: "badge gray", text: blk.source === "video_extracted" ? "视频提取" : blk.source }) : null,
      el("button", { text: "加一行", onclick: () => {
        blk.actions.push({ t: null, actor: "hero", action: "check", amount: null, source: "human" });
        renderBettingLine();
      } }),
      blk.l0_text ? el("span", { class: "bl-l0", text: "已知信息：" + blk.l0_text }) : null,
    );
    const tbody = el("tbody");
    blk.actions.forEach((a, i) => {
      const tr = el("tr", { onclick: (e) => {
        if (["INPUT", "SELECT", "BUTTON", "OPTION"].includes(e.target.tagName)) return;
        if (a.t != null) seekTo(Number(a.t));
      } });
      tr.append(el("td", null, el("input", { class: "t-input", type: "text",
        value: a.t == null ? "" : String(a.t),
        oninput: (e) => { const n = Number(e.target.value); a.t = e.target.value === "" || isNaN(n) ? null : Math.round(n * 10) / 10; } })));
      tr.append(el("td", null, selCN(["hero", "villain", "other"], "actor", a.actor || "hero", (e) => { a.actor = e.target.value; })));
      tr.append(el("td", null, selCN(BL_ACTIONS, "action", a.action || "check", (e) => { a.action = e.target.value; })));
      tr.append(el("td", null, el("input", { class: "amt-input", type: "text",
        value: a.amount == null ? "" : String(a.amount),
        oninput: (e) => { const n = Number(e.target.value); a.amount = e.target.value === "" || isNaN(n) ? null : n; } })));
      tr.append(el("td", null,
        el("button", { text: "▶", title: "视频跳到该时刻", onclick: (e) => { e.stopPropagation(); if (a.t != null) seekTo(Number(a.t)); } }),
        " ",
        el("button", { class: "danger", text: "删", onclick: (e) => { e.stopPropagation(); blk.actions.splice(i, 1); renderBettingLine(); } })));
      tbody.append(tr);
    });
    const table = el("table", null,
      el("thead", null, el("tr", null,
        ...["时间(秒)", "角色", "动作", "金额($)", "操作"].map((h) => el("th", { text: h })))),
      tbody);
    const block = el("div", { class: "bl-block" }, head);
    if (blk.actions.length) block.append(table);
    else block.append(el("div", { class: "bl-empty", text: "（本街无下注动作记录）" }));
    wrap.append(block);
  }
}
function truthFormValue(path) {
  const inp = $("#tf-" + path.replace(/\./g, "-"));
  return inp ? inp.value.trim() : "";
}
function collectTruthForm() {
  const t = JSON.parse(JSON.stringify(state.truth || {}));
  for (const f of TRUTH_FIELDS) {
    if (f.ro) continue;
    const raw = truthFormValue(f.path);
    if (f.num) {
      const n = Number(raw);
      setPath(t, f.path, raw === "" ? null : (isNaN(n) ? raw : n));
    } else {
      setPath(t, f.path, raw);
    }
  }
  t._table_players = state.tablePlayers || [];
  t._internal_names = state.internalNames || {};
  if (t._table_players.length) t.table_size = t._table_players.length; // 桌上人数由玩家表长度导出
  return t;
}
$("#btn-recompute").addEventListener("click", async () => {
  if (!state.truth) return;
  setMsg("#truth-msg", "重算中…", true);
  try {
    const res = await postJSON(`/api/item/${state.itemId}/recompute`, {
      hero: truthFormValue("hero_cards"),
      villain: truthFormValue("villain_cards"),
      board: truthFormValue("board"),
      pot: Number(truthFormValue("pot_before_allin")),
      call: Number(truthFormValue("to_call")),
      bb: Number(truthFormValue("bb")) || 1,
    });
    if (res.error) { setMsg("#truth-msg", "重算失败：" + res.error, false); return; }
    Object.assign(state.truth, res);
    for (const f of TRUTH_FIELDS) {
      if (!f.ro) continue;
      const inp = $("#tf-" + f.path.replace(/\./g, "-"));
      const v = getPath(state.truth, f.path);
      if (inp && v !== undefined) inp.value = String(v);
    }
    setMsg("#truth-msg", "重算完成，只读字段已回填（尚未保存）", true);
  } catch (e) {
    setMsg("#truth-msg", "重算失败：" + e.message, false);
  }
});
$("#btn-truth-save").addEventListener("click", async () => {
  if (!state.truth) return;
  const t = collectTruthForm();
  t.human_verified_truth = true;
  try {
    await postJSON(`/api/item/${state.itemId}/truth`, t);
    state.truth = t;
    $("#truth-verified-badge").classList.remove("hidden");
    setMsg("#truth-msg", "已保存 truth.json（首次保存自动备份 truth.json.bak）", true);
  } catch (e) {
    setMsg("#truth-msg", "保存失败：" + e.message, false);
  }
});

// ---------------- 1b. L0 手牌全文 ----------------
async function loadL0() {
  const ta = $("#l0-text");
  ta.value = "";
  $("#l0-verified-badge").classList.add("hidden");
  try {
    const data = await api(`/api/item/${state.itemId}/l0`);
    ta.value = data.text || "";
    $("#l0-verified-badge").classList.toggle("hidden", !data.human_verified);
    setMsg("#l0-msg", "");
  } catch (e) {
    setMsg("#l0-msg", "L0 加载失败：" + e.message, false);
  }
}
$("#btn-l0-save").addEventListener("click", async () => {
  try {
    await postJSON(`/api/item/${state.itemId}/l0`, { text: $("#l0-text").value });
    $("#l0-verified-badge").classList.remove("hidden");
    setMsg("#l0-msg", "已写回 item.json layers.L0.text（首次保存自动备份 item.json.bak）", true);
  } catch (e) {
    setMsg("#l0-msg", "保存失败：" + e.message, false);
  }
});

// ---------------- 1c. 行动时间线 ----------------
const ACT_STREETS = ["preflop", "flop", "turn", "river"];
const ACT_ACTORS = ["hero", "villain", "dealer", "other"];
const ACT_ACTIONS = ["deal", "check", "bet", "raise", "call", "fold", "allin", "showdown", "pot_awarded"];

async function loadActionTL() {
  state.atEvents = [];
  try {
    const data = await api(`/api/item/${state.itemId}/action_timeline`);
    state.atEvents = data.events || [];
  } catch (e) {
    setMsg("#at-msg", "行动时间线加载失败：" + e.message, false);
  }
  renderActionTL();
}
function selEl(options, value, onchange) {
  const s = el("select", { onchange });
  for (const o of options) s.append(el("option", { value: o, text: o }));
  s.value = value;
  return s;
}
function renderActionTL() {
  const tbody = $("#at-tbody");
  tbody.replaceChildren();
  state.atEvents.forEach((ev, i) => {
    const tr = el("tr", {
      onclick: (e) => {
        if (["INPUT", "SELECT", "BUTTON", "OPTION"].includes(e.target.tagName)) return;
        if (ev.t != null) seekTo(Number(ev.t), tr);
      },
    });
    // t：可输入 + ⇔ 拖动手柄（拖动时视频实时跟随）
    const tIn = el("input", { class: "t-input", type: "text",
      value: ev.t == null ? "" : String(ev.t),
      oninput: (e) => { const n = Number(e.target.value); if (e.target.value !== "" && !isNaN(n)) ev.t = Math.round(n * 10) / 10; } });
    const handle = el("span", { class: "drag-handle", text: "⇔", title: "左右拖动微调秒数" });
    handle.addEventListener("pointerdown", (e) => {
      e.preventDefault(); e.stopPropagation();
      handle.setPointerCapture(e.pointerId);
      const x0 = e.clientX, t0 = Number(ev.t) || 0;
      const onMove = (me) => {
        let t = t0 + (me.clientX - x0) * 0.05; // 20px = 1s
        t = Math.max(0, Math.min(video.duration || 1e9, t));
        ev.t = Math.round(t * 10) / 10;
        tIn.value = String(ev.t);
        video.currentTime = ev.t;
      };
      const onUp = () => {
        handle.removeEventListener("pointermove", onMove);
        handle.removeEventListener("pointerup", onUp);
      };
      handle.addEventListener("pointermove", onMove);
      handle.addEventListener("pointerup", onUp);
    });
    tr.append(el("td", { class: "t-cell" }, tIn, handle));
    tr.append(el("td", null, selCN(ACT_STREETS, "street", ev.street, (e) => { ev.street = e.target.value; })));
    tr.append(el("td", null, selCN(ACT_ACTORS, "actor", ev.actor, (e) => { ev.actor = e.target.value; })));
    tr.append(el("td", null, selCN(ACT_ACTIONS, "action", ev.action, (e) => { ev.action = e.target.value; })));
    tr.append(el("td", null, el("input", { class: "amt-input", type: "text",
      value: ev.amount == null ? "" : String(ev.amount),
      oninput: (e) => { const n = Number(e.target.value); ev.amount = e.target.value === "" || isNaN(n) ? null : n; } })));
    tr.append(el("td", null, el("span", {
      class: ev.source === "human" ? "src-human" : "src-doubao",
      text: cn("source", ev.source === "human" ? "human" : "doubao"),
    })));
    tr.append(el("td", null,
      el("button", { text: "▶", title: "视频跳到 t", onclick: (e) => { e.stopPropagation(); if (ev.t != null) seekTo(Number(ev.t), tr); } }),
      " ",
      el("button", { text: "取当前", title: "把 t 设为当前播放时间", onclick: (e) => {
        e.stopPropagation();
        ev.t = Math.round((video.currentTime || 0) * 10) / 10;
        ev.source = "human";
        renderActionTL();
      } }),
      " ",
      el("button", { text: "插行", title: "在此行后插入", onclick: (e) => {
        e.stopPropagation();
        state.atEvents.splice(i + 1, 0, { t: ev.t, street: ev.street, actor: "hero", action: "check",
          amount: null, source: "human", human_verified: false });
        renderActionTL();
      } }),
      " ",
      el("button", { class: "danger", text: "删", onclick: (e) => {
        e.stopPropagation();
        state.atEvents.splice(i, 1);
        renderActionTL();
      } }),
    ));
    tbody.append(tr);
  });
  if (!state.atEvents.length) {
    tbody.append(el("tr", null, el("td", { colspan: "7", text: "（无 action_timeline.jsonl，可用上方按钮新建，或跑 python -m pipeline.action_timeline --hand <id>）" })));
  }
}
$("#btn-at-add-now").addEventListener("click", () => {
  const t = Math.round((video.currentTime || 0) * 10) / 10;
  const ev = { t, street: "preflop", actor: "hero", action: "check", amount: null, source: "human", human_verified: false };
  const idx = state.atEvents.findIndex((x) => x.t != null && Number(x.t) > t);
  if (idx === -1) state.atEvents.push(ev); else state.atEvents.splice(idx, 0, ev);
  renderActionTL();
});
$("#btn-at-save").addEventListener("click", async () => {
  try {
    const res = await postJSON(`/api/item/${state.itemId}/action_timeline`, { events: state.atEvents });
    setMsg("#at-msg", `已保存 ${res.n_events} 条动作到 action_timeline.jsonl（已标记人工校准）`, true);
    await loadActionTL();
  } catch (e) {
    setMsg("#at-msg", "保存失败：" + e.message, false);
  }
});

// ---------------- 2. 时间轴校准 ----------------
async function loadTimeline() {
  state.tlEvents = [];
  state.tlMeta = null;
  try {
    const data = await api(`/api/item/${state.itemId}/timeline`);
    state.tlEvents = data.events || [];
    state.tlMeta = data.meta;
  } catch (e) {
    setMsg("#tl-msg", "时间轴加载失败：" + e.message, false);
  }
  renderTimeline();
}
function tlMetaLine() {
  const m = state.tlMeta;
  if (!m) return "meta：无 timeline_meta.json";
  const parts = [
    "模型：" + (m.model || "未知"),
    "生成时间：" + (m.generated_at || "未知"),
    "事件数：" + (m.n_events != null ? m.n_events : state.tlEvents.length),
    m.human_verified ? "✅ 已人工校准" : "⚠️ 未人工校准",
  ];
  if (m.banned_hits && m.banned_hits.length) parts.push("生成期禁用词命中：" + m.banned_hits.length);
  return "meta：" + parts.join(" ｜ ");
}
function newEvent(t) {
  return { t: Math.round(t * 10) / 10, who: "villain", gaze: "-", posture: "-", hands: "-",
    speech: "-", chips: "-", face: "-", note: "", source: "human", human_verified: false };
}
// 事件六字段+备注 ↔ 「字段: 内容」多行文本（只列有内容的字段；中文字段名，解析时中英文都认）
function evToText(ev) {
  const lines = [];
  for (const k of [...FIELDS6, "note"]) {
    const v = ev[k];
    if (v != null && String(v).trim() !== "" && String(v).trim() !== "-")
      lines.push(cn("field", k) + ": " + v);
  }
  return lines.join("\n");
}
function textToEv(text, ev) {
  const vals = {};
  let cur = null;
  for (const raw of String(text).split("\n")) {
    const m = raw.match(/^\s*(视线|姿态|手部|言语|筹码|表情|备注|gaze|posture|hands|speech|chips|face|note)\s*[:：]\s?(.*)$/);
    if (m) { cur = FIELD_BY_CN[m[1]]; vals[cur] = m[2]; }
    else if (raw.trim() !== "") {
      if (cur == null) cur = "note";
      vals[cur] = (vals[cur] ? vals[cur] + " " : "") + raw.trim();
    }
  }
  for (const k of FIELDS6) ev[k] = (k in vals && String(vals[k]).trim() !== "") ? vals[k].trim() : "-";
  ev.note = (("note" in vals) && String(vals.note).trim() !== "") ? vals.note.trim() : "";
}
function renderTimeline() {
  $("#tl-meta").textContent = tlMetaLine();
  const tbody = $("#tl-tbody");
  tbody.replaceChildren();
  state.tlEvents.forEach((ev, i) => {
    const tr = el("tr", {
      onclick: (e) => {
        if (["INPUT", "SELECT", "BUTTON", "OPTION", "TEXTAREA"].includes(e.target.tagName)) return;
        seekTo(Number(ev.t), tr);
      },
    });
    // t
    const tIn = el("input", { class: "t-input", type: "text", value: String(ev.t),
      oninput: (e) => { const n = Number(e.target.value); if (!isNaN(n)) ev.t = n; } });
    tr.append(el("td", null, tIn));
    // who（显示中文，存英文）
    tr.append(el("td", null, selCN(["villain", "hero", "both", "other"], "who", ev.who, (e) => { ev.who = e.target.value; })));
    // 观察内容：单个自动伸缩 textarea，「字段: 内容」一行一条，完整可见可编辑
    const ta = el("textarea", { class: "ev-text", rows: "1", spellcheck: "false",
      oninput: (e) => { textToEv(e.target.value, ev); autosize(e.target); validateBanned(); } });
    ta.value = evToText(ev);
    ta.dataset.row = String(i);
    tr.append(el("td", null, ta));
    // source
    tr.append(el("td", null, el("span", {
      class: ev.source === "human" ? "src-human" : "src-doubao",
      text: cn("source", ev.source === "human" ? "human" : "doubao"),
    })));
    // 操作
    tr.append(el("td", null,
      el("button", { text: "▶", title: "视频跳到 t", onclick: (e) => { e.stopPropagation(); seekTo(Number(ev.t), tr); } }),
      " ",
      el("button", { text: "插行", title: "在此行后插入", onclick: (e) => {
        e.stopPropagation();
        state.tlEvents.splice(i + 1, 0, newEvent(Number(ev.t) || 0));
        renderTimeline();
      } }),
      " ",
      el("button", { class: "danger", text: "删", onclick: (e) => {
        e.stopPropagation();
        state.tlEvents.splice(i, 1);
        renderTimeline();
      } }),
    ));
    tbody.append(tr);
  });
  if (!state.tlEvents.length) {
    tbody.append(el("tr", null, el("td", { colspan: "5", text: "（无事件，可用上方按钮新建）" })));
  }
  requestAnimationFrame(() => {
    document.querySelectorAll("#tl-tbody textarea.ev-text").forEach(autosize);
  });
  validateBanned();
}
function validateBanned() {
  const warn = $("#tl-banned-warn");
  const hits = [];
  document.querySelectorAll("#tl-tbody textarea.ev-text").forEach((inp) => {
    const words = checkBanned(inp.value);
    inp.classList.toggle("banned-hit", words.length > 0);
    if (words.length) hits.push(`第${Number(inp.dataset.row) + 1}行: ${words.join("/")}`);
  });
  if (hits.length) {
    warn.textContent = "⚠️ 命中禁用词（客观事实描述，不许推断情绪/牌力）：" + hits.join("；");
    warn.classList.remove("hidden");
  } else {
    warn.classList.add("hidden");
  }
  return hits.length === 0;
}
$("#btn-tl-add-now").addEventListener("click", () => {
  const ev = newEvent(video.currentTime || 0);
  const idx = state.tlEvents.findIndex((x) => Number(x.t) > ev.t);
  if (idx === -1) state.tlEvents.push(ev); else state.tlEvents.splice(idx, 0, ev);
  renderTimeline();
});
$("#btn-tl-save").addEventListener("click", async () => {
  if (!validateBanned() && !confirm("存在禁用词命中，确定仍要保存？")) return;
  try {
    const res = await postJSON(`/api/item/${state.itemId}/timeline`, { events: state.tlEvents });
    setMsg("#tl-msg", `已保存 ${res.n_events} 条事件（timeline.jsonl + timeline.txt${res.item_json_synced ? " + item.json 已同步" : ""}，已标记人工校准）`, true);
    await loadTimeline();
  } catch (e) {
    setMsg("#tl-msg", "保存失败：" + e.message, false);
  }
});

// ---------------- 3. 遮罩检查 ----------------
async function loadMask() {
  try {
    state.mask = await api(`/api/item/${state.itemId}/mask_review`);
  } catch (e) {
    state.mask = { item_id: state.itemId, checked: false, leaks: [], updated_at: null };
  }
  renderMask();
}
function renderMask() {
  $("#mask-checked").checked = !!state.mask.checked;
  const concl = $("#mask-conclusion");
  if (!state.mask.checked) concl.textContent = "（未检查完毕）";
  else concl.textContent = state.mask.leaks.length
    ? `结论：有泄露（${state.mask.leaks.length} 处）` : "结论：已检查完毕，无泄露";
  concl.style.color = state.mask.checked ? (state.mask.leaks.length ? "var(--red)" : "var(--green)") : "";
  if (state.mask.updated_at) concl.textContent += `　上次保存：${state.mask.updated_at}`;
  const tbody = $("#mask-tbody");
  tbody.replaceChildren();
  state.mask.leaks.forEach((lk, i) => {
    const tr = el("tr", { onclick: (e) => {
      if (["INPUT", "BUTTON"].includes(e.target.tagName)) return;
      seekTo(Number(lk.t), tr);
    } });
    tr.append(el("td", { text: fmtT(lk.t) + "s" }));
    tr.append(el("td", null, el("input", { type: "text", value: lk.note || "",
      oninput: (e) => { lk.note = e.target.value; } })));
    tr.append(el("td", null,
      el("button", { text: "▶", onclick: (e) => { e.stopPropagation(); seekTo(Number(lk.t), tr); } }),
      " ",
      el("button", { class: "danger", text: "删", onclick: (e) => {
        e.stopPropagation(); state.mask.leaks.splice(i, 1); renderMask();
      } })));
    tbody.append(tr);
  });
  if (!state.mask.leaks.length)
    tbody.append(el("tr", null, el("td", { colspan: "3", text: "（暂无泄露点）" })));
}
$("#btn-mask-mark").addEventListener("click", () => {
  state.mask.leaks.push({ t: Math.round((video.currentTime || 0) * 10) / 10, note: $("#mask-note").value.trim() });
  state.mask.leaks.sort((a, b) => a.t - b.t);
  $("#mask-note").value = "";
  renderMask();
});
$("#mask-checked").addEventListener("change", (e) => { state.mask.checked = e.target.checked; renderMask(); });
$("#btn-mask-save").addEventListener("click", async () => {
  try {
    const res = await postJSON(`/api/item/${state.itemId}/mask_review`, state.mask);
    state.mask.updated_at = res.updated_at;
    renderMask();
    setMsg("#mask-msg", "已保存 mask_review.json", true);
  } catch (e) {
    setMsg("#mask-msg", "保存失败：" + e.message, false);
  }
});

// ---------------- 4. cue 核验 ----------------
async function loadHallu() {
  try {
    state.hallu = await api("/api/hallucination");
  } catch (e) {
    state.hallu = [];
    setMsg("#cue-msg", "hallucination.jsonl 加载失败：" + e.message, false);
  }
  renderCue();
}
function cueStats() {
  const rows = state.hallu;
  const total = rows.length;
  const judgeFalse = rows.filter((r) => r.judge && r.judge.exists === false).length;
  const reviewed = rows.filter((r) => r.human != null).length;
  const sampled = rows.filter((r) => r.sampled_for_review).length;
  const sampledReviewed = rows.filter((r) => r.sampled_for_review && r.human != null).length;
  const pct = (a, b) => (b ? ((a / b) * 100).toFixed(1) + "%" : "-");
  return { total, judgeFalse, reviewed, sampled, sampledReviewed, pct };
}
function renderCueStats() {
  const s = cueStats();
  const box = $("#cue-stats");
  box.replaceChildren(
    el("span", { class: "stat" }, "总 cue 数：", el("b", { text: String(s.total) })),
    el("span", { class: "stat" }, "judge 判 false：", el("b", { text: `${s.judgeFalse}（${s.pct(s.judgeFalse, s.total)}）` })),
    el("span", { class: "stat" }, "人工已复核：", el("b", { text: `${s.reviewed}/${s.total}（${s.pct(s.reviewed, s.total)}）` })),
    el("span", { class: "stat" }, "抽检样本复核：", el("b", { text: `${s.sampledReviewed}/${s.sampled}（${s.pct(s.sampledReviewed, s.sampled)}）` })),
    el("span", { class: "hint", text: "目标：人工抽检覆盖全部 cue 的 10–20%" }),
  );
}
function renderCue() {
  renderCueStats();
  const wrap = $("#cue-groups");
  wrap.replaceChildren();
  if (!state.hallu.length) {
    wrap.append(el("p", { class: "meta-line", text: "results/hallucination.jsonl 为空或不存在（评测跑完后自动生成）。" }));
    return;
  }
  const groups = new Map();
  state.hallu.forEach((row, idx) => {
    const key = `${row.model || "?"} ｜ ${row.layer || "?"} ｜ trial ${row.trial != null ? row.trial : "?"}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push([idx, row]);
  });
  for (const [key, pairs] of groups) {
    const tbody = el("tbody");
    for (const [idx, row] of pairs) {
      const cue = row.cue || {};
      const judge = row.judge || {};
      const tr = el("tr", { onclick: (e) => {
        if (["INPUT", "SELECT", "BUTTON", "OPTION"].includes(e.target.tagName)) return;
        if (row.item_id && row.item_id !== state.itemId) loadItem(row.item_id).then(() => seekTo(Number(cue.t), tr));
        else seekTo(Number(cue.t), tr);
      } });
      const jcls = judge.exists === false ? "judge-false" : judge.exists === true ? "judge-true" : "judge-uncertain";
      const jtxt = judge.exists === false ? "幻觉" : judge.exists === true ? "存在" : "不确定";
      const humanSel = el("select", { onchange: (e) => {
        const v = e.target.value;
        if (v === "keep") row.human = null;
        else row.human = { exists: v === "uncertain" ? "uncertain" : v === "true",
          note: (row.human && row.human.note) || "" };
        renderCueStats();
        noteIn.disabled = v === "keep";
      } });
      humanSel.append(
        el("option", { value: "keep", text: "维持 judge" }),
        el("option", { value: "true", text: "确认存在" }),
        el("option", { value: "false", text: "判为幻觉" }),
        el("option", { value: "uncertain", text: "不确定" }));
      humanSel.value = row.human == null ? "keep"
        : row.human.exists === true ? "true"
        : row.human.exists === false ? "false" : "uncertain";
      const noteIn = el("input", { type: "text", placeholder: "复核备注",
        value: (row.human && row.human.note) || "",
        oninput: (e) => { if (row.human) row.human.note = e.target.value; } });
      noteIn.disabled = row.human == null;
      tr.append(
        el("td", { text: String(row.item_id || "") }),
        el("td", { text: cue.t != null ? fmtT(cue.t) + "s" : "-" }),
        el("td", { text: cue.who ? cn("who", cue.who) : "-" }),
        el("td", { text: cue.type ? (CN.field[cue.type] || cue.type) : "-" }),
        el("td", { text: cue.observed || "-" }),
        el("td", { text: cue.direction || "-" }),
        el("td", { text: cue.weight != null ? String(cue.weight) : "-" }),
        el("td", null, el("span", { class: jcls, text: jtxt })),
        el("td", null, el("span", { class: "evidence", text: judge.evidence || "" })),
        el("td", { text: row.sampled_for_review ? "抽检" : "" }),
        el("td", null, humanSel),
        el("td", null, noteIn),
      );
      tbody.append(tr);
    }
    wrap.append(el("div", { class: "cue-group" },
      el("h3", { text: key + `（${pairs.length} 条）` }),
      el("div", { class: "table-wrap" },
        el("table", null,
          el("thead", null, el("tr", null,
            ...["条目", "时间", "谁", "类型", "观察内容", "方向", "权重",
              "判定", "证据", "抽检", "人工改判", "备注"].map((h) => el("th", { text: h })))),
          tbody))));
  }
}
$("#btn-cue-reload").addEventListener("click", loadHallu);
$("#btn-cue-save").addEventListener("click", async () => {
  try {
    const res = await postJSON("/api/hallucination", state.hallu);
    setMsg("#cue-msg", `已保存 ${res.n} 行到 results/hallucination.jsonl`, true);
  } catch (e) {
    setMsg("#cue-msg", "保存失败：" + e.message, false);
  }
});

init();
