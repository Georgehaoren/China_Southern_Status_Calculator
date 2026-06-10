"use strict";

const state = {
  rules: null,
  partners: null,
  carriers: null,
  codeshare784: null,
  mileageTools: null,
  partnerStatus: null,
  dataSources: null,
  lastResult: null,
  calculating: false,
};

const tierOrder = ["BASE", "SILVER", "GOLD", "PLATINUM"];
const DRAFT_KEY = "cz_status_plan_draft_v22_import_cost_split";

function $(id) {
  return document.getElementById(id);
}

function applyTableDataLabels(root = document) {
  const tables = root.querySelectorAll ? root.querySelectorAll("table") : [];
  tables.forEach(table => {
    const headers = [...table.querySelectorAll("thead th")].map(th => th.textContent.trim());
    table.querySelectorAll("tbody tr").forEach(tr => {
      [...tr.children].forEach((td, index) => {
        if (headers[index]) td.setAttribute("data-label", headers[index]);
      });
    });
  });
}

function updateScrollableHints() {
  document.querySelectorAll(".table-wrap, .result-table").forEach(el => {
    const isScrollable = el.scrollWidth > el.clientWidth + 4;
    el.classList.toggle("is-scrollable", isScrollable);
  });
}

function refreshResponsiveTables(root = document) {
  applyTableDataLabels(root);
  window.requestAnimationFrame(updateScrollableHints);
}


function setBootStatus(message, level = "info") {
  const el = $("js-boot-banner");
  if (!el) return;
  el.textContent = message;
  el.className = `boot-banner ${level}`;
}

function showError(message, details = "") {
  console.error(message, details);
  setBootStatus(`前端错误：${message}`, "error");
  const line = $("status-line");
  if (line) {
    line.className = "status-line bad";
    line.innerHTML = `<strong>前端或接口错误：</strong>${escapeHtml(message)}${details ? `<br><small>${escapeHtml(String(details)).slice(0, 1000)}</small>` : ""}`;
  }
}

window.addEventListener("error", (event) => {
  showError(event.message || "Uncaught JavaScript error", `${event.filename || ""}:${event.lineno || ""}:${event.colno || ""}`);
});

window.addEventListener("unhandledrejection", (event) => {
  const reason = event.reason || "Unhandled promise rejection";
  showError(reason.message || String(reason), reason.stack || "");
});

