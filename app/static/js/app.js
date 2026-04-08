const $ = (sel) => document.querySelector(sel);

let categories = [];
let products = [];
let currentReceipt = null;

async function api(url, opts) {
  const res = await fetch(url, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

async function loadLists() {
  [categories, products] = await Promise.all([api('/api/categories'), api('/api/products')]);
  $('#product-list').innerHTML = '';
  const prev = $('#price-product').value;
  $('#price-product').innerHTML = '';
  products.forEach((p) => {
    const opt = document.createElement('option');
    opt.value = p.name;
    $('#product-list').appendChild(opt);
    $('#price-product').appendChild(new Option(p.name, p.id));
  });
  if (prev) $('#price-product').value = prev;
  loadPrices();
}

function categorySelect(selectedId) {
  const sel = document.createElement('select');
  sel.className = 'border rounded px-1 py-1 w-full';
  categories.forEach((c) => {
    const opt = new Option(c.name, c.id);
    if (c.id === selectedId) opt.selected = true;
    sel.appendChild(opt);
  });
  return sel;
}

function input(value, cls, type = 'text') {
  const el = document.createElement('input');
  el.type = type;
  el.value = value ?? '';
  el.className = 'border rounded px-2 py-1 w-full ' + (cls || '');
  if (type === 'number') el.step = 'any';
  return el;
}

function addRow(it = {}) {
  const tr = document.createElement('tr');
  tr.className = 'border-b';

  const raw = document.createElement('td');
  raw.className = 'py-1 pr-2 font-mono text-xs';
  raw.textContent = it.raw_name || '-';
  tr.dataset.raw = it.raw_name || '';

  const name = input(it.product ? it.product.name : '', '');
  name.setAttribute('list', 'product-list');
  const cat = categorySelect(it.category ? it.category.id : it.product?.category_id);
  // picking existing product -> use its category
  name.addEventListener('change', () => {
    const p = products.find((p) => p.name === name.value);
    if (p) cat.value = p.category_id;
  });

  const qty = input(it.quantity ?? 1, 'text-right w-20', 'number');
  const price = input(it.price_per_unit ?? '', 'text-right w-24', 'number');

  const del = document.createElement('button');
  del.type = 'button';
  del.textContent = '✕';
  del.className = 'text-gray-400 hover:text-red-600 px-2';
  del.onclick = () => tr.remove();

  [raw, name, cat, qty, price, del].forEach((el, i) => {
    if (i === 0) return tr.appendChild(el);
    const td = document.createElement('td');
    td.className = 'py-1 pr-2';
    td.appendChild(el);
    tr.appendChild(td);
  });
  $('#draft-items').appendChild(tr);
}

function renderDraft(receipt) {
  currentReceipt = receipt;
  $('#draft').classList.remove('hidden');
  $('#d-shop').value = receipt.shop_name || '';
  $('#d-date').value = receipt.purchase_date || '';
  $('#d-total').value = receipt.total_amount ?? '';
  $('#confirm-status').textContent = '';
  $('#draft-items').innerHTML = '';
  receipt.items.forEach((it) => addRow(it));
}

function collectDraft() {
  const items = [...$('#draft-items').children].map((tr) => {
    const [name, cat, qty, price] = tr.querySelectorAll('input, select');
    return {
      raw_name: tr.dataset.raw || name.value,
      product_name: name.value.trim(),
      category_id: Number(cat.value),
      quantity: qty.value,
      price_per_unit: price.value,
    };
  });
  return {
    shop_name: $('#d-shop').value,
    purchase_date: $('#d-date').value || null,
    total_amount: $('#d-total').value || null,
    items,
  };
}

$('#upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  $('#upload-status').textContent = 'czytam paragon...';
  try {
    const receipt = await api('/api/receipts', { method: 'POST', body: new FormData(e.target) });
    renderDraft(receipt);
    $('#upload-status').textContent = '';
    loadReceipts();
  } catch (err) {
    $('#upload-status').textContent = 'błąd: ' + err.message;
  }
});

$('#add-row').addEventListener('click', () => addRow());

$('#confirm').addEventListener('click', async () => {
  try {
    const res = await api(`/api/receipts/${currentReceipt.id}/confirm`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(collectDraft()),
    });
    if (res.total_mismatch) {
      $('#confirm-status').textContent = `zapisane, ale suma pozycji (${res.computed_total}) ≠ suma z paragonu`;
      $('#confirm-status').className = 'text-sm text-amber-600';
    } else {
      $('#confirm-status').textContent = 'zapisane ✓';
      $('#confirm-status').className = 'text-sm text-emerald-700';
    }
    loadLists();
    loadPie();
    loadReceipts();
  } catch (err) {
    $('#confirm-status').textContent = 'błąd: ' + err.message;
    $('#confirm-status').className = 'text-sm text-red-600';
  }
});

