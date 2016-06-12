function init_letter_bounce() {
    var persons = get_persons();
    var indexOf = make_name_index(persons);
    console.log(indexOf('Mathias'));

    var searchElement = document.createElement('input');
    searchElement.placeholder = 'Tilføj returneret brev';
    var searchResult = document.createElement('span');
    searchResult.style.paddingLeft = '8px';
    var searchContainer = document.createElement('div');
    searchContainer.appendChild(searchElement);
    searchContainer.appendChild(searchResult);

    function update() {
        var i = indexOf(searchElement.value);
        if (i === -1) searchResult.textContent = '';
        else searchResult.textContent = persons[i].str;
    }

    function searchElement_keydown(ev) {
        if (ev.keyCode === 13) { // return
            var i = indexOf(searchElement.value.toLowerCase());
            if (i !== -1) {
                searchElement.value = '';
                add_id(persons[i].id);
                update();
                ev.preventDefault();
                return false;
            }
        }
    }

    searchElement.addEventListener('keydown', searchElement_keydown);
    searchElement.addEventListener('keyup', update);

    var personsOutput = document.getElementById('persons');

    var table = document.createElement('table');
    var tbody = document.createElement('tbody');
    table.className = 'letter-bounce'
    table.appendChild(tbody);

    var idSet = {};

    function update_output() {
        var ids = [];
        for (var k in idSet) ids.push(k);
        personsOutput.value = ids.join(',');
    }

    function remove_id(i) {
        delete idSet[i];
        update_output();
    }

    function remove_id_click(i, el) {
        return function onclick(ev) {
            remove_id(i);
            el.parentNode.removeChild(el);
        };
    }

    function add_id(id) {
        console.log("Add", id);
        if (idSet[id]) return;
        idSet[id] = true;
        update_output();

        var i = 0;
        while (i < persons.length) {
            if (persons[i].id == id) break;
            ++i;
        }
        console.log("Add", i, persons.length);
        if (i === persons.length) return;
        var row = document.createElement('tr');
        var cells = [persons[i].str, persons[i].street,
                     persons[i].city, persons[i].country];
        for (var j = 0; j < cells.length; ++j) {
            var cell = document.createElement('td');
            cell.textContent = cells[j];
            row.appendChild(cell);
        }
        var cell = document.createElement('td');
        var button = document.createElement('button');
        button.textContent = 'X';
        button.addEventListener('click', remove_id_click(id, row), false);
        cell.appendChild(button);
        row.appendChild(cell);
        tbody.appendChild(row);
    }

    var ids = ((personsOutput.value.length > 0) ?
        personsOutput.value.split(',').map(function (v) { return parseInt(v); }) : []);
    for (var i = 0; i < ids.length; ++i) add_id(ids[i]);

    personsOutput.parentNode.insertBefore(searchContainer, personsOutput);
    personsOutput.parentNode.insertBefore(table, personsOutput);
    personsOutput.type = 'hidden';
}

window.addEventListener('load', init_letter_bounce);
