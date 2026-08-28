// ============================================================
// CollabHive — Brand Brief Form (brands fill it in)
// ------------------------------------------------------------------
// One click builds a BRANDED Google Form where brands submit their
// campaign brief. Responses auto-flow into a spreadsheet that the
// outreach -> auto-match engine reads, so brands you DM/email that
// open the link become matched leads automatically.
//
// WHAT IT DOES:
//   1. Run buildBrandForm() once.
//   2. Creates the form with CollabHive branding + all brief fields.
//   3. Auto-creates + links a response spreadsheet.
//   4. Installs an email trigger: brand gets a confirmation, you get
//      notified of each new brief.
//   5. Logs the FORM URL + RESPONSES SHEET URL.
//
// SETUP: script.google.com > New project > paste > buildBrandForm > Run.
// ============================================================

var BRAND_FORM_TITLE = 'CollabHive — Start a Brand Campaign';
var BRAND_SHEET_NAME = 'CollabHive Brand Briefs';
var NOTIFY_EMAIL = 'collabhive.in@gmail.com';
var LOGO_URL = 'https://adi-0704.github.io/collabhive-site/assets/img/logo.png';
var COMPANY_NAME = 'CollabHive';
var CONTACT_INFO = 'collabhive.in@gmail.com | @collabhive.in';


function buildBrandForm() {
  var form = FormApp.create(BRAND_FORM_TITLE);
  form.setDescription(
    'Tell us about your campaign and we will match you with the right creators ' +
    'from our network. Most brands hear back within 24 hours.'
  );

  if (LOGO_URL) {
    try {
      form.addImageItem()
        .setTitle('CollabHive')
        .setHelpText('CollabHive — Brand & Creator Collaboration Network')
        .setImage(UrlFetchApp.fetch(LOGO_URL).getBlob());
    } catch (e) { Logger.log('Logo skipped: ' + e); }
  }

  form.setConfirmationMessage(
    'Thanks! We received your brief. Our team will review it and reach out with ' +
    'a shortlist of matched creators and a quote.'
  );

  // --- SECTION 1: About your brand ---
  form.addPageBreakItem().setTitle('About your brand').setHelpText('Tell us who you are.');

  form.addTextItem().setTitle('Brand / business name').setRequired(true);
  form.addTextItem().setTitle('Your name').setRequired(true);
  form.addTextItem().setTitle('Email address').setRequired(true);
  form.addTextItem().setTitle('Phone / WhatsApp').setHelpText('With country code, e.g. +91 98765 43210').setRequired(false);
  form.addTextItem().setTitle('City & country').setRequired(true);
  form.addTextItem().setTitle('Website or social link').setRequired(false);

  // --- SECTION 2: Campaign ---
  form.addPageBreakItem().setTitle('Your campaign').setHelpText('What do you need?');

  form.addMultipleChoiceItem()
    .setTitle('What is your primary goal?')
    .setRequired(true)
    .setChoiceValues([
      'Brand awareness',
      'Product launch / reach',
      'Sales / conversions',
      'Footfall or local visits',
      'Content for our own channels',
      'Influencer reviews / UGC'
    ]);

  form.addMultipleChoiceItem()
    .setTitle('Which niche are you in (or closest to)?')
    .setRequired(true)
    .setChoiceValues([
      'Food & Beverage', 'Fashion & Apparel', 'Beauty & Cosmetics',
      'Fitness & Wellness', 'Tech & Startups', 'Travel & Hospitality',
      'Home & Decor', 'Finance', 'Education', 'Other'
    ]);

  form.addTextItem()
    .setTitle('Budget range (INR)')
    .setHelpText('e.g. 15,000 – 30,000')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Number of creators you need')
    .setHelpText('e.g. 4')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Posts per creator')
    .setHelpText('e.g. 1 reel + 2 stories')
    .setRequired(true);

  var timeline = form.addMultipleChoiceItem().setTitle('When do you need this?').setRequired(true);
  timeline.setChoiceValues(['ASAP (next 1 week)', 'Within 2 weeks', 'Within a month', 'Exploring — flexible']);

  // --- SECTION 3: Details ---
  form.addPageBreakItem().setTitle('More details').setHelpText('Optional but helps us match better.');

  form.addCheckboxItem()
    .setTitle('Preferred content formats')
    .setChoiceValues(['Reels', 'Stories', 'YouTube video', 'Photo posts', 'Live / event']);

  form.addParagraphTextItem()
    .setTitle('Describe your campaign / product')
    .setHelpText('What are we promoting, and to whom?')
    .setRequired(false);

  form.addCheckboxItem()
    .setTitle('I agree to be contacted by CollabHive about this campaign')
    .setRequired(true)
    .setChoiceValues(['Yes, I agree.']);

  // --- Auto-linked response spreadsheet ---
  Logger.log('Creating + linking response spreadsheet...');
  var ss = SpreadsheetApp.create(BRAND_SHEET_NAME);
  FormApp.openById(form.getId())
    .setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  Logger.log('Linked spreadsheet: ' + ss.getUrl());

  // --- Email trigger ---
  if (NOTIFY_EMAIL) {
    ScriptApp.newTrigger('brandEmailNotification')
      .forForm(form.getId()).onFormSubmit().create();
    PropertiesService.getScriptProperties().setProperty('BRAND_FORM_ID', form.getId());
    PropertiesService.getScriptProperties().setProperty('BRAND_NOTIFY_EMAIL', NOTIFY_EMAIL);
    Logger.log('Email notification enabled -> ' + NOTIFY_EMAIL);
  }

  Logger.log('==================================================');
  Logger.log('BRAND FORM URL (share with brands):');
  Logger.log(form.getPublishedUrl());
  Logger.log('BRAND BRIEFS SHEET: ' + ss.getUrl());
  Logger.log('==================================================');
}


function brandEmailNotification(e) {
  var notify = PropertiesService.getScriptProperties().getProperty('BRAND_NOTIFY_EMAIL') || '';
  var answers = e.response.getItemResponses();
  var email = '';
  var lines = [];
  for (var i = 0; i < answers.length; i++) {
    var title = answers[i].getItem().getTitle();
    var value = answers[i].getResponse();
    if (Array.isArray(value)) value = value.join(', ');
    if (/email/i.test(title)) email = String(value).trim();
    lines.push(title + ': ' + value);
  }
  var body = 'A new brand brief was submitted.\n\n' + lines.join('\n');

  if (email) {
    try {
      MailApp.sendEmail(email, 'CollabHive — we received your brief',
        'Hi!\n\nThanks for submitting your campaign brief. Our team is reviewing it ' +
        'and will send you a shortlist of matched creators and a quote shortly.\n\n- ' +
        COMPANY_NAME);
    } catch (e) { Logger.log('Brand confirm failed: ' + e); }
  }
  if (notify) {
    try { MailApp.sendEmail(notify, 'New CollabHive brand brief', body); }
    catch (e) { Logger.log('Owner notify failed: ' + e); }
  }
}
