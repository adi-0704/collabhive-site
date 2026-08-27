// ============================================================
// CollabHive — Influencer Outreach Tracker: ONE-CLICK Google Form builder
// ----------------------------------------------------------------------
// What this does (no manual form building needed):
//   1. run the buildOutreachForm() function once
//   2. It creates a Google Form with all the outreach fields below
//   3. It auto-creates and links a response spreadsheet named
//      "CollabHive Outreach Responses"
//   4. It prints the Form URL + a link so you can preview responses
//
// Setup:
//   script.google.com > New project > paste this whole file >
//   select buildOutreachForm in the dropdown > press Run > authorize.
//
// Optional: onFormSubmit() auto-logs a row into your main CollabHive
//   Sheet (backend/Code.gs style) into an "outreach" sheet. See below.
//
// NOTE: Google Forms CANNOT send Instagram/Twitter DMs. This form is your
//   data-collection sheet: you DM influencers yourself, then log the
//   result/response here so everything is tracked in one place.
// ============================================================

// ---- 1. EDIT THESE BEFORE RUNNING --------------------------------
var FORM_TITLE = "CollabHive — Influencer Outreach Log";
var SPREADSHEET_NAME = "CollabHive Outreach Responses";

// Whoever submits the form gets an email confirmation with a copy of their
// submission, AND you get notified. Set to the Gmail address the script runs
// as (must be re-entered in the form itself if someone else submits).
// Leave "" to disable all email.
var NOTIFY_EMAIL = "collabhive.in@gmail.com";
// ==================================================================


/** Build the entire form + linked response spreadsheet in one shot. */
function buildOutreachForm() {
  var form = FormApp.create(FORM_TITLE);
  form.setDescription('Log every influencer you DM. One row per outreach. Data lands in the linked spreadsheet.');

  form.addTextItem()
    .setTitle('Date of outreach')
    .setHelpText('YYYY-MM-DD or DD/MM/YYYY')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Influencer name')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Handle / username')
    .setHelpText('e.g. @aarav.eats')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('DM message sent (paste what you sent or the pitch)')
    .setRequired(false);

  var platform = form.addCheckboxItem()
    .setTitle('Platform(s) you DMed on')
    .setRequired(true);
  platform.setChoiceValues(['Instagram', 'YouTube', 'X / Twitter', 'LinkedIn', 'Email', 'Other']);

  form.addTextItem()
    .setTitle('Niche')
    .setHelpText('e.g. Food, Fashion, Travel, Fitness, Tech')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Followers (approx.)')
    .setHelpText('e.g. 24.5K, 1.2M')
    .setRequired(false);

  form.addTextItem()
    .setTitle('City / location')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Contact (email / phone / WhatsApp)')
    .setRequired(false);

  var status = form.addMultipleChoiceItem()
    .setTitle('Response status')
    .setRequired(true);
  status.setChoiceValues([
    'Sent — awaiting reply',
    'Replied — interested',
    'Replied — negotiating',
    'No reply',
    'Declined',
    'Collaborating / booked'
  ]);

  form.addTextItem()
    .setTitle('Proposed rate / offer')
    .setRequired(false);

  form.addParagraphTextItem()
    .setTitle('Notes / next steps')
    .setRequired(false);

  // Email field: collect the submitter's email so we can confirm + notify.
  // Only added when notifications are enabled.
  if (NOTIFY_EMAIL) {
    form.addTextItem()
      .setTitle('Your email (for a confirmation of this submission)')
      .setHelpText('An email confirmation + notification are only sent if you fill this in.')
      .setRequired(false);
  }

  // Link a spreadsheet for responses: every submission auto-lands here.
  Logger.log('Creating + linking response spreadsheet...');
  var ss = SpreadsheetApp.create(SPREADSHEET_NAME);
  var formUrl = FormApp.openById(form.getId());
  formUrl.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  Logger.log('Linked spreadsheet: ' + ss.getUrl());

  // Attach an on-submit trigger so every response fires an email.
  if (NOTIFY_EMAIL) {
    ScriptApp.newTrigger('outreachEmailNotification')
      .forForm(form.getId())
      .onFormSubmit()
      .create();
    PropertiesService.getScriptProperties().setProperty('FORM_ID', form.getId());
    PropertiesService.getScriptProperties().setProperty('NOTIFY_EMAIL', NOTIFY_EMAIL);
    Logger.log('Email notification enabled -> ' + NOTIFY_EMAIL);
  } else {
    Logger.log('Email disabled (NOTIFY_EMAIL empty).');
  }

  Logger.log('==================================================');
  Logger.log('FORM URL (copy + share this):');
  Logger.log(form.getPublishedUrl());
  Logger.log('RESPONSES SHEET (where data auto-appears): ' + ss.getUrl());
  Logger.log('==================================================');
}

