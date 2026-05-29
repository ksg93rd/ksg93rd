// Kismoe — Auth Modal and Session Management

import { supabase, signInWithEmail, signOut, getSession } from './supabase.js';

export let currentUser = null;

export async function initAuth() {
  // Check existing session
  const session = await getSession();
  if (session) currentUser = session.user;
  updateAuthUI();

  // Listen for auth state changes
  supabase.auth.onAuthStateChange((event, session) => {
    currentUser = session?.user ?? null;
    updateAuthUI();
    if (event === 'SIGNED_IN') closeAuthModal();
  });
}

export function requireAuth(callback) {
  if (currentUser) { callback(); return; }
  openAuthModal(callback);
}

function openAuthModal(onSuccess) {
  const modal = document.getElementById('authModal');
  if (!modal) return;
  modal.hidden = false;
  modal._onSuccess = onSuccess;
}

function closeAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) modal.hidden = true;
  if (modal?._onSuccess) { modal._onSuccess(); modal._onSuccess = null; }
}

function updateAuthUI() {
  const btn = document.getElementById('authBtn');
  if (!btn) return;
  if (currentUser) {
    btn.textContent = currentUser.email?.split('@')[0] ?? 'Account';
    btn.dataset.state = 'signed-in';
  } else {
    btn.textContent = 'Sign In';
    btn.dataset.state = 'signed-out';
  }
}

export function bindAuthEvents() {
  // Auth button in nav
  document.getElementById('authBtn')?.addEventListener('click', () => {
    if (currentUser) signOut();
    else openAuthModal();
  });

  // Auth modal form submit
  document.getElementById('authForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('authEmail')?.value?.trim();
    if (!email) return;
    const btn = e.target.querySelector('button[type=submit]');
    btn.textContent = 'Sending magic link…';
    btn.disabled = true;
    const { error } = await signInWithEmail(email);
    if (error) {
      btn.textContent = 'Try again';
      btn.disabled = false;
      document.getElementById('authError').textContent = error.message;
    } else {
      document.getElementById('authForm').innerHTML = '<p class="auth-success">✅ Check your email for a magic sign-in link!</p>';
    }
  });

  // Close on backdrop click
  document.getElementById('authModalBackdrop')?.addEventListener('click', () => {
    document.getElementById('authModal').hidden = true;
  });
}
