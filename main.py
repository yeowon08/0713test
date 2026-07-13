<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>열섬현상과 전력수요의 관계</title>

<!-- 한글 폰트: Pretendard -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<!-- 차트 라이브러리: Chart.js v4 (UMD) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<style>
  :root{
    /* 도심 · 열섬 = 파랑 계열 */
    --city:#2563eb;
    --city-deep:#1e3a8a;
    --suburb:#60a5fa;
    /* 전력 · 기온 = 주황 계열 */
    --power:#ea580c;
    --power-soft:#f97316;
    --amber:#f59e0b;

    --bg:#f4f7fb;
    --card:#ffffff;
    --ink:#0f172a;
    --muted:#64748b;
    --line:#e2e8f0;
    --line-soft:#eef2f7;

    --pos:#dc2626;   /* 양의 상관 강조(따뜻) */
    --neg:#2563eb;   /* 음의 상관 강조(차가움) */

    --radius:20px;
    --shadow:0 1px 2px rgba(15,23,42,.04), 0 12px 32px -12px rgba(15,23,42,.14);
  }

  *{box-sizing:border-box;}
  html,body{margin:0;padding:0;}
  body{
    font-family:'Pretendard Variable','Pretendard',system-ui,-apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
    background:var(--bg);
    color:var(--ink);
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  .wrap{max-width:1000px;margin:0 auto;padding:28px 18px 72px;}

  /* ---------- 헤더(히어로) ---------- */
  .hero{
    border-radius:var(--radius);
    padding:34px 30px 30px;
    color:#fff;
    background:linear-gradient(105deg,var(--city-deep) 0%,var(--city) 42%,var(--power-soft) 100%);
    box-shadow:var(--shadow);
    position:relative;
    overflow:hidden;
  }
  .hero .eyebrow{
    font-size:13px;letter-spacing:.14em;text-transform:uppercase;
    font-weight:700;opacity:.85;margin:0 0 10px;
  }
  .hero h1{font-size:clamp(26px,5.4vw,40px);font-weight:800;margin:0 0 14px;letter-spacing:-.02em;}
  .hero .q{
    display:inline-block;background:rgba(255,255,255,.16);
    border:1px solid rgba(255,255,255,.28);
    padding:9px 15px;border-radius:999px;font-weight:600;font-size:clamp(14px,2.6vw,16px);
    backdrop-filter:blur(4px);
  }
  /* 열섬 그라디언트 시그니처 바 */
  .gradient-key{display:flex;align-items:center;gap:12px;margin-top:22px;font-size:12.5px;font-weight:600;}
  .gradient-key .bar{
    flex:1;height:10px;border-radius:999px;
    background:linear-gradient(90deg,var(--suburb),#93c5fd,#fdba74,var(--power));
  }
  .gradient-key span{white-space:nowrap;opacity:.92;}

  /* ---------- 카드 공통 ---------- */
  .card{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:var(--radius);
    padding:24px 22px;
    box-shadow:var(--shadow);
    margin-top:20px;
  }
  .card-head{display:flex;align-items:center;gap:12px;margin-bottom:6px;}
  .badge{
    flex:none;width:30px;height:30px;border-radius:9px;
    display:grid;place-items:center;font-weight:800;font-size:14px;color:#fff;
    background:var(--city);
  }
  .card h2{font-size:19px;font-weight:800;margin:0;letter-spacing:-.01em;}
  .card .sub{color:var(--muted);font-size:14px;margin:2px 0 16px;}

  /* ---------- 데이터 확인 통계 ---------- */
  .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:6px;}
  .stat{
    border:1px solid var(--line);border-radius:14px;padding:14px 16px;background:#fbfdff;
  }
  .stat .k{font-size:12.5px;color:var(--muted);font-weight:600;}
  .stat .v{font-size:20px;font-weight:800;margin-top:3px;letter-spacing:-.01em;}
  .stat .v small{font-size:13px;color:var(--muted);font-weight:600;}
  .var-list{margin:16px 0 0;padding:0;list-style:none;display:grid;gap:8px;}
  .var-list li{display:flex;gap:10px;align-items:baseline;font-size:14px;}
  .var-list .dot{width:10px;height:10px;border-radius:3px;flex:none;transform:translateY(2px);}

  /* ---------- 필터 ---------- */
  .filters{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end;}
  .field{display:flex;flex-direction:column;gap:6px;}
  .field label{font-size:12.5px;font-weight:700;color:var(--muted);}
  select{
    appearance:none;-webkit-appearance:none;
    font-family:inherit;font-size:14.5px;font-weight:600;color:var(--ink);
    padding:10px 38px 10px 14px;border:1.5px solid var(--line);border-radius:12px;background:#fff;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpath d='M4 6l4 4 4-4'/%3E%3C/svg%3E");
    background-repeat:no-repeat;background-position:right 12px center;
    cursor:pointer;min-width:150px;transition:border-color .15s;
  }
  select:focus{outline:none;border-color:var(--city);box-shadow:0 0 0 3px rgba(37,99,235,.15);}
  .region-note{
    font-size:13px;color:var(--muted);background:#f1f5f9;border-radius:10px;
    padding:8px 12px;margin-top:14px;
  }
  .region-note b{color:var(--city);}
  .region-note .sub-b{color:var(--power);}

  /* ---------- 차트 ---------- */
  .chart-box{position:relative;width:100%;height:340px;margin-top:6px;}
  @media(max-width:560px){ .chart-box{height:290px;} }
  .toggle{display:flex;gap:8px;flex-wrap:wrap;margin:2px 0 14px;}
  .toggle button{
    font-family:inherit;font-size:13px;font-weight:700;cursor:pointer;
    padding:7px 13px;border-radius:999px;border:1.5px solid var(--line);
    background:#fff;color:var(--muted);transition:all .15s;
  }
  .toggle button.on{background:var(--city);border-color:var(--city);color:#fff;}
  .toggle button.on.warm{background:var(--power);border-color:var(--power);}

  /* ---------- 상관 결과 ---------- */
  .r-panel{
    display:flex;flex-wrap:wrap;gap:18px;align-items:center;
    margin-top:18px;padding:18px;border-radius:16px;background:#f8fafc;border:1px solid var(--line);
  }
  .r-num{font-size:44px;font-weight:800;letter-spacing:-.03em;line-height:1;}
  .r-meta{flex:1;min-width:200px;}
  .r-tag{
    display:inline-block;font-size:13.5px;font-weight:800;padding:5px 12px;border-radius:999px;color:#fff;margin-bottom:6px;
  }
  .r-desc{font-size:14px;color:var(--muted);}
  .caution{
    display:flex;gap:10px;align-items:flex-start;margin-top:16px;
    font-size:13.5px;color:#92400e;background:#fffbeb;border:1px solid #fde68a;
    border-radius:12px;padding:12px 14px;
  }
  .caution svg{flex:none;margin-top:2px;}

  /* ---------- 탐구 결과 ---------- */
  #resultText p{margin:0 0 12px;font-size:15px;}
  #resultText p:last-child{margin-bottom:0;}
  #resultText b.city{color:var(--city);}
  #resultText b.power{color:var(--power);}
  .highlight-box{background:#f1f6ff;border-left:4px solid var(--city);border-radius:0 12px 12px 0;padding:14px 16px;margin-top:6px;}

  /* ---------- 로딩 / 오류 ---------- */
  #loading{text-align:center;padding:60px 20px;color:var(--muted);}
  .spinner{
    width:38px;height:38px;border:4px solid var(--line);border-top-color:var(--city);
    border-radius:50%;margin:0 auto 16px;animation:spin 1s linear infinite;
  }
  @keyframes spin{to{transform:rotate(360deg);}}
  #errorBox{display:none;border:1px solid #fecaca;background:#fef2f2;border-radius:var(--radius);padding:26px 24px;margin-top:20px;}
  #errorBox h2{color:#b91c1c;margin:0 0 6px;font-size:19px;}
  #errorBox .why{color:#7f1d1d;font-size:14px;margin-bottom:16px;}
  #errorBox ol{margin:0;padding-left:20px;font-size:14px;color:#374151;}
  #errorBox li{margin-bottom:10px;}
  #errorBox code{background:#1e293b;color:#f8fafc;padding:2px 7px;border-radius:6px;font-size:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}
  #errorBox .cmd{display:block;background:#1e293b;color:#f8fafc;padding:10px 12px;border-radius:8px;margin-top:6px;font-family:ui-monospace,Menlo,monospace;font-size:13px;overflow-x:auto;}

  #app{display:none;}
  footer{text-align:center;color:var(--muted);font-size:12.5px;margin-top:32px;}
  .muted{color:var(--muted);}
</style>
</head>
<body>
<div class="wrap">

  <!-- ===== 히어로 ===== -->
  <header class="hero">
    <p class="eyebrow">데이터 탐구 · Urban Heat Island</p>
    <h1>열섬현상과 전력수요의 관계</h1>
    <div class="q">탐구 질문 — 열섬 강도가 커질수록 전력수요도 증가할까?</div>
    <div class="gradient-key">
      <span>교외(양평) 시원함</span>
      <div class="bar"></div>
      <span>도심(서울) 더움</span>
    </div>
  </header>

  <!-- ===== 로딩 ===== -->
  <div id="loading">
    <div class="spinner"></div>
    데이터를 불러오는 중입니다…
  </div>

  <!-- ===== 오류 안내 ===== -->
  <div id="errorBox">
    <h2>CSV 파일을 불러오지 못했습니다</h2>
    <p class="why" id="errorWhy"></p>
    <ol>
      <li><b>파일 위치·이름 확인</b> — <code>서울_기온.csv</code>, <code>양평_기온.csv</code>, <code>전력수요.csv</code> 세 파일이 <code>index.html</code>과 <b>같은 폴더</b>에 있어야 합니다. 이름의 밑줄(_)과 글자가 정확히 일치해야 합니다.</li>
      <li><b>웹 서버로 실행</b> — 파일을 더블클릭해 여는 <code>file://</code> 방식에서는 브라우저 보안정책 때문에 CSV를 못 읽습니다. 아래 중 하나로 실행하세요.
        <span class="cmd"># 이 폴더에서 터미널을 열고 실행<br>python -m http.server 8000<br># 그 다음 브라우저에서 http://localhost:8000 접속</span>
        또는 이 폴더를 그대로 <b>GitHub Pages</b>에 올리면 바로 실행됩니다.
      </li>
      <li><b>파일 인코딩</b> — 원본 CSV는 <b>EUC-KR(CP949)</b> 로 저장되어 있으며, 이 페이지가 자동으로 해당 인코딩으로 해석합니다. 파일을 다시 저장했다면 EUC-KR 또는 UTF-8 형식이어야 합니다.</li>
      <li><b>인터넷 연결</b> — 그래프 그리기(Chart.js)와 한글 폰트는 CDN에서 불러옵니다. 오프라인이면 그래프가 표시되지 않을 수 있습니다.</li>
    </ol>
  </div>

  <!-- ===== 앱 본문 ===== -->
  <main id="app">

    <!-- 2. 데이터 확인 -->
    <section class="card">
      <div class="card-head"><div class="badge" style="background:var(--muted)">01</div><h2>데이터 확인</h2></div>
      <p class="sub">분석에 사용한 데이터의 기간과 주요 변수입니다.</p>
      <div class="stat-grid">
        <div class="stat"><div class="k">관측 기간</div><div class="v" id="statPeriod">–</div></div>
        <div class="stat"><div class="k">관측 간격</div><div class="v" id="statInterval">1시간</div></div>
        <div class="stat"><div class="k">전체 관측 수</div><div class="v" id="statCount">–<small> 시간</small></div></div>
        <div class="stat"><div class="k">비교 지역</div><div class="v" style="font-size:16px">서울 vs 양평</div></div>
      </div>
      <ul class="var-list">
        <li><span class="dot" style="background:var(--city)"></span><b>도심 기온</b> — 서울(지점 108)의 시각별 기온 (°C)</li>
        <li><span class="dot" style="background:var(--suburb)"></span><b>교외 기온</b> — 양평(지점 202)의 시각별 기온 (°C)</li>
        <li><span class="dot" style="background:linear-gradient(90deg,var(--city),var(--power))"></span><b>열섬 강도</b> — 도심 기온 − 교외 기온 (°C)</li>
        <li><span class="dot" style="background:var(--power)"></span><b>전력수요</b> — 시각별 전력수요 (MWh)</li>
      </ul>

      <div class="region-note">
        비교 지역은 <b>도심 = 서울</b>, <span class="sub-b" style="font-weight:700">교외 = 양평</span> 으로 고정되어 있습니다.
        아래 필터로 <b>기간(월)</b> 과 <b>그래프 단위</b> 를 바꿔가며 분석할 수 있습니다.
      </div>

      <div class="filters" style="margin-top:16px">
        <div class="field">
          <label for="monthSel">기간 선택</label>
          <select id="monthSel"></select>
        </div>
        <div class="field">
          <label for="unitSel">그래프 단위</label>
          <select id="unitSel">
            <option value="daily">일별 평균</option>
            <option value="hourly">시간별</option>
          </select>
        </div>
        <div class="field" style="justify-content:flex-end">
          <span class="muted" id="filterInfo" style="font-size:13px;padding-bottom:10px"></span>
        </div>
      </div>
    </section>

    <!-- 3. 열섬현상 분석 -->
    <section class="card">
      <div class="card-head"><div class="badge">02</div><h2>열섬현상 분석</h2></div>
      <p class="sub">같은 날짜·시각의 도심(서울)과 교외(양평) 기온을 비교하고, <b>열섬 강도 = 도심 − 교외</b> 로 계산했습니다. (오른쪽 축)</p>
      <div class="chart-box"><canvas id="heatChart"></canvas></div>
    </section>

    <!-- 4. 전력수요 분석 -->
    <section class="card">
      <div class="card-head"><div class="badge" style="background:var(--power)">03</div><h2>전력수요 분석</h2></div>
      <p class="sub">시간·날짜에 따른 전력수요 변화입니다. 도심 기온(오른쪽 축)을 함께 표시해 <b>기온이 높은 시기</b>의 전력수요를 비교할 수 있습니다.</p>
      <div class="chart-box"><canvas id="powerChart"></canvas></div>
    </section>

    <!-- 5. 상관관계 분석 -->
    <section class="card">
      <div class="card-head"><div class="badge" style="background:var(--city-deep)">04</div><h2>상관관계 분석</h2></div>
      <p class="sub">가로축 <b>열섬 강도</b>, 세로축 <b>전력수요</b> 산점도입니다. 선형 추세선과 피어슨 상관계수(r)를 함께 표시합니다. <span class="muted">(점은 선택 기간의 시간별 관측값)</span></p>
      <div class="chart-box"><canvas id="scatterChart"></canvas></div>

      <div class="r-panel">
        <div class="r-num" id="rNum">–</div>
        <div class="r-meta">
          <span class="r-tag" id="rTag">–</span>
          <div class="r-desc" id="rDesc"></div>
        </div>
      </div>

      <div class="caution">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#b45309" stroke-width="2"><path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>
        <div><b>상관관계 ≠ 인과관계.</b> 두 변수가 함께 움직인다고 해서 한쪽이 다른 쪽의 <b>원인</b>이라는 뜻은 아닙니다. 전력수요는 기온·계절·요일·산업활동 등 여러 요인의 영향을 받으므로, 이 그래프만으로 “열섬이 전력수요를 늘린다”고 단정할 수 없습니다.</div>
      </div>
    </section>

    <!-- 6. 탐구 결과 -->
    <section class="card">
      <div class="card-head"><div class="badge" style="background:var(--amber)">05</div><h2>탐구 결과</h2></div>
      <p class="sub">현재 선택한 기간의 <b>실제 데이터</b>를 바탕으로 자동 요약합니다. (필터를 바꾸면 결과도 함께 갱신됩니다.)</p>
      <div id="resultText"></div>
    </section>

    <footer>
      데이터: 기상청 기온 관측(서울·양평), 시간별 전력수요 · 2025년 · 본 페이지는 실제 CSV를 직접 계산해 표시합니다.
    </footer>
  </main>
</div>

<script>
/* =========================================================
   1) CSV 불러오기 (EUC-KR 디코딩)
   ========================================================= */
const FILES = {
  seoul: '서울_기온.csv',
  yangpyeong: '양평_기온.csv',
  power: '전력수요.csv'
};

async function loadCSV(path){
  const res = await fetch(path);
  if(!res.ok) throw new Error(`'${path}' 응답 오류 (HTTP ${res.status})`);
  const buf = await res.arrayBuffer();
  // 원본 파일 인코딩이 EUC-KR(CP949) 이므로 그에 맞춰 해석
  let text;
  try { text = new TextDecoder('euc-kr').decode(buf); }
  catch(e){ text = new TextDecoder('utf-8').decode(buf); }
  return text;
}

// 간단 CSV 파서 (본 데이터에는 따옴표/내부 콤마가 없음)
function parseCSV(text){
  const lines = text.replace(/\r/g,'').split('\n').filter(l => l.trim().length);
  const header = lines[0].split(',');
  const rows = [];
  for(let i=1;i<lines.length;i++){
    rows.push(lines[i].split(','));
  }
  return {header, rows};
}

/* =========================================================
   2) 데이터 병합
   ========================================================= */
let RECORDS = [];   // {dt, date, month, seoul, yp, uhi, power}
let MONTHS = [];

async function buildData(){
  const [sT, yT, pT] = await Promise.all([
    loadCSV(FILES.seoul), loadCSV(FILES.yangpyeong), loadCSV(FILES.power)
  ]);

  // 기온 파일 열: 지점, 지점명, 일시, 기온(°C)  →  일시=idx2, 기온=idx3
  const seoulMap = new Map();
  for(const c of parseCSV(sT).rows){ if(c.length>=4) seoulMap.set(c[2].trim(), parseFloat(c[3])); }
  const ypMap = new Map();
  for(const c of parseCSV(yT).rows){ if(c.length>=4) ypMap.set(c[2].trim(), parseFloat(c[3])); }
  // 전력 파일 열: 일시, 전력수요(MWh)  →  일시=idx0, 수요=idx1
  const powerMap = new Map();
  for(const c of parseCSV(pT).rows){ if(c.length>=2) powerMap.set(c[0].trim(), parseFloat(c[1])); }

  // 세 파일 모두에 존재하는 시각만 병합
  const recs = [];
  for(const [dt, s] of seoulMap){
    const y = ypMap.get(dt);
    const p = powerMap.get(dt);
    if(y===undefined || p===undefined) continue;
    if(!isFinite(s)||!isFinite(y)||!isFinite(p)) continue;
    recs.push({ dt, date: dt.slice(0,10), month: dt.slice(0,7),
                seoul:s, yp:y, uhi:+(s-y).toFixed(2), power:p });
  }
  recs.sort((a,b)=> a.dt < b.dt ? -1 : 1);
  RECORDS = recs;
  MONTHS = [...new Set(recs.map(r=>r.month))].sort();
  if(RECORDS.length === 0) throw new Error('세 파일에서 공통되는 시각이 없어 데이터를 병합하지 못했습니다.');
}

/* =========================================================
   3) 통계 유틸
   ========================================================= */
function pearson(xs, ys){
  const n = xs.length;
  if(n < 3) return NaN;
  let sx=0, sy=0, sxx=0, syy=0, sxy=0;
  for(let i=0;i<n;i++){ const x=xs[i], y=ys[i]; sx+=x; sy+=y; sxx+=x*x; syy+=y*y; sxy+=x*y; }
  const cov = n*sxy - sx*sy;
  const dx = n*sxx - sx*sx;
  const dy = n*syy - sy*sy;
  const den = Math.sqrt(dx*dy);
  return den === 0 ? NaN : cov/den;
}
function linReg(xs, ys){
  const n = xs.length;
  let sx=0, sy=0, sxx=0, sxy=0;
  for(let i=0;i<n;i++){ sx+=xs[i]; sy+=ys[i]; sxx+=xs[i]*xs[i]; sxy+=xs[i]*ys[i]; }
  const slope = (n*sxy - sx*sy) / (n*sxx - sx*sx);
  const intercept = (sy - slope*sx) / n;
  return {slope, intercept};
}
const mean = a => a.reduce((s,v)=>s+v,0)/a.length;
const fmt = (n,d=1) => n.toLocaleString('ko-KR',{minimumFractionDigits:d,maximumFractionDigits:d});

/* r 해석: 크기 + 부호 */
function interpretR(r){
  const a = Math.abs(r);
  let strength, color;
  if(a < 0.1){ strength='상관관계가 거의 없음'; color='#64748b'; }
  else if(a < 0.3){ strength='약한 상관관계'; color='#0891b2'; }
  else if(a < 0.7){ strength='뚜렷한(중간) 상관관계'; color= r>0 ? '#ea580c' : '#2563eb'; }
  else { strength='강한 상관관계'; color= r>0 ? '#dc2626' : '#1e3a8a'; }

  let sign = '';
  if(a >= 0.1) sign = r > 0 ? '양의 ' : '음의 ';
  const label = a < 0.1 ? strength : (sign + strength);

  let desc;
  if(a < 0.1) desc = '열섬 강도와 전력수요가 함께 움직이는 경향이 거의 나타나지 않습니다.';
  else if(r > 0) desc = '열섬 강도가 클수록 전력수요도 커지는 경향이 있습니다.';
  else desc = '열섬 강도가 클수록 전력수요는 오히려 작아지는 경향이 있습니다.';
  return {label, color, desc, strength, sign:(r>0?'양':'음')};
}

/* =========================================================
   4) 필터링 & 집계
   ========================================================= */
function getFiltered(){
  const m = document.getElementById('monthSel').value;
  return m === 'all' ? RECORDS : RECORDS.filter(r=>r.month===m);
}
// 일별 평균 집계
function aggregateDaily(rows){
  const g = new Map();
  for(const r of rows){
    if(!g.has(r.date)) g.set(r.date, {date:r.date, seoul:[], yp:[], uhi:[], power:[]});
    const o = g.get(r.date);
    o.seoul.push(r.seoul); o.yp.push(r.yp); o.uhi.push(r.uhi); o.power.push(r.power);
  }
  return [...g.values()].sort((a,b)=>a.date<b.date?-1:1).map(o=>({
    label:o.date.slice(5),               // MM-DD
    seoul:mean(o.seoul), yp:mean(o.yp), uhi:mean(o.uhi), power:mean(o.power)
  }));
}
function toHourly(rows){
  return rows.map(r=>({ label:r.dt.slice(5).replace(' ','\n'), seoul:r.seoul, yp:r.yp, uhi:r.uhi, power:r.power }));
}

/* =========================================================
   5) 차트
   ========================================================= */
Chart.defaults.font.family = "'Pretendard','system-ui',sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#475569';
let heatChart, powerChart, scatterChart;

function commonLineOpts(yLeftTitle, yRightTitle, xTitle){
  return {
    responsive:true, maintainAspectRatio:false,
    interaction:{mode:'index', intersect:false},
    plugins:{
      legend:{position:'top', labels:{usePointStyle:true, pointStyle:'line', padding:16, font:{weight:'600'}}},
      tooltip:{
        backgroundColor:'#0f172a', padding:12, cornerRadius:10, titleFont:{weight:'700'},
        callbacks:{}
      }
    },
    scales:{
      x:{ title:{display:true, text:xTitle, font:{weight:'700'}, color:'#64748b'},
          grid:{display:false}, ticks:{maxTicksLimit:12, autoSkip:true, maxRotation:0} },
      y:{ position:'left', title:{display:true, text:yLeftTitle, font:{weight:'700'}, color:'#64748b'},
          grid:{color:'#eef2f7'} },
      y1:{ position:'right', title:{display:true, text:yRightTitle, font:{weight:'700'}, color:'#64748b'},
           grid:{drawOnChartArea:false} }
    }
  };
}

function drawHeat(data){
  const labels = data.map(d=>d.label);
  const big = data.length > 400;
  const opts = commonLineOpts('기온 (°C)', '열섬 강도 (°C)', document.getElementById('unitSel').value==='daily'?'날짜':'날짜·시각');
  opts.plugins.tooltip.callbacks.label = (c)=>{
    const u = c.dataset.unit || '';
    return `${c.dataset.label}: ${fmt(c.parsed.y)}${u}`;
  };
  const cfg = {
    type:'line',
    data:{ labels, datasets:[
      {label:'도심(서울) 기온', unit:' °C', data:data.map(d=>d.seoul), borderColor:'#2563eb', backgroundColor:'#2563eb',
       borderWidth:2, pointRadius:big?0:2, tension:.25, yAxisID:'y'},
      {label:'교외(양평) 기온', unit:' °C', data:data.map(d=>d.yp), borderColor:'#60a5fa', backgroundColor:'#60a5fa',
       borderWidth:2, pointRadius:big?0:2, tension:.25, borderDash:[5,3], yAxisID:'y'},
      {label:'열섬 강도(도심−교외)', unit:' °C', data:data.map(d=>d.uhi), borderColor:'#ea580c', backgroundColor:'rgba(234,88,12,.10)',
       borderWidth:2, pointRadius:big?0:2, tension:.25, fill:true, yAxisID:'y1'}
    ]},
    options:opts
  };
  if(big) cfg.options.animation=false;
  heatChart?.destroy();
  heatChart = new Chart(document.getElementById('heatChart'), cfg);
}

function drawPower(data){
  const labels = data.map(d=>d.label);
  const big = data.length > 400;
  const unit = document.getElementById('unitSel').value;
  const powLabel = unit==='daily' ? '전력수요(일 평균)' : '전력수요';
  const opts = commonLineOpts('전력수요 (MWh)', '도심 기온 (°C)', unit==='daily'?'날짜':'날짜·시각');
  opts.plugins.tooltip.callbacks.label = (c)=>{
    if(c.dataset.yAxisID==='y1') return `${c.dataset.label}: ${fmt(c.parsed.y)} °C`;
    return `${c.dataset.label}: ${fmt(c.parsed.y,0)} MWh`;
  };
  const cfg = {
    type:'line',
    data:{ labels, datasets:[
      {label:powLabel, data:data.map(d=>d.power), borderColor:'#ea580c', backgroundColor:'rgba(234,88,12,.12)',
       borderWidth:2, pointRadius:big?0:2, tension:.25, fill:true, yAxisID:'y'},
      {label:'도심(서울) 기온', data:data.map(d=>d.seoul), borderColor:'#2563eb', backgroundColor:'#2563eb',
       borderWidth:2, pointRadius:big?0:2, tension:.25, borderDash:[5,3], yAxisID:'y1'}
    ]},
    options:opts
  };
  if(big) cfg.options.animation=false;
  powerChart?.destroy();
  powerChart = new Chart(document.getElementById('powerChart'), cfg);
}

function drawScatter(rows){
  // 산점도는 항상 시간별 원자료 사용
  const pts = rows.map(r=>({x:r.uhi, y:r.power}));
  const xs = rows.map(r=>r.uhi), ys = rows.map(r=>r.power);
  const {slope, intercept} = linReg(xs, ys);
  const xmin = Math.min(...xs), xmax = Math.max(...xs);
  const trend = [{x:xmin, y:slope*xmin+intercept}, {x:xmax, y:slope*xmax+intercept}];

  const cfg = {
    type:'scatter',
    data:{ datasets:[
      {label:'시간별 관측값', data:pts, backgroundColor:'rgba(37,99,235,.28)', borderColor:'rgba(37,99,235,.28)',
       pointRadius:2.5, pointHoverRadius:5},
      {type:'line', label:'선형 추세선', data:trend, borderColor:'#ea580c', borderWidth:2.5,
       pointRadius:0, fill:false, tension:0}
    ]},
    options:{
      responsive:true, maintainAspectRatio:false, animation:false,
      plugins:{
        legend:{position:'top', labels:{usePointStyle:true, padding:16, font:{weight:'600'}}},
        tooltip:{ backgroundColor:'#0f172a', padding:12, cornerRadius:10,
          callbacks:{ label:(c)=> c.datasetIndex===0
            ? `열섬 강도 ${fmt(c.parsed.x,2)} °C · 전력수요 ${fmt(c.parsed.y,0)} MWh`
            : `추세선` }
        }
      },
      scales:{
        x:{ title:{display:true, text:'열섬 강도 (°C)  =  도심(서울) − 교외(양평)', font:{weight:'700'}, color:'#64748b'},
            grid:{color:'#eef2f7'} },
        y:{ title:{display:true, text:'전력수요 (MWh)', font:{weight:'700'}, color:'#64748b'},
            grid:{color:'#eef2f7'} }
      }
    }
  };
  scatterChart?.destroy();
  scatterChart = new Chart(document.getElementById('scatterChart'), cfg);

  return pearson(xs, ys);
}

/* =========================================================
   6) 상관 결과 & 탐구 결과 텍스트
   ========================================================= */
function renderCorrelation(r, rows){
  const info = interpretR(r);
  document.getElementById('rNum').textContent = 'r = ' + (isNaN(r)?'–':r.toFixed(3));
  document.getElementById('rNum').style.color = info.color;
  const tag = document.getElementById('rTag');
  tag.textContent = info.label;
  tag.style.background = info.color;
  document.getElementById('rDesc').textContent = info.desc + `  (표본 ${rows.length.toLocaleString('ko-KR')}시간)`;
  return info;
}

function renderResult(r, info, rows){
  const uhis = rows.map(x=>x.uhi);
  const meanUHI = mean(uhis);
  const posShare = uhis.filter(v=>v>0).length / uhis.length * 100;
  const monthSel = document.getElementById('monthSel');
  const periodName = monthSel.value==='all' ? '2025년 전체 기간' : monthSel.value.replace('-','년 ')+'월';
  const rTxt = isNaN(r) ? '계산 불가' : r.toFixed(3);

  // 참고: 도심 기온 자체와 전력수요의 상관 (실제 계산값)
  const rTemp = pearson(rows.map(x=>x.seoul), rows.map(x=>x.power));

  const el = document.getElementById('resultText');
  el.innerHTML = `
    <div class="highlight-box">
      <b>${periodName}</b> 동안 도심(서울)은 교외(양평)보다 평균 <b class="city">${fmt(meanUHI,2)}°C</b> 높았고,
      전체 시간의 약 <b>${fmt(posShare,0)}%</b>에서 도심이 더 더웠습니다 (열섬현상 확인).
    </div>
    <p style="margin-top:14px">
      열섬 강도와 전력수요의 피어슨 상관계수는 <b style="color:${info.color}">r = ${rTxt}</b> 로,
      <b style="color:${info.color}">${info.label}</b> 로 나타났습니다.
      ${
        Math.abs(r) < 0.1
        ? `즉 이 기간의 데이터에서는 <b>열섬 강도가 커진다고 전력수요가 함께 뚜렷하게 증가하지는 않았습니다.</b> 탐구 질문에 대한 답은 “데이터상 뚜렷한 관계는 확인되지 않음”입니다.`
        : (r>0
          ? `즉 열섬 강도가 클수록 전력수요도 커지는 <b>양의 경향</b>이 관찰됩니다. 다만 그 관계의 세기는 위 등급(${info.strength})만큼입니다.`
          : `즉 열섬 강도가 클수록 전력수요는 오히려 작아지는 <b>음의 경향</b>이 관찰됩니다.`)
      }
    </p>
    <p>
      참고로 <b class="power">도심 기온</b> 자체와 전력수요의 상관계수는 <b>r = ${isNaN(rTemp)?'–':rTemp.toFixed(3)}</b> 입니다.
      전력수요는 열섬 강도(두 지역의 온도 차)보다 <b>실제 기온·계절·요일</b> 등의 영향을 더 크게 받는 것으로 보이며,
      상관관계가 곧 인과관계를 뜻하지는 않습니다.
    </p>
    <p class="muted" style="font-size:13px">
      ※ 위 수치는 선택한 기간의 실제 CSV 데이터를 그대로 계산한 값이며, 필터를 바꾸면 결과도 달라집니다.
      월별로 비교해 보면 여름철과 겨울철에서 관계가 다르게 나타나는지 직접 탐구할 수 있습니다.
    </p>
  `;
}

/* =========================================================
   7) 전체 갱신
   ========================================================= */
function updateAll(){
  const rows = getFiltered();
  const unit = document.getElementById('unitSel').value;

  // 필터 안내
  document.getElementById('filterInfo').textContent =
    `${rows.length.toLocaleString('ko-KR')}시간 · ${unit==='daily'?'일별 평균':'시간별'} 표시`;

  // 선그래프 데이터(일별/시간별)
  const lineData = unit==='daily' ? aggregateDaily(rows) : toHourly(rows);
  drawHeat(lineData);
  drawPower(lineData);

  // 산점도 & 상관 (항상 시간별 원자료)
  const r = drawScatter(rows);
  const info = renderCorrelation(r, rows);
  renderResult(r, info, rows);
}

/* =========================================================
   8) 초기화
   ========================================================= */
function fillMonthOptions(){
  const sel = document.getElementById('monthSel');
  const monthName = m => m.replace('-','년 ')+'월';
  let html = '<option value="all">2025년 전체</option>';
  for(const m of MONTHS) html += `<option value="${m}">${monthName(m)}</option>`;
  sel.innerHTML = html;
}
function fillDataInfo(){
  const first = RECORDS[0].dt, last = RECORDS[RECORDS.length-1].dt;
  document.getElementById('statPeriod').textContent = first.slice(0,10);
  document.getElementById('statPeriod').insertAdjacentHTML('beforeend',
    `<br><small style="font-weight:600;color:#64748b">~ ${last.slice(0,10)}</small>`);
  document.getElementById('statCount').innerHTML = RECORDS.length.toLocaleString('ko-KR') + '<small> 시간</small>';
}

function showError(err){
  document.getElementById('loading').style.display='none';
  document.getElementById('app').style.display='none';
  const box = document.getElementById('errorBox');
  box.style.display='block';
  const isFile = location.protocol === 'file:';
  document.getElementById('errorWhy').textContent =
    (isFile ? '현재 file:// 방식으로 열려 있어 브라우저가 CSV 파일을 차단했을 가능성이 큽니다. ' : '')
    + '자세한 원인: ' + (err && err.message ? err.message : err);
  console.error(err);
}

(async function init(){
  try{
    await buildData();
    fillDataInfo();
    fillMonthOptions();
    document.getElementById('monthSel').addEventListener('change', updateAll);
    document.getElementById('unitSel').addEventListener('change', updateAll);
    document.getElementById('loading').style.display='none';
    document.getElementById('app').style.display='block';
    updateAll();
  }catch(err){
    showError(err);
  }
})();
</script>
</body>
</html>
