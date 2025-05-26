
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
                if ([6].includes(i)) {
                    cols.push('""');
                }
                else if (i === 4 || i === 5) {
                    // 新品・中古在庫の列番号に応じて調整（例: i === 4, 5）
                    const display = td.querySelector(".display-text");
                    const raw = display?.dataset.raw || display?.textContent.replace(/[^\d]/g, "");
                    cols.push(`"${raw}"`);
                }
                else if (i === 3) {
                    // 状態列がここなら状態表示を抽出
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
    link.setAttribute("download", "parts_list.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});


// 検索ボタン
document.getElementById("search-button").addEventListener("click", filterTable);

function filterTable() {
    const filter = document.getElementById("search-input").value.toLowerCase();
    // shippedOnly チェックは不要なので常に true に設定
    const matchesShipped = true;

    const rows = document.querySelectorAll("#printable-table tbody tr");

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        // shippedOnly は使わないので無視
        const matchesText = text.includes(filter);

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

// 編集モード切り替え関数
function toggleEditMode(button) {
  const row = button.closest('tr');
  const partId = row.dataset.partId;

  const displayTexts = row.querySelectorAll('.display-text');
  const editInputs = row.querySelectorAll('.edit-input');
  const stockControls = row.querySelectorAll('.stock-control'); // ←追加

  // 編集モード判定（inputの表示状態で判定）
  const isEditing = editInputs[0].style.display === 'inline-block';

  if (isEditing) {
    // 編集モード → 保存処理

    // フォームデータを収集
    const data = {
      part_type: editInputs[0].value.trim(),
      part_name: editInputs[1].value.trim(),
      manufacturer: editInputs[2].value.trim(),
      model_number: editInputs[3].value.trim(),
      new_stock: parseInt(editInputs[4].value.trim()) || 0,
      used_stock: parseInt(editInputs[5].value.trim()) || 0,
      remarks: editInputs[6].value.trim()
    };

    // APIへPATCH送信（POSTでもOK）
    fetch(`/update_part/${partId}`, {
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
      // 更新成功時、入力フォームと「＋」「−」ボタンを非表示にして
      editInputs.forEach(input => input.style.display = 'none');
      stockControls.forEach(btn => btn.style.display = 'none');  // ←追加
      // テキスト表示部分に新しい値を反映し表示
      displayTexts.forEach((span, i) => {
        let value;
        switch(i){
          case 0: value = data.part_type; break;
          case 1: value = data.part_name; break;
          case 2: value = data.manufacturer; break;
          case 3: value = data.model_number; break;
          case 4: value = `${data.new_stock} 個`; break;
          case 5: value = `${data.used_stock} 個`; break;
          case 6: value = data.remarks; break;
        }
        span.textContent = value;
        span.style.display = 'inline-block';
      });
      // ボタン文言を「編集」に戻す
      button.textContent = '編集';
    })
    .catch(err => {
      alert('保存に失敗しました: ' + err.message);
    });

  } else {
    // 表示モード → 編集モードへ切替
    editInputs.forEach(input => input.style.display = 'inline-block');
    stockControls.forEach(btn => btn.style.display = 'inline-block');  // ←追加
    displayTexts.forEach(span => span.style.display = 'none');
    button.textContent = '保存';
  }
}


// CSRFトークン取得
function getCsrfToken() {
  const meta = document.querySelector('meta[name=csrf-token]');
  return meta ? meta.content : '';
}

function changeStock(button, delta) {
  const cell = button.closest('td');
  const input = cell.querySelector('.edit-input');
  const current = parseInt(input.value) || 0;
  const newValue = Math.max(0, current + delta);
  input.value = newValue;
}
