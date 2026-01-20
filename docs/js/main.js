async function initialLoad() {
    getRecords(true)
        .then(data => {
            var tbody = document.getElementById("records-tbody");
            for (const recordData of data) {
                insertRecordRow(tbody, recordData);
            }
        });
}

function insertRecordRow(tbody, data) {
    var record = `${data.w}-${data.l}-${data.t}`;
    var winPercentage = data.w_pct.toFixed(3);
    var allPlayRecord = `${data.ap_w}-${data.ap_l}-${data.ap_t}`;
    var allPlayWinPercentage = data.ap_w_pct.toFixed(3);
    var luckPercentage = data.luck.toFixed(1);
    var pointsFor = data.pf.toFixed(2);
    var pointsAgainst = data.pa.toFixed(2);
    var pointsForPerGame = data.pf_g.toFixed(2);
    var pointsAgainstPerGame = data.pa_g.toFixed(2);
    var rowData = [
        [`${data.manager} (${data.seasons})`, "text-start"],
        [record, null],
        [winPercentage, null],
        [`${pointsFor} (${pointsForPerGame})`, null],
        [`${pointsAgainst} (${pointsAgainstPerGame})`, null],
        [allPlayRecord, null],
        [allPlayWinPercentage, null],
        [luckPercentage, null]
    ];

    var row = document.createElement("tr");
    for (const [columnData, columnClass] of rowData) {
        var column = document.createElement("td");
        if (columnClass) {
            column.classList.add(columnClass);
        }
        column.append(columnData);
        row.append(column);
    }
    tbody.append(row);
}

async function getRecords(is_active) {
    return await loadFile("./data/records.json")
        .then(data => data.filter(entry => entry.active == is_active));
}