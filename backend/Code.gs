// ============================================================
// CollabHive — Google Sheets backend (Apps Script Web App)
// Paste this whole file into a NEW standalone Apps Script project
// (script.google.com > New project), then Deploy as a Web App.
// See SETUP.md for the full steps.
//
// Script Properties to set (Project Settings > Script Properties):
//   SHEET_ID  = the Google Sheet ID (from its URL between /d/ and /edit)
//   ADMIN_KEY = your admin key (used to view brands/bookings/stats)
// ============================================================

var SHEET_ID = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
var ADMIN_KEY = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY') || 'collabhive';

// column order per sheet (headers auto-created on first access)
var SHEETS = {
  creators: ['timestamp', 'name', 'handle', 'niche', 'followers', 'city', 'rate', 'links', 'about'],
  brands:   ['timestamp', 'business', 'category', 'city', 'budget', 'goal', 'link', 'notes'],
  bookings: ['timestamp', 'brand', 'creator', 'niche', 'city', 'status']
};

function ss_() { return SpreadsheetApp.openById(SHEET_ID); }

function sheet_(name) {
  var ss = ss_();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(SHEETS[name]);
  }
  return sh;
}

function requireKey_(e) {
  var key = (e && e.parameter && e.parameter.key) || '';
  return key === ADMIN_KEY;
}

function listRows_(name) {
  var sh = sheet_(name);
  var data = sh.getDataRange().getValues();
  if (data.length < 2) return [];
  var headers = data[0];
  var out = [];
  for (var i = 1; i < data.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) {
      obj[headers[j]] = (data[i][j] === undefined || data[i][j] === null) ? '' : data[i][j];
    }
    out.push(obj);
  }
  return out;
}

function appendRow_(name, obj) {
  var sh = sheet_(name);
  var cols = SHEETS[name];
  var vals = cols.map(function (c) { return (obj[c] === undefined || obj[c] === null) ? '' : obj[c]; });
  sh.appendRow(vals);
  return vals;
}

function output_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  e = e || {};
  var action = (e.parameter && e.parameter.action) || '';
  var sheetName = (e.parameter && e.parameter.sheet) || '';
  try {
    if (action === 'list') {
      if (sheetName !== 'creators' && !requireKey_(e)) return output_({ error: 'unauthorized' });
      if (!SHEETS[sheetName]) return output_({ error: 'bad sheet' });
      return output_({ rows: listRows_(sheetName) });
    }
    if (action === 'stats') {
      if (!requireKey_(e)) return output_({ error: 'unauthorized' });
      return output_({
        brands: listRows_('brands').length,
        creators: listRows_('creators').length,
        bookings: listRows_('bookings').length
      });
    }
    return output_({ error: 'unknown action' });
  } catch (err) {
    return output_({ error: String(err) });
  }
}

function doPost(e) {
  e = e || {};
  var action = (e.parameter && e.parameter.action) || '';
  var sheetName = (e.parameter && e.parameter.sheet) || '';
  try {
    if (action === 'add') {
      if (!SHEETS[sheetName]) return output_({ error: 'bad sheet' });
      var obj = {};
      try { obj = JSON.parse((e.postData && e.postData.contents) || '{}'); } catch (err) { obj = {}; }
      appendRow_(sheetName, obj);
      return output_({ ok: true });
    }
    return output_({ error: 'unknown action' });
  } catch (err) {
    return output_({ error: String(err) });
  }
}
