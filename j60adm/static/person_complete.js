function make_title_index(persons) {
    var titles = [];
    var titlePerson = [];
    var personStart = [];
    for (var i = 0; i < persons.length; ++i) {
        personStart.push(titles.length);
        for (var j = 0; j < persons[i].titles.length; ++j) {
            var t = persons[i].titles[j].title;
            titlePerson.push(i);
            var period = persons[i].titles[j].period + '';
            period = period.substring(2, 4);
            titles.push(t + period);

            if (t.substring(0, 2) === 'FU') {
                var fu = t.substring(2, t.length).toLowerCase();
                titlePerson.push(i);
                titles.push(fu);
            }
        }
    }
    titles = titles.map(String.toLowerCase);

    return function indexOf(searchValue, fromIndex) {
        if (fromIndex) fromIndex = personStart[fromIndex];
        var i = titles.indexOf(searchValue.toLowerCase(), fromIndex);
        if (i === -1) return i;
        return titlePerson[i];
    }
}

function make_id_index(persons) {
    var ids = persons.map(function (p) { return p.id; });
    return function indexOf(searchValue, fromIndex) {
        searchValue = parseInt(searchValue);
        if (isNaN(searchValue)) return -1;
        else return ids.indexOf(searchValue, fromIndex);
    };
}

function make_person_index(persons) {
    var name = make_name_index(persons);
    var id = make_id_index(persons);
    var title = make_title_index(persons);
    return combine_index(combine_index(name, id), title);
}

function setup_person_complete(persons, indexOf, outputElement) {
    var inputElement = document.createElement('input');
    inputElement.setAttribute('size', '10');
    var personElement = document.createElement('span');
    personElement.style.paddingLeft = '8px';

    var personData = JSON.parse(
        outputElement.getAttribute('data-person-complete'));

    function input_keydown(ev) {
        console.log(ev.keyCode);
    }

    function person_by_id(id) {
        id = parseInt(id);
        if (isNaN(id)) return null;
        for (var i = 0; i < persons.length; ++i) {
            if (persons[i].id === id) return persons[i];
        }
        return null;
    }

    function set_person(p) {
        if (p === null) {
            outputElement.value = '';
            personElement.textContent = '';
        } else {
            outputElement.value = p.id;
            personElement.textContent = p.str;
        }
    }

    function blur(ev) {
        var p = person_by_id(outputElement.value);
        if (p !== null) {
            inputElement.value = p.id;
        }
    }

    function initialize_from_id() {
        var p = person_by_id(outputElement.value);
        if (p !== null) {
            personElement.textContent = p.str;
            inputElement.value = p.id;
            return true;
        }
    }

    function initialize_from_name() {
        var i = indexOf(personData.name);
        if (i !== -1) {
            console.log(persons[i].name);
            set_person(persons[i]);
            inputElement.value = persons[i].id;
            return true;
        }
    }

    function initialize_from_title() {
        if (!personData.title) return;
        var pattern = /(cerm|form|inka|ka..|nf|pr|sekr|vc|fu..) \d\d(\d\d)/;
        var mo = pattern.exec(personData.title);
        if (mo === null) return;
        var k = mo[1].replace(/\$/g, 'S');
        var i = indexOf(k + mo[2]);
        if (i === -1) return;
        var p = persons[i];
        var mo = /\S+ /.exec(p.name);
        if (mo === null) return;
        var foundName = mo[0];
        if (personData.name.substring(0, foundName.length) === foundName) {
            // Same first name, probably legit
            set_person(persons[i]);
            inputElement.value = persons[i].id;
            return true;
        }
    }

    function initial() {
        if (initialize_from_id()) return;
        else if (initialize_from_name()) return;
        else if (initialize_from_title()) return;
    }

    function update() {
        var v = inputElement.value.trim();
        console.log(v);
        if (v === '') return set_person(null);
        var i = indexOf(v);
        if (i !== -1) set_person(persons[i]);
    }

    inputElement.addEventListener('keydown', input_keydown);
    inputElement.addEventListener('blur', blur);
    inputElement.addEventListener('keyup', update);

    initial();

    outputElement.parentNode.insertBefore(inputElement, outputElement);
    outputElement.parentNode.insertBefore(personElement, outputElement);
    outputElement.type = 'hidden';
}

function init_person_complete() {
    var persons = get_persons();
    var indexOf = make_person_index(persons);
    var toComplete = [].slice.call(document.querySelectorAll('*[data-person-complete]'));
    for (var i = 0; i < toComplete.length; ++i)
        setup_person_complete(persons, indexOf, toComplete[i]);
}

window.addEventListener('load', init_person_complete);
