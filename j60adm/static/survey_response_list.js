function get_persons() {
    function get_person(o) {
        return JSON.parse(o.getAttribute('data-person'));
    }
    var personElements = document.querySelectorAll('#person-list > li[data-person]');
    return [].slice.call(personElements).map(get_person);
}

function make_index(values) {
    values = [].slice.call(values);
    var m = 0;
    for (var i = 0; i < values.length; ++i)
        if (values[i].length > values[m].length) m = i;
    var fieldLength = values[m].length;
    var haystack = [];
    var none = '@';
    var pad = none.repeat(fieldLength);
    for (var i = 0; i < values.length; ++i)
        haystack.push((none + values[i] + pad).substring(0, fieldLength + 1));
    haystack = haystack.join('');

    return function indexOf(searchValue, fromIndex) {
        if (searchValue === '') return -1;
        if (fromIndex) fromIndex = (fieldLength+1) * fromIndex;
        var i = haystack.indexOf(none + searchValue, fromIndex);
        if (i === -1) return -1;
        else return (i / (fieldLength+1)) | 0;
    }
}

function make_regex_index(values) {
    values = [].slice.call(values);
    var m = 0;
    for (var i = 0; i < values.length; ++i)
        if (values[i].length > values[m].length) m = i;
    var fieldLength = values[m].length;
    var haystack = [];
    var none = '@';
    var pad = none.repeat(fieldLength);
    for (var i = 0; i < values.length; ++i)
        haystack.push((none + values[i] + pad).substring(0, fieldLength + 1));
    haystack = haystack.join('');

    return function indexOf(searchValue, fromIndex) {
        if (searchValue === '') return -1;
        if (fromIndex) fromIndex = (fieldLength+1) * fromIndex;
        else fromIndex = 0;
        var pattern = new RegExp(none + searchValue);
        var mo = pattern.exec(haystack.substring(fromIndex, haystack.length));
        if (mo === null) return -1;
        else return ((mo.index + fromIndex) / (fieldLength+1)) | 0;
    }
}

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

function make_name_index(persons) {
    var names = persons.map(function (p) { return p.name; });
    names = names.map(String.toLowerCase);
    var f = make_regex_index(names);
    return function indexOf(searchValue, fromIndex) {
        var pattern = searchValue.toLowerCase().replace(/ /gi, ' ([^@ ]+ )*');
        return f(pattern, fromIndex);
    };
}

function combine_index(f1, f2) {
    return function indexOf(searchValue, fromIndex) {
        var i1 = f1(searchValue, fromIndex);
        var i2 = f2(searchValue, fromIndex);
        if (i1 === -1 || i2 === -1) return Math.max(i1, i2);
        else return Math.min(i1, i2);
    }
}

function make_person_index(persons) {
    var name = make_name_index(persons);
    var id = make_id_index(persons);
    var title = make_title_index(persons);
    return combine_index(combine_index(name, id), title);
}

function setup_person_complete(persons, indexOf, outputElement) {
    var inputElement = document.createElement('input');
    var personElement = document.createElement('span');

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
        if (v === '') set_person(null);
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

function init() {
    var persons = get_persons();
    console.log(persons);
    var indexOf = make_person_index(persons);
    var toComplete = [].slice.call(document.querySelectorAll('*[data-person-complete]'));
    for (var i = 0; i < toComplete.length; ++i)
        setup_person_complete(persons, indexOf, toComplete[i]);
}

window.addEventListener('load', init);
