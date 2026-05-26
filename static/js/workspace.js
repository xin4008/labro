var experiment = null;
var currentStepIdx = -1;

async function loadExperiment() {
  var res = await fetch('/api/experiments/' + EXPERIMENT_ID);
  experiment = await res.json();

  var dirRes = await fetch('/api/experiments/' + EXPERIMENT_ID + '/dir');
  if (dirRes.ok) {
    experiment._dir_name = (await dirRes.json()).dir_name;
  }

  if (!experiment.steps.length) {
    document.getElementById('steps-container').innerHTML =
      '<p style="color:var(--gray-500);font-size:.85rem;">暂无步骤，点击下方按钮添加或返回首页用AI生成</p>';
    return;
  }
  renderStepList();
  if (currentStepIdx < 0 || currentStepIdx >= experiment.steps.length) {
    selectStep(0);
  } else {
    selectStep(currentStepIdx);
  }
}

async function saveExperiment() {
  await fetch('/api/experiments/' + EXPERIMENT_ID, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(experiment),
  });
}

function renderStepList() {
  var container = document.getElementById('steps-container');
  container.innerHTML = experiment.steps.map(function(s, i) {
    var cls = ['step-item'];
    if (s.completed) cls.push('completed');
    if (i === currentStepIdx) cls.push('active');
    return '<div class="' + cls.join(' ') + '" onclick="selectStep(' + i + ')">' +
      '<div class="step-checkbox" onclick="event.stopPropagation();toggleStep(' + i + ')">' + (s.completed ? '✓' : '') + '</div>' +
      '<span class="step-title">' + (i + 1) + '. ' + escHtml(s.title) + '</span>' +
    '</div>';
  }).join('');
}

function selectStep(idx) {
  currentStepIdx = idx;
  renderStepList();
  renderStepDetail();
}

async function toggleStep(idx) {
  experiment.steps[idx].completed = !experiment.steps[idx].completed;
  await saveExperiment();
  renderStepList();
  if (idx === currentStepIdx) renderStepDetail();
}

function renderStepDetail() {
  var detail = document.getElementById('step-detail');

  if (currentStepIdx < 0 || !experiment.steps.length) {
    detail.innerHTML = '<p style="color:var(--gray-500);text-align:center;padding:40px;">请从左侧选择一个步骤</p>';
    return;
  }

  var s = experiment.steps[currentStepIdx];

  var photosHtml = (s.photos || []).map(function(p) {
    return '<img src="/data/' + getExpDirName() + '/' + p + '" onclick="openPhoto(\'/data/' + getExpDirName() + '/' + p + '\')" alt="实验照片">';
  }).join('');

  var dataFieldsHtml = (s.data_fields || []).map(function(f, fi) {
    return '<tr>' +
      '<td><input value="' + escHtml(f.label) + '" onchange="updateDataField(' + fi + ',\'label\',this.value)" placeholder="名称"></td>' +
      '<td><input value="' + escHtml(f.value) + '" onchange="updateDataField(' + fi + ',\'value\',this.value)" placeholder="数值"></td>' +
      '<td><input value="' + escHtml(f.unit) + '" onchange="updateDataField(' + fi + ',\'unit\',this.value)" placeholder="单位" style="width:60px;"></td>' +
      '<td><button class="btn btn-danger btn-sm" onclick="deleteDataField(' + fi + ')">x</button></td>' +
    '</tr>';
  }).join('');

  detail.innerHTML =
    '<h2>步骤 ' + s.id + '：' + escHtml(s.title) +
      ' <button class="btn btn-danger btn-sm" onclick="deleteStep(' + currentStepIdx + ')" style="float:right;">删除步骤</button>' +
    '</h2>' +

    '<div class="form-group">' +
      '<label>操作说明</label>' +
      '<textarea onchange="updateStepField(\'instruction\', this.value)">' + escHtml(s.instruction) + '</textarea>' +
    '</div>' +

    '<div class="form-group">' +
      '<label>实验现象</label>' +
      '<textarea onchange="updateStepField(\'observation\', this.value)" placeholder="记录你观察到的现象...">' + escHtml(s.observation || '') + '</textarea>' +
    '</div>' +

    '<div class="form-group">' +
      '<label>实验数据</label>' +
      '<table class="data-table">' +
        '<thead><tr><th>数据项</th><th>数值</th><th>单位</th><th></th></tr></thead>' +
        '<tbody id="data-table-body">' + dataFieldsHtml + '</tbody>' +
      '</table>' +
      '<button class="btn btn-outline btn-sm" style="margin-top:6px;" onclick="addDataField()">+ 添加数据项</button>' +
    '</div>' +

    '<div class="form-group">' +
      '<label>照片</label>' +
      '<input type="file" accept="image/*" multiple onchange="uploadPhotos(this)" style="margin-bottom:8px;">' +
      '<div class="photo-grid" id="photo-grid">' + photosHtml + '</div>' +
    '</div>' +

    '<div class="ai-notes">' +
      renderNote('注意事项', s.ai_notes && s.ai_notes.precautions, 'note-precautions') +
      renderNote('预测现象', s.ai_notes && s.ai_notes.prediction, 'note-prediction') +
      renderNote('安全提醒', s.ai_notes && s.ai_notes.safety, 'note-safety') +
    '</div>';
}

