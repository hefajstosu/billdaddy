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
  products.forEach((p) => {
    const opt = document.createElement('option');
    opt.value = p.name;
    $('#product-list').appendChild(opt);
  });
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
  const cat = categorySelect(it.category ? it.category.id : null);
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
  } catch (err) {
    $('#confirm-status').textContent = 'błąd: ' + err.message;
    $('#confirm-status').className = 'text-sm text-red-600';
  }
});

loadLists();
