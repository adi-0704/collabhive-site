// ============================================================
// CollabHive — Influencer Application Form (influencers fill it in)
// ------------------------------------------------------------------
// WHAT THIS DOES (one click, no manual form building):
//   1. Run buildInfluencerForm() once.
//   2. It creates a BRANDED Google Form using CollabHive's branding
//      (logo image, colors, title, description).
//   3. It auto-creates and links a response spreadsheet so every
//      influencer application lands there automatically.
//   4. It installs an email trigger: influencer gets a confirmation,
//      and you (collabhive.in@gmail.com) get notified of each new lead.
//   5. Logs the FORM URL + RESPONSES SHEET URL.
//
// SETUP:
//   script.google.com > New project > paste this whole file >
//   select buildInfluencerForm > Run > authorize.
//   Look at the Execution log for your URLs.
// ============================================================

// ---- 1. BRANDING + SETTINGS (edit these) ------------------------
var FORM_TITLE   = 'CollabHive — Influencer Application';
var SHEET_NAME   = 'CollabHive Influencer Leads';

// Logo shown on the form. Use a public, working image URL, or leave "" to
// skip the image entirely (the form still works — just no logo).
var LOGO_URL = '';

// CollabHive brand colors (theme + header).
var THEME_COLOR = '#6C3BFF';   // primary purple
var HEADER_COLOR = '#1E1B2E';  // deep navy

// Where application + confirmation emails go / come from.
// This is YOUR address (the script's authorized account) that gets
// notified of every new application. Leave "" to disable email.
var NOTIFY_EMAIL = 'collabhive.in@gmail.com';

// Who runs / owns this — shown in the form intro + confirmation.
var COMPANY_NAME = 'CollabHive';
var CONTACT_INFO = 'collabhive.in@gmail.com | @collabhive';
// ==================================================================


