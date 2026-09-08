import { postJson } from '../utils.js';

const STORAGE_KEY = 'varvarova_wishlist';

const root = () => document.documentElement;

const isAuth = () => root().dataset.wishlistAuth === 'true';

const toggleUrl = () => root().dataset.wishlistToggleUrl || '';

const mergeUrl = () => root().dataset.wishlistMergeUrl || '';

function readIds() {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (!Array.isArray(raw)) {
      return [];
    }
    const seen = new Set();
    const ids = [];
    raw.forEach((value) => {
      const id = Number(value);
      if (!Number.isInteger(id) || id < 1 || seen.has(id)) {
        return;
      }
      seen.add(id);
      ids.push(id);
    });
    return ids;
  } catch {
    return [];
  }
}

function writeIds(ids) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
}

function updateCount(count) {
  document.querySelectorAll('[data-wishlist-count]').forEach((node) => {
    node.textContent = count > 0 ? String(count) : '';
  });
}

function markButtons(ids) {
  const set = new Set(ids);
  document.querySelectorAll('[data-wishlist-toggle]').forEach((button) => {
    const id = Number(button.dataset.productId);
    const on = set.has(id);
    button.classList.toggle('is-active', on);
    button.setAttribute('aria-pressed', on ? 'true' : 'false');
    button.setAttribute('aria-label', on ? 'Прибрати з улюбленого' : 'Додати в улюблене');
  });
}

function refreshGuestPage() {
  const page = document.querySelector('[data-wishlist-page]');
  if (!page || isAuth()) {
    return;
  }
  const params = new URLSearchParams(window.location.search);
  if (params.has('ids')) {
    return;
  }
  const ids = readIds();
  if (!ids.length) {
    return;
  }
  params.set('ids', ids.join(','));
  window.location.replace(`${window.location.pathname}?${params.toString()}`);
}

function dropCardIfRemoved(button, inWishlist) {
  if (inWishlist || !document.querySelector('[data-wishlist-page]')) {
    return;
  }
  button.closest('.product-grid__item')?.remove();
  if (!document.querySelector('[data-wishlist-page] .vv-card')) {
    window.location.reload();
  }
}

async function mergeGuestIntoAccount() {
  if (!isAuth()) {
    return;
  }
  const ids = readIds();
  if (!ids.length || !mergeUrl()) {
    return;
  }
  const data = await postJson(mergeUrl(), { ids });
  localStorage.removeItem(STORAGE_KEY);
  updateCount(data.count);
}

async function toggleAuth(productId, button) {
  const data = await postJson(toggleUrl(), { product_id: productId });
  button.classList.toggle('is-active', data.in_wishlist);
  button.setAttribute('aria-pressed', data.in_wishlist ? 'true' : 'false');
  button.setAttribute(
    'aria-label',
    data.in_wishlist ? 'Прибрати з улюбленого' : 'Додати в улюблене',
  );
  updateCount(data.count);
  dropCardIfRemoved(button, data.in_wishlist);
}

function toggleGuest(productId, button) {
  let ids = readIds();
  const on = ids.includes(productId);
  ids = on ? ids.filter((id) => id !== productId) : [...ids, productId];
  writeIds(ids);
  markButtons(ids);
  updateCount(ids.length);
  dropCardIfRemoved(button, !on);
}

function hydrate() {
  if (isAuth()) {
    return;
  }
  const ids = readIds();
  markButtons(ids);
  updateCount(ids.length);
}

document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-wishlist-toggle]');
  if (!button) {
    return;
  }
  event.preventDefault();
  const productId = Number(button.dataset.productId);
  if (!Number.isInteger(productId) || productId < 1) {
    return;
  }
  if (isAuth()) {
    toggleAuth(productId, button);
    return;
  }
  toggleGuest(productId, button);
});

document.body.addEventListener('htmx:afterSwap', () => {
  if (!isAuth()) {
    hydrate();
  }
});

hydrate();
refreshGuestPage();
mergeGuestIntoAccount();