function fmtNumber(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString("zh-CN", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (err) {
    throw new Error(`${url} 返回的不是合法 JSON：${text.slice(0, 300)}`);
  }
  if (!response.ok) {
    const msg = data && (data.message || data.error) ? `${data.error || "Error"}: ${data.message || ""}` : response.statusText;
    throw new Error(`${url} 请求失败：HTTP ${response.status} ${msg}`);
  }
  return data;
}

function tierOptions(select, defaultValue = "") {
  if (!select) return;
  select.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "请选择";
  select.appendChild(placeholder);

  const tiers = state.rules && state.rules.tiers ? state.rules.tiers : {};
  for (const code of tierOrder) {
    const tier = tiers[code];
    if (!tier) continue;
    const option = document.createElement("option");
    option.value = code;
    option.textContent = `${tier.name_cn || code} (${code})`;
    select.appendChild(option);
  }
  select.value = [...select.options].some(o => o.value === defaultValue) ? defaultValue : "";
}

function readSettings() {
  return {
    current_tier: $("current_tier")?.value || "",
    member_tier: $("member_tier")?.value || "",
    target_tier: $("target_tier")?.value || "",
    retention_year: $("retention_year")?.value || "",
    current_qualifying_miles: Number($("current_qualifying_miles")?.value || 0),
    current_qualifying_segments: Number($("current_qualifying_segments")?.value || 0),
    carryover_miles: Number($("carryover_miles")?.value || 0),
    carryover_segments: Number($("carryover_segments")?.value || 0),
    items: readRows(),
  };
}

function readRows() {
  return [...document.querySelectorAll("#items-body tr")]
    .map((tr, index) => {
      const row = {
        id: `row-${index + 1}`,
        name: tr.querySelector(".name")?.value || "",
        count: Number(tr.querySelector(".count")?.value || 0),
        product_type: tr.querySelector(".product_type")?.value || "",
        earning_mode: tr.querySelector(".earning_mode")?.value || "",
        marketing_carrier: tr.querySelector(".marketing_carrier")?.value || "",
        operating_carrier: tr.querySelector(".operating_carrier")?.value || "",
        origin_airport: tr.querySelector(".origin_airport")?.value || "",
        destination_airport: tr.querySelector(".destination_airport")?.value || "",
        standard_miles_source: tr.querySelector(".standard_miles_source")?.value || "unknown",
        standard_miles_note: tr.querySelector(".standard_miles_note")?.value || "",
        flight_number: tr.querySelector(".flight_number")?.value || "",
        cost_group: tr.querySelector(".cost_group")?.value || "",
        cost_input_mode: tr.querySelector(".cost_input_mode")?.value || "per_unit",
        mileage_tool_code: tr.querySelector(".mileage_tool_code")?.value || "",
        ticket_prefix: tr.querySelector(".ticket_prefix")?.value || "",
        booking_class: tr.querySelector(".booking_class")?.value || "",
        standard_miles: Number(tr.querySelector(".standard_miles")?.value || 0),
        cash_amount: Number(tr.querySelector(".cash_amount")?.value || 0),
        manual_qualifying_miles: Number(tr.querySelector(".manual_qualifying_miles")?.value || 0),
        manual_qualifying_segments: Number(tr.querySelector(".manual_qualifying_segments")?.value || 0),
        manual_award_miles: Number(tr.querySelector(".manual_award_miles")?.value || 0),
      };
      return row;
    })
    // 新增空白行用于录入，不把完全空白行送到后端计算 / Blank rows are for editing only.
    .filter(row => !isCompletelyBlankRow(row));
}

function isCompletelyBlankRow(row) {
  const textFields = [
    row.name,
    row.product_type,
    row.earning_mode,
    row.marketing_carrier,
    row.operating_carrier,
    row.origin_airport,
    row.destination_airport,
    row.standard_miles_source === "unknown" ? "" : row.standard_miles_source,
    row.standard_miles_note,
    row.flight_number,
    row.cost_group,
    row.cost_input_mode === "per_unit" ? "" : row.cost_input_mode,
    row.mileage_tool_code,
    row.ticket_prefix,
    row.booking_class,
  ];
  const numberFields = [
    row.count,
    row.standard_miles,
    row.cash_amount,
    row.manual_qualifying_miles,
    row.manual_qualifying_segments,
    row.manual_award_miles,
  ];
  return textFields.every(v => String(v || "").trim() === "") && numberFields.every(v => !Number(v));
}

function setRows(items) {
  const body = $("items-body");
  if (!body) return;
  body.innerHTML = "";
  const safeItems = Array.isArray(items) ? items : [];
  for (const item of safeItems) addRow(item);
  calculate();
}

function addRow(data = {}) {
  const template = $("row-template");
  const body = $("items-body");
  if (!template || !body) throw new Error("页面模板缺失：row-template 或 items-body 未找到");
  const clone = template.content.cloneNode(true);
  const tr = clone.querySelector("tr");
  const defaults = {
    name: "",
    count: "",
    product_type: "",
    earning_mode: "",
    marketing_carrier: "",
    operating_carrier: "",
    origin_airport: "",
    destination_airport: "",
    standard_miles_source: "unknown",
    standard_miles_note: "",
    flight_number: "",
    cost_group: "",
    cost_input_mode: "per_unit",
    mileage_tool_code: "",
    ticket_prefix: "",
    booking_class: "",
    standard_miles: "",
    cash_amount: "",
    manual_qualifying_miles: "",
    manual_qualifying_segments: "",
    manual_award_miles: "",
    ...data,
  };

  for (const [key, value] of Object.entries(defaults)) {
    const el = tr.querySelector(`.${key}`);
    if (el) el.value = value;
  }

  tr.querySelector(".remove-row")?.addEventListener("click", () => {
    tr.remove();
    calculate();
  });
  tr.querySelectorAll(".marketing_carrier, .operating_carrier, .origin_airport, .destination_airport, .mileage_tool_code, .booking_class, .flight_number").forEach(el => {
    el.addEventListener("blur", () => { el.value = String(el.value || "").trim().toUpperCase(); calculate(); });
  });
  tr.addEventListener("input", debounce(calculate, 250));
  tr.addEventListener("change", calculate);
  body.appendChild(tr);
  refreshResponsiveTables(body);
}

function sampleRows() {
  return [
    { name: "便宜短途I舱四段往返", count: 16, product_type: "ticket", earning_mode: "cash", marketing_carrier: "CZ", operating_carrier: "CZ", origin_airport: "", destination_airport: "", standard_miles_source: "cz_skypearl_calculator", standard_miles_note: "现金消费模式下标准里程仅留作参考", flight_number: "CZ示例", mileage_tool_code: "CZ", ticket_prefix: "784", booking_class: "I", standard_miles: 500, cash_amount: 260 },
    { name: "CZ非784标准里程示例", count: 2, product_type: "ticket", earning_mode: "standard", marketing_carrier: "CZ", operating_carrier: "CZ", origin_airport: "CAN", destination_airport: "PEK", standard_miles_source: "cz_skypearl_calculator", standard_miles_note: "示例值，实际请以南航明珠查询为准", flight_number: "CZ示例", mileage_tool_code: "CZ", ticket_prefix: "999", booking_class: "M", standard_miles: 1800, cash_amount: 850 },
    { name: "KE首尔-东京/中长线M舱", count: 2, product_type: "ticket", earning_mode: "partner", marketing_carrier: "KE", operating_carrier: "KE", origin_airport: "ICN", destination_airport: "NRT", standard_miles_source: "manual_official_tool", standard_miles_note: "合作伙伴累积到南航时仍以南航合作伙伴规则/实际入账为准", flight_number: "KE示例", mileage_tool_code: "CZ", ticket_prefix: "180", booking_class: "M", standard_miles: 760, cash_amount: 650 },
    { name: "784代码共享U舱匿名化示例", count: 1, product_type: "ticket", earning_mode: "codeshare_784", marketing_carrier: "CZ", operating_carrier: "HO", origin_airport: "", destination_airport: "", standard_miles_source: "manual_actual_posting", standard_miles_note: "按匿名化实际入账样本：U舱25%估算126定级里程；定级航段按CZ/OQ票面U舱0.75参考测算", flight_number: "CZ/HO示例", mileage_tool_code: "CZ", ticket_prefix: "784", booking_class: "U", standard_miles: 503, cash_amount: 300 },
    { name: "MF国内Y舱合作伙伴", count: 4, product_type: "ticket", earning_mode: "partner", marketing_carrier: "MF", operating_carrier: "MF", origin_airport: "XMN", destination_airport: "PKX", standard_miles_source: "manual_official_tool", standard_miles_note: "可先查南航明珠或厦航航空公司工具，再填入标准里程", flight_number: "MF示例", mileage_tool_code: "MF", ticket_prefix: "731", booking_class: "Y", standard_miles: 1200, cash_amount: 500 },
    { name: "AA经济舱V低累积示例", count: 2, product_type: "ticket", earning_mode: "partner", marketing_carrier: "AA", operating_carrier: "AA", origin_airport: "LAX", destination_airport: "LHR", standard_miles_source: "manual_official_tool", standard_miles_note: "跨计划累积需优先核对南航合作伙伴表", flight_number: "AA示例", mileage_tool_code: "CZ", ticket_prefix: "001", booking_class: "V", standard_miles: 11000, cash_amount: 2600 },
    { name: "柜台升舱产品", count: 1, product_type: "upgrade", earning_mode: "ancillary", marketing_carrier: "CZ", operating_carrier: "CZ", origin_airport: "", destination_airport: "", standard_miles_source: "unknown", standard_miles_note: "", flight_number: "", mileage_tool_code: "CZ", ticket_prefix: "784", booking_class: "", standard_miles: 0, cash_amount: 500 },
  ];
}

async function calculate() {
  if (state.calculating) return;
  state.calculating = true;
  try {
    const payload = readSettings();
    const result = await fetchJson("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!result || !result.summary || !result.target) {
      throw new Error("/api/calculate 返回结构不完整，缺少 summary 或 target");
    }
    state.lastResult = result;
    renderSummary(result);
    renderRows(result.items || []);
    setBootStatus("JS 已加载，后端接口正常。", "ok");
  } catch (err) {
    showError(err.message || "计算失败", err.stack || "");
  } finally {
    state.calculating = false;
  }
}

function scenarioLabel(mode) {
  if (mode === "retention_discount") return "保级折扣";
  if (mode === "upgrade") return "升级 / 新定级";
  if (mode === "scenario_not_selected") return "未选择评定场景，暂按原始标准";
  if (mode === "target_not_selected") return "未选择目标级别";
  return "原始标准";
}

function renderSummary(result) {
  const summary = result.summary || {};
  const target = result.target || {};
  const targetNotSelected = target.mode === "target_not_selected";

  $("target-threshold").textContent = targetNotSelected
    ? "请选择目标级别"
    : `${fmtNumber(target.required_miles)}里程 / ${fmtNumber(target.required_segments, 2)}段`;
  $("target-note").textContent = targetNotSelected
    ? "目标级别为空时不判断达标"
    : `${target.target_name || "目标级别"} · ${Math.round(Number(target.discount || 1) * 100)}%标准 · ${scenarioLabel(target.mode)}`;
  $("total-qm").textContent = fmtNumber(summary.total_qualifying_miles);
  $("miles-gap").textContent = targetNotSelected ? "请选择目标级别" : (Number(summary.miles_gap_to_target || 0) > 0 ? `还差 ${fmtNumber(summary.miles_gap_to_target)} 定级里程` : "里程已达标");
  $("total-qs").textContent = fmtNumber(summary.total_qualifying_segments, 2);
  $("segments-gap").textContent = targetNotSelected ? "请选择目标级别" : (Number(summary.segments_gap_to_target || 0) > 0 ? `还差 ${fmtNumber(summary.segments_gap_to_target, 2)} 定级航段` : "航段已达标");
  $("planned-cost").textContent = `¥${fmtNumber(summary.planned_cost, 2)}`;
  $("cost-efficiency").textContent = `¥/定级里程 ${summary.cost_per_qualifying_mile ?? "—"} · ¥/定级航段 ${summary.cost_per_qualifying_segment ?? "—"}`;

  const line = $("status-line");
  if (!line) return;
  if (targetNotSelected) {
    line.className = "status-line";
    line.textContent = "请选择目标级别和评定场景后再判断升级/保级缺口。";
  } else if (summary.target_met) {
    line.className = "status-line ok";
    line.textContent = `已满足 ${target.target_name || "目标"}：${summary.target_met_by_miles ? "按定级里程达标" : ""}${summary.target_met_by_miles && summary.target_met_by_segments ? " + " : ""}${summary.target_met_by_segments ? "按定级航段达标" : ""}。`;
  } else {
    line.className = "status-line bad";
    line.textContent = `尚未满足 ${target.target_name || "目标"}：还差 ${fmtNumber(summary.miles_gap_to_target)} 定级里程或 ${fmtNumber(summary.segments_gap_to_target, 2)} 定级航段。`;
  }
}

function renderRows(items) {
  const container = $("result-table");
  if (!container) return;
  if (!items.length) {
    container.innerHTML = "<p>尚无明细。</p>";
    return;
  }
  const rows = items.map(item => {
    const notes = (item.notes || []).map(n => `<span class="badge warn">${escapeHtml(n)}</span>`).join(" ");
    const partner = item.partner_code ? `${escapeHtml(item.partner_code)} · ${escapeHtml(item.partner_label || "")}` : "—";
    return `<tr>
      <td>${escapeHtml(item.name || "—")}</td>
      <td>${escapeHtml(item.count ?? "—")}</td>
      <td><span class="badge">${escapeHtml(item.earning_mode || "—")}</span></td>
      <td>${escapeHtml(item.marketing_carrier || "—")}/${escapeHtml(item.operating_carrier || "—")}</td>
      <td>${escapeHtml(item.flight_number || "—")}</td>
      <td>${escapeHtml(item.origin_airport || "—")}→${escapeHtml(item.destination_airport || "—")}</td>
      <td>${escapeHtml(sourceLabel(item.standard_miles_source || "unknown"))}<br><small>${escapeHtml(item.standard_miles_note || "")}</small></td>
      <td>${item.official_tool_url ? `<a href="${escapeHtml(item.official_tool_url)}" target="_blank" rel="noopener">${escapeHtml(item.official_tool_name || "航空公司工具")}</a>` : "—"}</td>
      <td>${escapeHtml(item.cost_group || "—")}</td>
      <td>${escapeHtml(costModeLabel(item.cost_input_mode || "per_unit"))}<br><small>${escapeHtml(item.cost_allocation_note || "")}</small></td>
      <td>${partner}</td>
      <td>${escapeHtml(item.booking_class || "—")}</td>
      <td>${item.cabin_accrual_rate !== undefined ? `${fmtNumber(Number(item.cabin_accrual_rate) * 100, 2)}%` : "—"}</td>
      <td>${fmtNumber(item.segment_credit_per_segment, 2)}</td>
      <td>¥${fmtNumber(item.total_cost, 2)}</td>
      <td>${fmtNumber(item.total_qualifying_miles)}</td>
      <td>${fmtNumber(item.total_qualifying_segments, 2)}</td>
      <td>${fmtNumber(item.total_award_miles)}</td>
      <td>${item.cost_per_qualifying_mile ?? "—"}</td>
      <td>${notes}</td>
    </tr>`;
  }).join("");
  container.innerHTML = `<table><thead><tr>
    <th>名称</th><th>次数</th><th>模式</th><th>市场/承运</th><th>航班号</th><th>航线</th><th>标准里程来源</th><th>航空公司工具</th><th>成本组</th><th>成本口径</th><th>合作伙伴</th><th>舱位</th><th>累积率</th><th>单段定级航段</th><th>总成本</th><th>定级里程</th><th>定级航段</th><th>奖励里程</th><th>¥/定级里程</th><th>提示</th>
  </tr></thead><tbody>${rows}</tbody></table>`;
  refreshResponsiveTables(container);
}

function sourceLabel(value) {
  const labels = {
    manual_official_tool: "手动：航空公司工具",
    manual_actual_posting: "手动：实际入账",
    cz_skypearl_calculator: "南航明珠查询",
    airline_own_calculator: "航司自有工具",
    airport_distance_estimate: "机场距离估算",
    unknown: "未标注",
  };
  return labels[value] || value || "未标注";
}

function costModeLabel(value) {
  const labels = {
    per_unit: "每段/每次成本",
    row_total: "本行总成本",
    order_total_even: "整单总价：按段数均分",
    order_total_by_standard_miles: "整单总价：按标准里程分摊",
  };
  return labels[value] || value || "每段/每次成本";
}


function renderDataSources() {
  const container = $("data-sources-table");
  if (!container) return;
  const sources = state.dataSources && Array.isArray(state.dataSources.sources) ? state.dataSources.sources : [];
  if (!sources.length) {
    container.innerHTML = "<p>暂无来源登记。</p>";
    return;
  }
  const rows = sources.map(s => `<tr>
    <td>${escapeHtml(s.id || "")}</td>
    <td>${escapeHtml(s.name_cn || "")}</td>
    <td>${escapeHtml(s.source_category || "")}</td>
    <td>${s.url ? `<a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">打开</a>` : "—"}</td>
    <td>${escapeHtml(Array.isArray(s.applies_to) ? s.applies_to.join(" / ") : (s.applies_to || ""))}</td>
    <td>${escapeHtml(s.retrieved_or_provided_at || "")}</td>
    <td>${escapeHtml(s.notes_cn || "")}</td>
  </tr>`).join("");
  container.innerHTML = `<table><thead><tr><th>来源ID</th><th>来源名称</th><th>类型</th><th>链接</th><th>适用数据</th><th>提供/查询日期</th><th>备注</th></tr></thead><tbody>${rows}</tbody></table>`;
  refreshResponsiveTables(container);
}

function renderMileageTools() {
  const container = $("mileage-tools-table");
  if (!container) return;
  const tools = state.mileageTools && Array.isArray(state.mileageTools.tools) ? state.mileageTools.tools : [];
  if (!tools.length) {
    container.innerHTML = "<p>暂无航空公司工具链接库。</p>";
    return;
  }
  const rows = tools.map(t => `<tr>
    <td>${escapeHtml(t.code || "")}</td>
    <td>${escapeHtml(t.program || "")}</td>
    <td>${escapeHtml(t.name_cn || "")}</td>
    <td>${escapeHtml(t.tool_type || "")}</td>
    <td><a href="${escapeHtml(t.tool_url || "#")}" target="_blank" rel="noopener">打开</a></td>
    <td>${escapeHtml(t.recommended_for || "")}</td>
    <td>${escapeHtml(t.notes_cn || "")}</td>
  </tr>`).join("");
  container.innerHTML = `<table><thead><tr><th>代码</th><th>计划/来源</th><th>工具</th><th>类型</th><th>链接</th><th>建议用途</th><th>备注</th></tr></thead><tbody>${rows}</tbody></table>`;
  refreshResponsiveTables(container);
}

function statusText(status) {
  if (!status) return "未知";
  const labels = {
    active_ffp_partner: "当前参考可累积",
    active_limited_or_special: "可用但有限制",
    adjusted_or_expired: "已调整/到期",
    legacy_skyteam_verify_required: "历史天合合作待核验",
    codeshare_or_elite_only_unknown_ffp: "代码共享/权益未知",
    self_or_subsidiary: "南航体系",
    unknown_unverified: "未确认"
  };
  return labels[status] || status;
}

function riskBadge(risk) {
  const r = String(risk || "medium").toLowerCase();
  const label = r === "low" ? "低" : r === "high" ? "高" : r === "verify_required" ? "需核验" : "中";
  return `<span class="risk-badge risk-${escapeHtml(r)}">${label}</span>`;
}

function partnerStatusFor(code) {
  const statuses = state.partnerStatus && state.partnerStatus.carriers ? state.partnerStatus.carriers : {};
  return statuses[String(code || "").toUpperCase()] || {};
}

function serviceClassLabel(value, rule = {}) {
  if (rule && rule.service_class_display) return String(rule.service_class_display);
  if (rule && rule.service_class_cn && rule.service_class_en) return `${rule.service_class_cn} / ${rule.service_class_en}`;
  const key = String(value || "").trim().toLowerCase();
  const labels = {
    first: "头等舱 / First Class",
    business: "公务舱 / Business Class",
    premium_economy: "超级经济舱 / Premium Economy",
    economy: "经济舱 / Economy Class",
    unknown: "未列明 / Not Listed"
  };
  if (!key) return "";
  return labels[key] || `${value}`;
}

function renderPartnerRules() {
  const container = $("partner-rules-table");
  if (!container) return;
  const partners = state.partners && state.partners.partners ? state.partners.partners : {};
  const rows = [];
  for (const [code, p] of Object.entries(partners)) {
    const st = partnerStatusFor(code);
    for (const r of p.rules || []) {
      rows.push(`<tr>
        <td>${escapeHtml(code)}</td>
        <td>${escapeHtml(p.name_cn || "")}</td>
        <td>${escapeHtml(statusText(st.ffp_status || p.ffp_status))}</td>
        <td>${riskBadge(st.risk_level || p.risk_level)}</td>
        <td>${escapeHtml(p.validity_cn || "")}</td>
        <td>${escapeHtml(serviceClassLabel(r.service_class, r))}</td>
        <td>${escapeHtml((r.cabins || []).join("/"))}</td>
        <td>${fmtNumber(Number(r.mileage_rate || 0) * 100, 2)}%</td>
        <td>${fmtNumber(r.segment_credit, 2)}</td>
        <td>${escapeHtml(st.status_note_cn || p.status_note_cn || "")}</td>
      </tr>`);
    }
  }
  container.innerHTML = `<table><thead><tr><th>代码</th><th>航司</th><th>当前状态</th><th>风险</th><th>适用日期</th><th>服务等级</th><th>订座舱位</th><th>里程累积率</th><th>计入定级航段</th><th>状态备注</th></tr></thead><tbody>${rows.join("")}</tbody></table>`;
  refreshResponsiveTables(container);
}

function renderCarrierDatalist() {
  const dl = $("carrier-code-list");
  if (!dl) return;
  const carriers = state.carriers && Array.isArray(state.carriers.carriers) ? state.carriers.carriers : [];
  dl.innerHTML = carriers.map(c => {
    const st = partnerStatusFor(c.code) || c;
    const label = `${c.code || ""} · ${c.name_cn || ""} · ${c.name_en || ""} · ${statusText(st.ffp_status || c.ffp_status)}`;
    return `<option value="${escapeHtml(c.code || "")}" label="${escapeHtml(label)}"></option>`;
  }).join("");
}


function renderMileageToolDatalist() {
  const dl = $("mileage-tool-code-list");
  if (!dl) return;
  const tools = state.mileageTools && Array.isArray(state.mileageTools.tools) ? state.mileageTools.tools : [];
  dl.innerHTML = tools.map(t => {
    const code = t.code || "";
    const label = `${code} · ${t.program || ""} · ${t.name_cn || ""} · ${t.tool_type || ""}`;
    return `<option value="${escapeHtml(code)}" label="${escapeHtml(label)}"></option>`;
  }).join("");
}

function renderCarrierDirectory() {
  const container = $("carrier-directory-table");
  if (!container) return;
  const carriers = state.carriers && Array.isArray(state.carriers.carriers) ? state.carriers.carriers : [];
  if (!carriers.length) {
    container.innerHTML = "<p>暂无航司代码库。</p>";
    return;
  }
  const rows = carriers.map(c => {
    const st = partnerStatusFor(c.code) || c;
    return `<tr>
      <td>${escapeHtml(c.code || "")}</td>
      <td>${escapeHtml(c.name_cn || "")}</td>
      <td>${escapeHtml(c.name_en || "")}</td>
      <td>${escapeHtml(statusText(st.ffp_status || c.ffp_status))}</td>
      <td>${riskBadge(st.risk_level || c.risk_level)}</td>
      <td>${escapeHtml((c.relation_types || []).join(" / "))}</td>
      <td>${c.has_partner_rule ? "是" : "否"}</td>
      <td>${c.has_codeshare_784_rule ? "是" : "否"}</td>
      <td>${escapeHtml(st.status_note_cn || c.status_note_cn || "")}</td>
      <td>${escapeHtml(c.notes_cn || "")}</td>
    </tr>`;
  }).join("");
  container.innerHTML = `<table><thead><tr><th>代码</th><th>中文名</th><th>英文名</th><th>当前状态</th><th>风险</th><th>关系/用途</th><th>合作伙伴表</th><th>784代码共享表</th><th>状态备注</th><th>备注</th></tr></thead><tbody>${rows}</tbody></table>`;
  refreshResponsiveTables(container);
}

function renderPartnerStatus() {
  const container = $("partner-status-table");
  if (!container) return;
  const statuses = state.partnerStatus && state.partnerStatus.carriers ? state.partnerStatus.carriers : {};
  const rows = Object.values(statuses).sort((a, b) => String(a.code).localeCompare(String(b.code))).map(st => `<tr>
    <td>${escapeHtml(st.code || "")}</td>
    <td>${escapeHtml(statusText(st.ffp_status))}</td>
    <td>${st.current_accrual_eligible ? "是" : "否"}</td>
    <td>${riskBadge(st.risk_level)}</td>
    <td>${escapeHtml(st.relation_hint || "")}</td>
    <td>${escapeHtml(st.status_note_cn || "")}</td>
  </tr>`).join("");
  container.innerHTML = `<table><thead><tr><th>代码</th><th>当前状态</th><th>默认可自动累积</th><th>风险</th><th>关系提示</th><th>备注</th></tr></thead><tbody>${rows}</tbody></table>`;
  refreshResponsiveTables(container);
}



function renderServiceClassNotes() {
  const container = $("service-class-notes-table");
  if (!container) return;
  const records = state.serviceClassNotes && Array.isArray(state.serviceClassNotes.records) ? state.serviceClassNotes.records : [];
  if (!records.length) {
    container.innerHTML = "<p>暂无服务等级说明。</p>";
    return;
  }
  const rows = records.map(r => `<tr>
    <td>${escapeHtml(r.id || "")}</td>
    <td>${escapeHtml(r.carrier_code || "")}</td>
    <td>${escapeHtml(r.name_cn || "")}</td>
    <td>${escapeHtml(r.name_en || "")}</td>
    <td>${escapeHtml(r.note_cn || "")}</td>
    <td>${escapeHtml(r.risk_note_cn || "")}</td>
    <td>${escapeHtml(r.source_refs || "")}</td>
  </tr>`).join("");
  container.innerHTML = `<table><thead><tr><th>ID</th><th>航司</th><th>中文说明</th><th>英文说明</th><th>提示内容</th><th>风险提示</th><th>来源</th></tr></thead><tbody>${rows}</tbody></table>`;
  refreshResponsiveTables(container);
}

function renderCodeshare784Rules() {
  const container = $("codeshare-784-table");
  if (!container) return;
  const carriers = state.codeshare784 && state.codeshare784.carriers ? state.codeshare784.carriers : {};
  const rows = [];
  for (const [code, c] of Object.entries(carriers)) {
    for (const r of c.rules || []) {
      rows.push(`<tr>
        <td>${escapeHtml(code)}</td>
        <td>${escapeHtml(c.name_cn || "")}</td>
        <td>${escapeHtml(c.validity_cn || "")}</td>
        <td>${escapeHtml(serviceClassLabel(r.service_class, r))}</td>
        <td>${escapeHtml((r.cabins || []).join("/"))}</td>
        <td>${fmtNumber(Number(r.mileage_rate || 0) * 100, 2)}%</td>
        <td>按南航票面舱位</td>
        <td>${escapeHtml(r.rule_source || "")}</td>
      </tr>`);
    }
  }
  container.innerHTML = rows.length
    ? `<table><thead><tr><th>承运方</th><th>航司</th><th>适用/来源</th><th>服务等级</th><th>舱位</th><th>定级里程比例</th><th>定级航段</th><th>来源</th></tr></thead><tbody>${rows.join("")}</tbody></table>`
    : "<p>暂无 784 代码共享规则。可替换 JSON/CSV 增补。</p>";
  refreshResponsiveTables(container);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

window.addEventListener("resize", debounce(updateScrollableHints, 150));

function debounce(fn, wait) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

async function download(endpoint, filename) {
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readSettings()),
    });
    if (!response.ok) throw new Error(`${endpoint} 导出失败：HTTP ${response.status}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    showError(err.message || "导出失败", err.stack || "");
  }
}


function downloadTextFile(filename, text, mime = "text/plain;charset=utf-8") {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function downloadCsvTemplate() {
  const headers = [
    "name", "count", "product_type", "earning_mode", "marketing_carrier", "operating_carrier", "flight_number",
    "origin_airport", "destination_airport", "ticket_prefix", "booking_class", "standard_miles",
    "standard_miles_source", "mileage_tool_code", "standard_miles_note", "cost_group", "cost_input_mode",
    "cash_amount", "manual_qualifying_miles", "manual_qualifying_segments", "manual_award_miles"
  ];
  const example = [
    "示例：同一订单第一段", "1", "ticket", "cash", "CZ", "CZ", "CZ1234", "CAN", "WUH", "784", "U", "500",
    "cz_skypearl_calculator", "CZ", "示例行；导入前可删除", "ORD001", "order_total_by_standard_miles", "1200", "", "", ""
  ];
  downloadTextFile("cz_status_import_template.csv", `${headers.join(",")}\n${example.map(csvEscape).join(",")}\n`, "text/csv;charset=utf-8");
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    const next = text[i + 1];
    if (inQuotes) {
      if (ch === '"' && next === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        cell += ch;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        row.push(cell);
        cell = "";
      } else if (ch === '\n') {
        row.push(cell);
        rows.push(row);
        row = [];
        cell = "";
      } else if (ch === '\r') {
        // ignore CR; LF will close the row
      } else {
        cell += ch;
      }
    }
  }
  if (cell.length || row.length) {
    row.push(cell);
    rows.push(row);
  }
  return rows.filter(r => r.some(c => String(c || "").trim() !== ""));
}

function normalizeImportedRow(raw = {}) {
  const get = (...keys) => {
    for (const key of keys) {
      if (raw[key] !== undefined && raw[key] !== null && raw[key] !== "") return raw[key];
    }
    return "";
  };
  return {
    name: get("name", "名称"),
    count: get("count", "次数", "次数/段数"),
    product_type: get("product_type", "type", "类型"),
    earning_mode: get("earning_mode", "mode", "累积方式"),
    marketing_carrier: get("marketing_carrier", "marketing", "市场方"),
    operating_carrier: get("operating_carrier", "operating", "承运方"),
    origin_airport: get("origin_airport", "origin", "始发"),
    destination_airport: get("destination_airport", "destination", "到达"),
    flight_number: get("flight_number", "flight_no", "flight", "航班号"),
    standard_miles_source: get("standard_miles_source", "里程来源") || "unknown",
    standard_miles_note: get("standard_miles_note", "里程备注"),
    cost_group: get("cost_group", "成本分摊组", "订单组"),
    cost_input_mode: get("cost_input_mode", "成本口径") || "per_unit",
    mileage_tool_code: get("mileage_tool_code", "工具代码"),
    ticket_prefix: get("ticket_prefix", "票号前缀"),
    booking_class: get("booking_class", "舱位"),
    standard_miles: get("standard_miles", "standard_miles_per_segment", "标准里程"),
    cash_amount: get("cash_amount", "cash_amount_per_unit", "现金消费额/成本", "cash_per_unit"),
    manual_qualifying_miles: get("manual_qualifying_miles", "手动定级里程"),
    manual_qualifying_segments: get("manual_qualifying_segments", "手动航段"),
    manual_award_miles: get("manual_award_miles", "手动奖励里程"),
  };
}

function applyImportedPlan(data) {
  let items = [];
  if (Array.isArray(data)) {
    items = data;
  } else if (data && Array.isArray(data.items)) {
    items = data.items;
    const settings = data.settings || data;
    for (const key of ["current_tier", "member_tier", "target_tier", "retention_year", "current_qualifying_miles", "current_qualifying_segments", "carryover_miles", "carryover_segments"]) {
      const el = $(key);
      if (el && settings[key] !== undefined) el.value = settings[key];
    }
  } else {
    throw new Error("JSON 格式不正确：需要包含 items 数组，或直接使用数组。");
  }
  setRows(items.map(normalizeImportedRow));
  alert(`已导入 ${items.length} 行。请核对成本口径、舱位、标准里程来源和现金金额。`);
}

function importCsvPlan(text) {
  const table = parseCsv(text);
  if (table.length < 2) throw new Error("CSV 至少需要表头和一行数据。");
  const headers = table[0].map(h => String(h || "").trim());
  const items = [];
  for (const cells of table.slice(1)) {
    const raw = {};
    headers.forEach((h, i) => { raw[h] = cells[i] ?? ""; });
    if (String(raw.name || raw["名称"] || "").trim().toLowerCase() === "summary") break;
    const row = normalizeImportedRow(raw);
    if (!isCompletelyBlankRow({
      ...row,
      count: Number(row.count || 0),
      standard_miles: Number(row.standard_miles || 0),
      cash_amount: Number(row.cash_amount || 0),
      manual_qualifying_miles: Number(row.manual_qualifying_miles || 0),
      manual_qualifying_segments: Number(row.manual_qualifying_segments || 0),
      manual_award_miles: Number(row.manual_award_miles || 0),
    })) items.push(row);
  }
  setRows(items);
  alert(`已从 CSV 导入 ${items.length} 行。`);
}

function handleImportFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const text = String(reader.result || "");
      if (/\.json$/i.test(file.name) || file.type.includes("json")) {
        applyImportedPlan(JSON.parse(text));
      } else {
        importCsvPlan(text);
      }
    } catch (err) {
      showError(err.message || "导入失败", err.stack || "");
    }
  };
  reader.readAsText(file, "utf-8");
}