// ============================================================
// EMAIL NOTIFICATION
// Runs every time someone submits the form. Sends:
//   - a confirmation email to the submitter (if they entered their email)
//   - a notification email to NOTIFY_EMAIL
// Uses MailApp (the script's own authorized account) — NOT an SMTP app
// password, since Apps Script does not accept Gmail app passwords.
// ============================================================
function outreachEmailNotification(e) {
  var props = PropertiesService.getScriptProperties();
  var notify = props.getProperty('NOTIFY_EMAIL') || '';

  // Build a readable body from all answers.
  var lines = [];
  var submitterEmail = '';
  var answers = e.response.getItemResponses();
  for (var i = 0; i < answers.length; i++) {
    var item = answers[i].getItem().getTitle();
    var value = answers[i].getResponse();
    if (Array.isArray(value)) value = value.join(', ');
    if (item.toLowerCase().indexOf('your email') !== -1) {
      submitterEmail = String(value).trim();
      continue; // don't include the email field in the main body body
    }
    lines.push(item + ': ' + value);
  }
  var body = 'A new CollabHive outreach was logged.\n\n' + lines.join('\n');

  // 1) Confirmation to the submitter.
  if (submitterEmail) {
    try {
      MailApp.sendEmail(submitterEmail, 'CollabHive — outreach logged', body);
    } catch (err) {
      Logger.log('Submitter confirmation failed: ' + err);
    }
  }

  // 2) Notification to you.
  if (notify) {
    try {
      MailApp.sendEmail(notify, 'New CollabHive outreach logged', body);
    } catch (err) {
      Logger.log('Owner notification failed: ' + err);
    }
  }
}

// ============================================================
// TEST EMAIL — run this once to confirm delivery works.
// Sends a test message to NOTIFY_EMAIL. Check your Inbox (and Spam).
// ============================================================
function testEmail() {
  var props = PropertiesService.getScriptProperties();
  var notify = props.getProperty('NOTIFY_EMAIL') || NOTIFY_EMAIL;
  if (!notify) { Logger.log('No NOTIFY_EMAIL set.'); return; }
  MailApp.sendEmail(
    notify,
    'CollabHive — email test',
    'This is a delivery test from the CollabHive outreach notification script. If you can see this, email notifications are working.'
  );
  Logger.log('Test email sent to ' + notify + ' — check your Inbox and Spam.');
}

/** (Optional) Mirror each submission into your main CollabHive sheet "outreach" tab.
 *  Set YOUR_MAIN_SHEET_ID below, then create a configureMainSheetTrigger() run once. */
var YOUR_MAIN_SHEET_ID = '';  // paste your main CollabHive spreadsheet ID here

function mirrorToMainSheet(e) {
  if (!YOUR_MAIN_SHEET_ID) { Logger.log('Set YOUR_MAIN_SHEET_ID first.'); return; }
  var ss = SpreadsheetApp.openById(YOUR_MAIN_SHEET_ID);
  var sh = ss.getSheetByName('outreach');
  if (!sh) {
    sh = ss.insertSheet('outreach');
    sh.appendRow(['timestamp', 'date', 'name', 'handle', 'message', 'platform', 'niche', 'followers', 'city', 'contact', 'status', 'rate', 'notes']);
  }
  var r = e.response;
  var row = [new Date()];
  for (var i = 0; i < r.getItemResponses().length; i++) {
    var ir = r.getItemResponses()[i];
    var t = ir.getItem().getTitle();
    var v = ir.getResponse();
    if (Array.isArray(v)) v = v.join(', ');
    // map by the form field titles
    if (t.toLowerCase().indexOf('date') !== -1) row[1] = v;
    else if (t.toLowerCase().indexOf('name') !== -1) row[2] = v;
    else if (t.toLowerCase().indexOf('handle') !== -1) row[3] = v;
    else if (t.toLowerCase().indexOf('message') !== -1) row[4] = v;
    else if (t.toLowerCase().indexOf('platform') !== -1) row[5] = v;
    else if (t.toLowerCase().indexOf('niche') !== -1) row[6] = v;
    else if (t.toLowerCase().indexOf('follower') !== -1) row[7] = v;
    else if (t.toLowerCase().indexOf('city') !== -1) row[8] = v;
    else if (t.toLowerCase().indexOf('contact') !== -1) row[9] = v;
    else if (t.toLowerCase().indexOf('status') !== -1) row[10] = v;
    else if (t.toLowerCase().indexOf('rate') !== -1) row[11] = v;
    else if (t.toLowerCase().indexOf('notes') !== -1) row[12] = v;
  }
  sh.appendRow(row);
}

/** Run once after setting YOUR_MAIN_SHEET_ID to start mirroring submissions. */
function configureMainSheetTrigger() {
  var formId = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  if (!formId) { Logger.log('Run buildOutreachForm() first.'); return; }
  ScriptApp.newTrigger('mirrorToMainSheet').forForm(formId).onFormSubmit().create();
  Logger.log('Mirror trigger created.');
}