function renderNote(label, text, cls) {
  if (!text) return '';
  return '<div class="note-block ' + cls + '">' +
    '<div class="note-label">' + label + '</div>' +
    '<div>' + escHtml(text) + '</div>' +
  '</div>';
}

async function updateStepField(field, value) {
  experiment.steps[currentStepIdx][field] = value;
  await saveExperiment();
}

async function updateDataField(fi, key, value) {
  experiment.steps[currentStepIdx].data_fields[fi][key] = value;
  await saveExperiment();
}

async function addDataField() {
  experiment.steps[currentStepIdx].data_fields = experiment.steps[currentStepIdx].data_fields || [];
  experiment.steps[currentStepIdx].data_fields.push({ label: '', value: '', unit: '' });
  await saveExperiment();
  renderStepDetail();
}

async function deleteDataField(fi) {
  experiment.steps[currentStepIdx].data_fields.splice(fi, 1);
  await saveExperiment();
  renderStepDetail();
}

async function uploadPhotos(input) {
  var files = input.files;
  for (var i = 0; i < files.length; i++) {
    var form = new FormData();
    form.append('photo', files[i]);
    var stepId = experiment.steps[currentStepIdx].id;
    var res = await fetch('/api/experiments/' + EXPERIMENT_ID + '/upload-photo/' + stepId, {
      method: 'POST',
      body: form,
    });
    var data = await res.json();
    if (data.path) {
      experiment.steps[currentStepIdx].photos.push(data.path);
      await saveExperiment();
    }
  }
  renderStepDetail();
  input.value = '';
}

function openPhoto(url) {
  var w = window.open('', '_blank');
  w.document.write('<img src="' + url + '" style="max-width:100%;max-height:100vh;">');
}

function getExpDirName() {
  return experiment && experiment._dir_name ? experiment._dir_name : '';
}

async function addStep() {
  var newId = Math.max.apply(null, experiment.steps.map(function(s) { return s.id; }).concat([0])) + 1;
  experiment.steps.push({
    id: newId,
    title: '新步骤',
    instruction: '',
    completed: false,
    observation: '',
    photos: [],
    data_fields: [],
    ai_notes: { precautions: '', prediction: '', safety: '' },
  });
  await saveExperiment();
  selectStep(experiment.steps.length - 1);
}

async function deleteStep(idx) {
  if (!confirm('确定删除步骤 "' + experiment.steps[idx].title + '" 吗？此操作不可撤销。')) return;
  experiment.steps.splice(idx, 1);
  await saveExperiment();
  if (currentStepIdx >= experiment.steps.length) {
    currentStepIdx = experiment.steps.length - 1;
  }
  renderStepList();
  if (currentStepIdx >= 0) {
    renderStepDetail();
  } else {
    document.getElementById('step-detail').innerHTML =
      '<p style="color:var(--gray-500);text-align:center;padding:40px;">请从左侧选择一个步骤</p>';
  }
}

function exportWord() {
  window.open('/api/experiments/' + EXPERIMENT_ID + '/export-word', '_blank');
  showToast('Word 文档已开始下载');
}

loadExperiment();
