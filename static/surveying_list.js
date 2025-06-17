document.getElementById("csv-export-btn").addEventListener("click", function () {
    const rows = document.querySelectorAll("table tbody tr");
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";

    // ヘッダー取得
    const headers = Array.from(document.querySelectorAll("table thead th"))
                        .map(th => `"${th.textContent.trim().replace(/"/g, '""')}"`)
                        .join(",");
    csvContent += headers + "\n";

    rows.forEach(row => {
        if (row.style.display !== "none") {
            const tds = row.querySelectorAll("td");

            // 「詳細」「切替」「管理」は列番号で空白にする（0始まり）
            // 例：詳細(8), 切替(9), 管理(10) → 空白にする
            // それ以外は基本テキスト取得。ただし「状態」(5列目)だけ特別扱い

            let cols = [];

            tds.forEach((td, i) => {
                // 8,9,10列目は空白
                if ([8,9,10].includes(i)) {
                    cols.push('""');
                }
                // 状態(5)列は状態表示spanのテキストを使う
                else if (i === 5) {
                    const statusSpan = td.querySelector("span.status-display");
                    const statusText = statusSpan ? statusSpan.textContent.trim() : td.textContent.trim();
                    cols.push(`"${statusText.replace(/"/g, '""')}"`);
                }
                else {
                    // それ以外は編集用inputが表示されていればその値、それ以外はテキスト全体
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
    link.setAttribute("download", "surveying_list.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});


// 「検索」ボタンを押した時に検索を実行
document.getElementById("search-button").addEventListener("click", filterTable);

// 出庫中チェックボックスは変わったら即フィルターかける（必要なら）
document.getElementById("shippedOnlyCheckbox").addEventListener("change", filterTable);

// filterTable関数はそのまま使う
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

function toggleDeleteColumn() {
  const deleteCols = document.querySelectorAll('.delete-column');
  let isEditing = false;
  
  deleteCols.forEach(col => {
    if (col.style.display === 'none' || col.style.display === '') {
      col.style.display = 'table-cell'; // 表示
      col.classList.remove('hidden');
      isEditing = true;
    } else {
      col.style.display = 'none'; // 非表示
      col.classList.add('hidden');
    }
  });

  // PDFリンク表示切替
  document.querySelectorAll('.pdf-link').forEach(el => {
    el.style.display = isEditing ? 'inline' : 'none';
  });
}


// 出庫先詳細ポップアップ表示
function showShipmentDetails(toolId) {
    const popup = document.getElementById(`shipment-details-popup-${toolId}`);
    if (popup) {
        popup.style.display = 'flex';
    }
}

// 出庫先詳細ポップアップ閉じる
function closePopup(toolId) {
    const popup = document.getElementById(`shipment-details-popup-${toolId}`);
    if (popup) {
        popup.style.display = 'none';
    }
}

// 点検日変更ポップアップ表示
function showInspectionPopup(toolId) {
    const popup = document.getElementById(`inspection-popup-${toolId}`);
    if (popup) {
        popup.style.display = 'flex';
    }
}

// 点検日変更ポップアップ閉じる
function closeInspectionPopup(toolId) {
    const popup = document.getElementById(`inspection-popup-${toolId}`);
    if (popup) {
        popup.style.display = 'none';
    }
}

// 出庫先詳細フォームの削除ボタン（フォームの値をリセット）
function clearShipmentFields(toolId) {
    document.getElementById(`company-name-${toolId}`).value = '';
    document.getElementById(`shipment-site-${toolId}`).value = '';
    document.getElementById(`start-date-${toolId}`).value = '';
    document.getElementById(`end-date-${toolId}`).value = '';
}

function toggleStateForm(toolId) {
    const form = document.getElementById(`state-form-${toolId}`);
    if (form.classList.contains('hidden')) {
        form.classList.remove('hidden');
    } else {
        form.classList.add('hidden');
    }
}

function toggleEditMode(button) {
  const row = button.closest('tr');
  const toolId = row.dataset.toolId;

  const displayTexts = row.querySelectorAll('.display-text');
  const editInputs = row.querySelectorAll('.edit-input');

    // 編集モード判定
  const isEditing = editInputs[0].style.display === 'inline-block';

    // 「保存」状態 → サーバに送信して保存
  if (isEditing) {
    const data = {
      tool_type: editInputs[0].value.trim(),
      name: editInputs[1].value.trim(),
      manufacturer: editInputs[2].value.trim(),
      serial_number: editInputs[3].value.trim()
    };

    fetch(`/update_surveying_tool/${toolId}`, {
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
        span.textContent = data[['tool_type','name','manufacturer','serial_number'][i]];
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

// CSRFトークンを<meta>タグから取得する例
function getCsrfToken() {
  const meta = document.querySelector('meta[name=csrf-token]');
  return meta ? meta.content : '';
}

function toggleStatusSelect(toolId) {
  const form = document.getElementById(`status-form-${toolId}`);
  form.style.display = (form.style.display === 'none' || form.style.display === '') ? 'inline-block' : 'none';
}

function cancelStatusChange(toolId) {
  const form = document.getElementById(`status-form-${toolId}`);
  form.style.display = 'none';
}