loadLists();

// --- charts ---
const COLORS = ['#059669', '#2563eb', '#d97706', '#dc2626', '#7c3aed', '#db2777',
  '#0891b2', '#65a30d', '#ea580c', '#4b5563', '#a16207'];

async function loadPie() {
  const params = new URLSearchParams();
  if ($('#f-from').value) params.set('from', $('#f-from').value);
  if ($('#f-to').value) params.set('to', $('#f-to').value);
  const rows = await api('/api/stats/categories?' + params);

  new Chart($('#pie'), {
    type: 'doughnut',
    data: {
      labels: rows.map((r) => r.category),
      datasets: [{ data: rows.map((r) => r.total), backgroundColor: COLORS }],
    },
    options: { plugins: { legend: { position: 'bottom' } } },
  });
  const sum = rows.reduce((a, r) => a + r.total, 0);
  $('#pie-total').textContent = `razem ${sum.toFixed(2)} zł`;
}

$('#f-from').addEventListener('change', loadPie);
$('#f-to').addEventListener('change', loadPie);
loadPie();

async function loadPrices() {
  const id = $('#price-product').value;
  if (!id) return;
  const data = await api(`/api/stats/prices/${id}`);

  new Chart($('#line'), {
    type: 'line',
    data: {
      labels: data.points.map((p) => p.date),
      datasets: [{
        label: data.product.name,
        data: data.points.map((p) => p.price),
        borderColor: '#059669',
        tension: 0.2,
      }],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        tooltip: { callbacks: { afterLabel: (ctx) => data.points[ctx.dataIndex].shop || '' } },
      },
    },
  });

  const el = $('#price-change');
  if (data.change_pct === null) {
    el.textContent = data.points.length ? 'za mało danych' : 'brak zakupów';
    el.className = 'text-sm text-gray-500';
  } else {
    el.textContent = `${data.change_pct > 0 ? '+' : ''}${data.change_pct}% od pierwszego zakupu`;
    el.className = 'text-sm ' + (data.change_pct > 0 ? 'text-red-600' : 'text-emerald-700');
  }
}

$('#price-product').addEventListener('change', loadPrices);

// --- receipts list ---
async function loadReceipts() {
  const rows = await api('/api/receipts');
  const tbody = $('#receipts');
  tbody.innerHTML = '';
  rows.forEach((r) => {
    const tr = document.createElement('tr');
    tr.className = 'border-b';
    const cells = [r.purchase_date || '-', r.shop_name || '?',
      r.total_amount != null ? r.total_amount.toFixed(2) : '-', r.status];
    cells.forEach((v, i) => {
      const td = document.createElement('td');
      td.className = 'py-1' + (i === 2 ? ' text-right' : '');
      td.textContent = v;
      tr.appendChild(td);
    });

    const td = document.createElement('td');
    td.className = 'text-right space-x-2';
    const edit = document.createElement('button');
    edit.textContent = 'edytuj';
    edit.className = 'text-emerald-700 hover:underline';
    edit.onclick = async () => {
      renderDraft(await api(`/api/receipts/${r.id}`));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    const del = document.createElement('button');
    del.textContent = 'usuń';
    del.className = 'text-red-600 hover:underline';
    del.onclick = async () => {
      await fetch(`/api/receipts/${r.id}`, { method: 'DELETE' });
      loadReceipts();
      loadPie();
    };
    td.append(edit, del);
    tr.appendChild(td);
    tbody.appendChild(tr);
  });
}

loadReceipts();
