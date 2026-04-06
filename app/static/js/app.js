const $ = (sel) => document.querySelector(sel);

async function api(url, opts) {
  const res = await fetch(url, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function renderDraft(receipt) {
  $('#draft').classList.remove('hidden');
  $('#draft-info').textContent =
    `${receipt.shop_name || '?'} • ${receipt.purchase_date || 'brak daty'} • suma ${receipt.total_amount ?? '?'} zł`;

  const tbody = $('#draft-items');
  tbody.innerHTML = '';
  receipt.items.forEach((it) => {
    const tr = document.createElement('tr');
    tr.className = 'border-b';
    tr.innerHTML = `
      <td class="py-1 font-mono text-xs">${it.raw_name}</td>
      <td>${it.product ? it.product.name : '<i class="text-gray-400">nowy</i>'}</td>
      <td>${it.category ? it.category.name : ''}</td>
      <td class="text-right">${it.quantity}</td>
      <td class="text-right">${it.price_per_unit}</td>`;
    tbody.appendChild(tr);
  });
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
