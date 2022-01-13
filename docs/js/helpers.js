function saveSelectedTeam(selectedTeam) {
    document.cookie = `selectedTeam=${selectedTeam}`;
}

function loadSelectedTeam() {
    return document.cookie.replace("selectedTeam=", "");
}

async function loadFile(fileName) {
    return await fetch(fileName).then(res => res.json());
}

function replaceContent(elementId, content) {
    var element = document.getElementById(elementId);
    element.innerHTML = "";
    element.append(content);
}