/** Build the branded influencer application form + linked sheet + email trigger. */
function buildInfluencerForm() {
  var form = FormApp.create(FORM_TITLE);
  form.setDescription(
    'Join the CollabHive creator network. Fill this in and our team will ' +
    'review your profile for brand collaborations. It takes about 2 minutes.'
  );

  // Branding
  if (LOGO_URL) {
    try {
      form.addImageItem()
        .setTitle('CollabHive')
        .setHelpText('CollabHive — Brand & Creator Collaboration Network')
        .setImage(UrlFetchApp.fetch(LOGO_URL).getBlob());
    } catch (err) {
      Logger.log('Logo skipped (could not load ' + LOGO_URL + '): ' + err);
    }
  }
  form.setConfirmationMessage(
    'Thanks for applying, ' + COMPANY_NAME + ' received your details. ' +
    'Our team will reach out if your profile is a good fit.'
  );

  // --- Brand identity ---
  // Note: GAS does not expose full custom hex theming for classic Forms.
  // Brand shows via the logo image + form title + description.
  try {
    form.setThemeColor(FormApp.ThemeColor.PURPLE);
  } catch (err) {
    Logger.log('Theme color not applied: ' + err);
  }

  // --- SECTION 1: About you ---
  form.addPageBreakItem().setTitle('About you').setHelpText('Tell us who you are.');

  form.addTextItem()
    .setTitle('Full name')
    .setHelpText('As it appears on your profiles')
    .setRequired(true);

  var gender = form.addMultipleChoiceItem().setTitle('How should we address you?').setRequired(true);
  gender.setChoiceValues(['He/Him', 'She/Her', 'They/Them', 'Prefer not to say']);

  form.addTextItem()
    .setTitle('Email address')
    .setHelpText('For contracts + payments')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Phone / WhatsApp')
    .setHelpText('With country code, e.g. +91 98765 43210')
    .setRequired(true);

  form.addTextItem()
    .setTitle('City & country')
    .setHelpText('e.g. Delhi, India')
    .setRequired(true);

  form.addDateItem()
    .setTitle('Date of birth')
    .setHelpText('Some campaigns are age-restricted')
    .setRequired(true);

  // --- SECTION 2: Your content ---
  form.addPageBreakItem().setTitle('Your content').setHelpText('Where + what you create.');

  form.addTextItem()
    .setTitle('Instagram handle')
    .setHelpText('e.g. @aarav.eats')
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Platforms you create on')
    .setRequired(true)
    .setChoiceValues(['Instagram', 'YouTube', 'X / Twitter', 'LinkedIn', 'TikTok', 'Snapchat', 'Facebook', 'Other']);

  form.addTextItem()
    .setTitle('Profile link(s) for other platforms')
    .setHelpText('Optional — paste any extra profile URLs')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Primary content niche')
    .setHelpText('e.g. Food, Fashion, Fitness, Travel, Gaming, Beauty, Tech')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Followers (total across platforms)')
    .setHelpText('e.g. 45K, 1.2M')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Average views / reach (per post or video)')
    .setHelpText('e.g. 8K views, 15K reach')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Content formats you make')
    .setHelpText('e.g. Reels, Shorts, long-form video, photos, stories, blogs')
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('How long have you been creating content?')
    .setRequired(false)
    .setChoiceValues(['Less than 6 months', '6\u201312 months', '1\u20132 years', '3\u20135 years', '5+ years']);

  // --- SECTION 3: Collaboration ---
  form.addPageBreakItem().setTitle('Collaboration').setHelpText('Rates, content, and availability.');

  form.addMultipleChoiceItem()
    .setTitle('What kind of collaborations interest you?')
    .setRequired(true)
    .setChoiceValues([
      'Sponsored posts / Reels',
      'Product gifting + reviews',
      'Long-term brand ambassador',
      'Affiliate / commission',
      'Events & activations',
      'All of the above'
    ]);

  form.addTextItem()
    .setTitle('Your rate (starting from)')
    .setHelpText('e.g. ₹5,000 per post — so brands know your baseline')
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Your content preferences')
    .setRequired(false)
    .setChoiceValues([
      'I like creative freedom',
      'I follow brand briefs closely',
      'I like both',
      'Depends on the campaign'
    ]);

  form.addCheckboxItem()
    .setTitle('When are you available?')
    .setRequired(true)
    .setChoiceValues(['Weekdays', 'Weekends', 'Only evenings', 'Flexible / full-time', 'Busy — reach out for scheduling']);

  form.addTextItem()
    .setTitle('Brands you have worked with')
    .setHelpText('List any past brand collaborations (optional)')
    .setRequired(false);

  form.addParagraphTextItem()
    .setTitle('Links to your best 3 recent posts')
    .setHelpText('Paste up to 3 URLs of your strongest content')
    .setRequired(false);

  form.addParagraphTextItem()
    .setTitle('Anything else we should know?')
    .setHelpText('Kits, niche audiences, unique selling points, etc.')
    .setRequired(false);

  // Consent
  form.addCheckboxItem()
    .setTitle('I agree to be contacted by CollabHive about collaborations')
    .setRequired(true)
    .setChoiceValues(['Yes, I agree.']);

  // --- Auto-linked response spreadsheet ---
  Logger.log('Creating + linking response spreadsheet...');
  var ss = SpreadsheetApp.create(SHEET_NAME);
  FormApp.openById(form.getId())
    .setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  Logger.log('Linked spreadsheet: ' + ss.getUrl());

  // --- Email trigger (confirmation + notification) ---
  if (NOTIFY_EMAIL) {
    ScriptApp.newTrigger('influencerEmailNotification')
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
  Logger.log('FORM URL (share this with influencers):');
  Logger.log(form.getPublishedUrl());
  Logger.log('RESPONSES SHEET (leads auto-appear): ' + ss.getUrl());
  Logger.log('==================================================');
}


/** Sends a personalized thank-you to the influencer + a notification to you on every submission. */
function influencerEmailNotification(e) {
  var props = PropertiesService.getScriptProperties();
  var notify = props.getProperty('NOTIFY_EMAIL') || '';

  var lines = [];
  var influencerEmail = '';
  var leadName = '';
  var handle = '';
  var niche = '';
  var answers = e.response.getItemResponses();
  for (var i = 0; i < answers.length; i++) {
    var title = answers[i].getItem().getTitle();
    var value = answers[i].getResponse();
    if (Array.isArray(value)) value = value.join(', ');
    // Capture fields we personalize / route on.
    if (/email/i.test(title)) influencerEmail = String(value).trim();
    if (/full name/i.test(title)) leadName = String(value).trim();
    if (/instagram/i.test(title)) handle = String(value).trim();
    if (/niche/i.test(title)) niche = String(value).trim();
    lines.push(title + ': ' + value);
  }

  var ownerBody = 'A new ' + FORM_TITLE + ' was submitted.\n\n' + lines.join('\n');

  // 1) Personalized thank-you to the influencer.
  if (influencerEmail) {
    try {
      var firstName = leadName ? leadName.split(' ')[0] : 'there';
      var context = '';
      if (handle) context = ' We have your profile noted as ' + handle;
      if (niche) context += (context ? ' with a focus on ' : ' with a focus on ') + niche;
      MailApp.sendEmail(
        influencerEmail,
        'CollabHive — thank you, ' + firstName + '!',
        'Hi ' + firstName + ',\n\n' +
        'Thank you for applying to join the CollabHive creator network.' +
        (context ? context + '.' : '.') +
        '\n\nOur team is going through every application and will reach out ' +
        'if there is a fit for upcoming brand collaborations.\n\n' +
        'While you wait, make sure your profiles are up to date and your best ' +
        'content is easy to find \u2014 it helps us match you faster.\n\n' +
        'Talk soon,\n- ' + COMPANY_NAME + ' (' + CONTACT_INFO + ')'
      );
    } catch (err) {
      Logger.log('Influencer thank-you failed: ' + err);
    }
  }

  // 2) Notification to you (collabhive.in@gmail.com).
  if (notify) {
    try {
      MailApp.sendEmail(notify, 'New CollabHive influencer application', ownerBody);
    } catch (err) {
      Logger.log('Owner notification failed: ' + err);
    }
  }
}


/** Runs a delivery test to NOTIFY_EMAIL. Check Inbox + Spam. */
function testEmail() {
  var notify = PropertiesService.getScriptProperties().getProperty('NOTIFY_EMAIL') || NOTIFY_EMAIL;
  if (!notify) { Logger.log('No NOTIFY_EMAIL set.'); return; }
  MailApp.sendEmail(
    notify,
    'CollabHive — email test',
    'This is a delivery test from the CollabHive influencer application script. If you can see this, email notifications work.'
  );
  Logger.log('Test email sent to ' + notify + ' — check Inbox and Spam.');
}
