// Custom Timeline JS

// The TL.Timeline constructor takes at least two arguments:
// the id of the Timeline container (no '#'), and
// the URL to your JSON data file or Google spreadsheet.
// the id must refer to an element "above" this code,
// and the element must have CSS styling to give it width and height
// optionally, a third argument with configuration options can be passed.
// See below for more about options.
var additionalOptions = {
    script_path: '/timeline/js/',
    language: 'en',
    font: 'amatic-andika'
}

timeline = new TL.Timeline('timeline-embed',
    'https://docs.google.com/spreadsheets/d/1by_h0BOTLOznb41zDnVZLMfijvqTh6UZ0h3Vc-FIQrM/edit#gid=0');

