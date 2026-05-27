async function loadExperiments() {
  var list = document.getElementById('experiment-list');
  try {
    var res = await fetch('/api/experiments');
    var data = await res.json();
    if (data.length === 0) {
      list.innerHTML = '<div class="card" style="text-align:center;padding:40px;color:var(--gray-500);">' +
        '<p style="font-size:2rem;">&#x1F9EA;</p>' +
        '<p>还没有实验，点击"新建实验"开始吧</p>' +
      '</div>';
      return;
    }
    list.innerHTML = data.map(function(exp) {
      var pct = exp.total_steps ? Math.round(exp.completed_steps / exp.total_steps * 100) : 0;
      return '<a href="/experiment/' + exp.id + '" class="exp-card">' +
        '<div class="card">' +
          '<h3>' + escHtml(exp.title) + '</h3>' +
          '<div class="meta">' + exp.created_at + ' · ' + exp.completed_steps + '/' + exp.total_steps + ' 步完成</div>' +
          '<div class="progress-bar"><div class="fill" style="width:' + pct + '%"></div></div>' +
        '</div>' +
      '</a>';
    }).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:var(--danger)">加载失败：' + e.message + '</p>';
  }
}

function showCreateModal() {
  document.getElementById('create-modal').classList.remove('hidden');
}
function hideCreateModal() {
  document.getElementById('create-modal').classList.add('hidden');
}

async function createExperiment() {
  var title = document.getElementById('new-title').value.trim();
  var objective = document.getElementById('new-objective').value.trim();
  var references = document.getElementById('new-references').value.trim();
  var apikey = document.getElementById('new-apikey').value.trim();

  if (!title) { showToast('请填写实验标题', 'error'); return; }
  if (!objective) { showToast('请填写实验目的', 'error'); return; }

  var btn = document.getElementById('btn-create');
  btn.disabled = true;
  btn.textContent = '正在创建...';

  try {
    if (apikey) {
      await fetch('/api/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deepseek_api_key: apikey }),
      });
    }

    var res1 = await fetch('/api/experiments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title, objective: objective, references: references }),
    });
    var exp = await res1.json();
    if (exp.error) { showToast(exp.error, 'error'); btn.disabled = false; btn.textContent = '创建并生成步骤'; return; }

    btn.textContent = 'AI 正在生成步骤...';
    var res2 = await fetch('/api/generate-steps', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ objective: objective, references: references }),
    });
    var gen = await res2.json();
    if (gen.error) { showToast(gen.error, 'error'); btn.disabled = false; btn.textContent = '创建并生成步骤'; return; }

    exp.steps = gen.steps;
    await fetch('/api/experiments/' + exp.id, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(exp),
    });

    window.location.href = '/experiment/' + exp.id;
  } catch (e) {
    showToast('操作失败：' + e.message, 'error');
    btn.disabled = false;
    btn.textContent = '创建并生成步骤';
  }
}

loadExperiments();
