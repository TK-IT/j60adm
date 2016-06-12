function get_persons() {
    function get_person(o) {
        return JSON.parse(o.getAttribute('data-person'));
    }
    var personList = document.getElementById('person-list');
    var personElements = personList.querySelectorAll('li[data-person]');
    var persons = [].slice.call(personElements).map(get_person);
    personList.style.display = 'none';
    return persons;
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
    if (values.length === 0) return function indexOf(a,b) { return -1; }
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

function combine_index(f1, f2) {
    return function indexOf(searchValue, fromIndex) {
        var i1 = f1(searchValue, fromIndex);
        var i2 = f2(searchValue, fromIndex);
        if (i1 === -1 || i2 === -1) return Math.max(i1, i2);
        else return Math.min(i1, i2);
    }
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
