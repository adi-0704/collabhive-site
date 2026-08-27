// CollabHive — site config. Edit this ONE file to go live.
//   supabaseUrl / supabaseAnonKey -> Supabase backend (RECOMMENDED). See backend/SUPABASE.md
//   base / adminKey               -> Google Sheets + Apps Script backend (alternative). See backend/SETUP.md
//   ga4Id / pixelId               -> analytics
window.CH_ANALYTICS = window.CH_ANALYTICS || { ga4Id: "", pixelId: "" };
window.CH_API = window.CH_API || {
  supabaseUrl: "https://tfdnmlzvktqjwjjbkoif.supabase.co",
  supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRmZG5tbHp2a3RxandqamJrb2lmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc3MDU1NTEsImV4cCI6MjEwMzI4MTU1MX0.6MiLbqMoyXDio_KwSkgeM3Iev4B0pKACJMKglUf3RkY",
  base: "",
  adminKey: "collabhive"
};

// Live Google Form where influencers apply (auto-logs to the CollabHive Influencer Leads sheet).
// Set CH_ANALYTICS alongside this; see also backend/influencer_form.gs.
window.CH_APPLY = window.CH_APPLY || {
  creatorFormUrl: "https://docs.google.com/forms/d/e/1FAIpQLScIV5PVkwbdcvMpzCyxTAzN71ORCqaTaIMY7Dr15xEMXSxIXQ/viewform",
  brandFormUrl: ""
};
