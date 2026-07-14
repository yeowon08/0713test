<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>온열질환자 수 분석 대시보드</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{
  margin:0;
  padding:0;
  box-sizing:border-box;
  font-family:'Malgun Gothic',sans-serif;
}
body{
  background:linear-gradient(135deg,#FFE5EC,#FFF1C1,#DFFFE0,#DDEBFF,#EAD7FF);
  min-height:100vh;
  padding:30px;
}
.container{
  max-width:1100px;
  margin:auto;
}
h1{
  text-align:center;
  margin-bottom:20px;
  color:#444;
}
.selector{
  text-align:center;
  margin-bottom:25px;
}
select{
  padding:12px 18px;
  font-size:18px;
  border:none;
  border-radius:12px;
  background:white;
  box-shadow:0 3px 10px rgba(0,0,0,0.1);
}
.cards{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:20px;
  margin-bottom:30px;
}
.card{
  background:white;
  padding:25px;
  border-radius:20px;
  text-align:center;
  box-shadow:0 5px 15px rgba(0,0,0,0.08);
}
.card h2{
  font-size:20px;
  margin-bottom:10px;
}
.card p{
  font-size:32px;
  font-weight:bold;
  color:#ff69b4;
}
.chart-box{
  background:white;
  padding:20px;
  border-radius:20px;
  box-shadow:0 5px 15px rgba(0,0,0,0.08);
  height:420px;
}
.analysis{
  margin-top:25px;
  background:white;
  padding:20px;
  border-radius:20px;
  box-shadow:0 5px 15px rgba(0,0,0,0.08);
  line-height:1.8;
}
@media(max-width:768px){
  .card p{font-size:26px;}
}
</style>
</head>
<body>
<div class="container">
  <h1>🌡️ 온열질환자 수 분석 대시보드 📈</h1>

  <div class="selector">
    📍 지역 선택 :
    <select id="regionSelect">
      <option>서울</option>
      <option>부산</option>
      <option>대구</option>
      <option>인천</option>
      <option>대전</option>
      <option>울산</option>
      <option>수원</option>
      <option>양평</option>
      <option>전주</option>
      <option>거제</option>
      <option>제주</option>
      <option>세종</option>
      <option>강릉</option>
    </select>
  </div>

  <div class="cards">
    <div class="card">
      <h2>📅 데이터 연도 수</h2>
      <p id="yearCount">0년</p>
    </div>
    <div class="card">
      <h2>👥 최신 연도 환자수</h2>
      <p id="latestCount">0명</p>
    </div>
    <div class="card">
      <h2>📈 누적 환자수</h2>
      <p id="totalCount">0명</p>
    </div>
  </div>

  <div class="chart-box">
    <canvas id="tempChart"></canvas>
  </div>

  <div class="analysis">
    <h3>🔍 분석 결과</h3>
    <p id="analysisText"></p>
  </div>
</div>

<script>
const years = ["2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"];
let allData = [];
let chart;

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",").map(v => v.trim());
  return lines.slice(1).map(line => {
    const values = line.split(",").map(v => v.trim());
    const obj = {};
    headers.forEach((h, i) => obj[h] = values[i]);
    return obj;
  });
}

function buildChart(dataPoints) {
  const ctx = document.getElementById("tempChart");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: years,
      datasets: [{
        label: "온열환자수(명)",
        data: dataPoints,
        borderWidth: 3,
        tension: 0.3,
        fill: false,
        borderColor: "#ff69b4",
        backgroundColor: "#ff69b4",
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

function updateData(region) {
  const filtered = allData.filter(d => d.region === region);

  const mapped = years.map(y => {
    const row = filtered.find(d => String(d.year) === String(y));
    return row ? Number(row.heat_patients) : null;
  });

  const valid = mapped.filter(v => v !== null);
  const total = valid.reduce((a, b) => a + b, 0);
  const latest = valid.length ? valid[valid.length - 1] : 0;

  document.getElementById("yearCount").innerText = `${valid.length}년`;
  document.getElementById("latestCount").innerText = `${latest.toLocaleString()}명`;
  document.getElementById("totalCount").innerText = `${total.toLocaleString()}명`;

  chart.data.datasets[0].data = mapped;
  chart.update();

  const first = valid[0] || 0;
  const last = valid[valid.length - 1] || 0;
  const change = (last - first).toLocaleString();

  document.getElementById("analysisText").innerHTML =
    `${region}의 온열환자수는 2015년부터 2025년까지 확인할 수 있습니다. ` +
    `첫해 대비 최신 연도의 변화는 <strong>${change}명</strong>입니다. ` +
    `이 대시보드는 지역별 온열질환 추세를 시각적으로 비교하도록 설계되었습니다.`;
}

fetch("heat_patients_2015_2025.csv")
  .then(r => r.text())
  .then(text => {
    allData = parseCSV(text);
    buildChart(years.map(() => null));
    updateData(document.getElementById("regionSelect").value);
  })
  .catch(err => {
    console.error(err);
    document.getElementById("analysisText").innerText =
      "CSV 파일을 불러오지 못했습니다. 파일명과 경로를 확인하세요.";
    buildChart(years.map(() => null));
  });

document.getElementById("regionSelect").addEventListener("change", function() {
  updateData(this.value);
});
</script>
</body>
</html>