function saveLocal() {
  localStorage.setItem(DRAFT_KEY, JSON.stringify(readSettings()));
  alert("草稿已保存到浏览器本地存储。")
}

function loadLocal() {
  const raw = localStorage.getItem(DRAFT_KEY);
  if (!raw) return false;
  try {
    const draft = JSON.parse(raw);
    if (!draft || !Array.isArray(draft.items)) return false;
    for (const key of ["current_tier", "member_tier", "target_tier", "retention_year", "current_qualifying_miles", "current_qualifying_segments", "carryover_miles", "carryover_segments"]) {
      const el = $(key);
      if (el && draft[key] !== undefined) el.value = draft[key];
    }
    setRows(draft.items || []);
    return true;
  } catch (err) {
    console.warn("Draft load failed", err);
    return false;
  }
}

async function init() {
  setBootStatus("JS 已启动，正在请求后端规则……", "info");
  const rules = await fetchJson("/api/rules");
  const partners = await fetchJson("/api/partners");
  const carriers = await fetchJson("/api/carriers");
  const codeshare784 = await fetchJson("/api/codeshare-784");
  const mileageTools = await fetchJson("/api/mileage-tools");
  const partnerStatus = await fetchJson("/api/partner-status");
  const dataSources = await fetchJson("/api/data-sources");
  const serviceClassNotes = await fetchJson("/api/service-class-notes");
  state.rules = rules;
  state.partners = partners;
  state.carriers = carriers;
  state.codeshare784 = codeshare784;
  state.mileageTools = mileageTools;
  state.partnerStatus = partnerStatus;
  state.dataSources = dataSources;
  state.serviceClassNotes = serviceClassNotes;

  const versionEl = $("rules-version");
  if (versionEl) {
    versionEl.textContent = `${state.rules.valid_from || "?"} → ${state.rules.valid_to || "?"} · Partner ${state.partners.version || "working"} · Status ${state.partnerStatus.version || "working"}`;
  }

  tierOptions($("current_tier"), "");
  tierOptions($("member_tier"), "");
  tierOptions($("target_tier"), "");

  document.querySelectorAll(".settings-panel input, .settings-panel select").forEach(el => {
    el.addEventListener("input", debounce(calculate, 200));
    el.addEventListener("change", calculate);
  });

  $("add-row")?.addEventListener("click", () => { addRow(); calculate(); });
  $("load-sample")?.addEventListener("click", () => setRows(sampleRows()));
  $("import-plan")?.addEventListener("click", () => $("import-file")?.click());
  $("import-file")?.addEventListener("change", (event) => {
    handleImportFile(event.target.files && event.target.files[0]);
    event.target.value = "";
  });
  $("download-template")?.addEventListener("click", downloadCsvTemplate);
  $("clear-all")?.addEventListener("click", () => setRows([]));
  $("export-csv")?.addEventListener("click", () => download("/api/export/csv", "cz_status_plan.csv"));
  $("export-json")?.addEventListener("click", () => download("/api/export/json", "cz_status_plan.json"));
  $("save-local")?.addEventListener("click", saveLocal);

  renderPartnerRules();
  renderCarrierDatalist();
  renderMileageToolDatalist();
  renderCarrierDirectory();
  renderPartnerStatus();
  renderCodeshare784Rules();
  renderMileageTools();
  renderDataSources();
  renderServiceClassNotes();
  if (!loadLocal()) { addRow(); calculate(); }
}

document.addEventListener("DOMContentLoaded", () => {
  init().catch(err => {
    showError(err.message || "初始化失败", err.stack || "");
  });
});
