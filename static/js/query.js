function runQuery(path) {
    fetch(`${window.origin}/` + path, {
            method: "POST",
            credentials: "include",
            body: JSON.stringify($(".form-control").val()),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        }).then(response => response.json())
        .then(data => {
            var str = JSON.stringify(JSON.parse(data), undefined, 4);
            const list = document.getElementById("JSON")
            if (list.hasChildNodes()) {
                list.removeChild(list.childNodes[0]);
            }
            document.getElementById("JSON").appendChild(document.createElement('pre')).innerHTML = syntaxHighlight(str);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}