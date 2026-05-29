// Kismoe — Supabase Client

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

export const supabase = createClient(
  'https://lfzsqoksvydmvjfkbehl.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmenNxb2tzdnlkbXZqZmtiZWhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwOTUzNjYsImV4cCI6MjA3MDY3MTM2Nn0.KGoozv1MXsC7uq0uo7OQejbrtwV0rqED205T63PXx6E'
);

export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession();
  return session;
}

export async function signInWithEmail(email) {
  return supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.origin } });
}

export async function signOut() {
  return supabase.auth.signOut();
}
