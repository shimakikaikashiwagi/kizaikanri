// CSVエクスポート
document.getElementById("csv-export-btn").addEventListener("click", function () {
    const rows = document.querySelectorAll("#printable-table tbody tr");
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";

    // ヘッダー取得
    const headers = Array.from(document.querySelectorAll("#printable-table thead th"))
                        .map(th => `"${th.textContent.trim().replace(/"/g, '""')}"`)
                        .join(",");
    csvContent += headers + "\n";

    rows.forEach(row => {
        if (row.style.display !== "none") {
            const tds = row.querySelectorAll("td");
            let cols = [];

            tds.forEach((td, i) => {
                if ([7,8,9].includes(i)) {
                    cols.push('""');
                }
                else if (i === 4) {
                    const statusSpan = td.querySelector("span.status-display");
                    const statusText = statusSpan ? statusSpan.textContent.trim() : td.textContent.trim();
                    cols.push(`"${statusText.replace(/"/g, '""')}"`);
                }
                else {
                    const input = td.querySelector('input.edit-input');
                    if (input && input.style.display !== 'none') {
                        cols.push(`"${input.value.trim().replace(/"/g, '""')}"`);
                    } else {
                        cols.push(`"${td.textContent.trim().replace(/"/g, '""')}"`);
                    }
                }
            });

            csvContent += cols.join(",") + "\n";
        }
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "system_list.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// 検索ボタン
document.getElementById("search-button").addEventListener("click", filterTable);
// 出庫中チェックボックス
document.getElementById("shippedOnlyCheckbox").addEventListener("change", filterTable);

function filterTable() {
    const filter = document.getElementById("search-input").value.toLowerCase();
    const shippedOnly = document.getElementById("shippedOnlyCheckbox").checked;
    const rows = document.querySelectorAll("#printable-table tbody tr");

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const isShipped = row.classList.contains("shipped");

        const matchesText = text.includes(filter);
        const matchesShipped = shippedOnly ? isShipped : true;

        if (matchesText && matchesShipped) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

// 削除列の表示・非表示切り替え
function toggleDeleteColumn() {
  const deleteCols = document.querySelectorAll('.delete-column');
  deleteCols.forEach(col => {
    if (col.style.display === 'none' || col.style.display === '') {
      col.style.display = 'table-cell'; // 表示
      col.classList.remove('hidden');
    } else {
      col.style.display = 'none'; // 非表示
      col.classList.add('hidden');
    }
  });
}

// 出庫先詳細ポップアップ表示
function showShipmentDetails(SystemId) {
    const popup = document.getElementById(`shipment-details-popup-${SystemId}`);
    if (popup) {
        popup.style.display = 'flex';
    }
}

// 出庫先詳細ポップアップ閉じる
function closePopup(SystemId) {
    const popup = document.getElementById(`shipment-details-popup-${SystemId}`);
    if (popup) {
        popup.style.display = 'none';
    }
}

// 出庫先詳細フォームの削除ボタン（フォームの値をリセット）
function clearShipmentFields(SystemId) {
    document.getElementById(`company-name-${SystemId}`).value = '';
    document.getElementById(`shipment-site-${SystemId}`).value = '';
    document.getElementById(`start-date-${SystemId}`).value = '';
    document.getElementById(`end-date-${SystemId}`).value = '';
}

// 状態フォーム表示切替
function toggleStateForm(SystemId) {
    const form = document.getElementById(`state-form-${SystemId}`);
    if (form.classList.contains('hidden')) {
        form.classList.remove('hidden');
    } else {
        form.classList.add('hidden');
    }
}

// 編集モード切り替え
function toggleEditMode(button) {
  const row = button.closest('tr');
  const SystemId = row.dataset.SystemId;

  const displayTexts = row.querySelectorAll('.display-text');
  const editInputs = row.querySelectorAll('.edit-input');

  const isEditing = editInputs[0].style.display === 'inline-block';

  if (isEditing) {
    const data = {
      System_type: editInputs[0].value.trim(),
      name: editInputs[1].value.trim(),
      manufacturer: editInputs[2].value.trim(),
      serial_number: editInputs[3].value.trim()
    };

    fetch(`/update_system_System/${SystemId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) throw new Error('更新失敗');
      return response.json();
    })
    .then(json => {
      editInputs.forEach(input => input.style.display = 'none');
      displayTexts.forEach((span, i) => {
        span.textContent = data[['System_type','name','manufacturer','serial_number'][i]];
        span.style.display = 'inline-block';
      });
      button.textContent = '編集';
    })
    .catch(err => {
      alert('保存に失敗しました: ' + err.message);
    });

  } else {
    editInputs.forEach(input => input.style.display = 'inline-block');
    displayTexts.forEach(span => span.style.display = 'none');
    button.textContent = '保存';
  }
}

// CSRFトークン取得
function getCsrfToken() {
  const meta = document.querySelector('meta[name=csrf-token]');
  return meta ? meta.content : '';
}

// 状態変更フォーム表示切替
function toggleStatusSelect(SystemId) {
  const form = document.getElementById(`status-form-${SystemId}`);
  form.style.display = (form.style.display === 'none' || form.style.display === '') ? 'inline-block' : 'none';
}

// 状態変更キャンセル
function cancelStatusChange(SystemId) {
  const form = document.getElementById(`status-form-${SystemId}`);
  form.style.display = 'none';
}
