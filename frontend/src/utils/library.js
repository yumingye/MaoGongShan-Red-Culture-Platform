import { readStorage, writeStorage } from './storage'

const FAVORITE_KEY = 'mg_favorites_v2'
const RECENT_KEY = 'mg_recent_views_v2'

function readList(key) {
  const value = readStorage(key, [])
  return Array.isArray(value) ? value : []
}

function writeList(key, list) {
  return writeStorage(key, list)
}

export function getFavorites() {
  return readList(FAVORITE_KEY)
}

export function saveFavorite(item) {
  const list = getFavorites().filter((entry) => entry.key !== item.key)
  writeList(FAVORITE_KEY, [{ ...item, savedAt: new Date().toISOString() }, ...list].slice(0, 200))
}

export function removeFavorite(key) {
  writeList(FAVORITE_KEY, getFavorites().filter((entry) => entry.key !== key))
}

export function isFavorite(key) {
  return getFavorites().some((entry) => entry.key === key)
}

export function toggleFavorite(item) {
  if (isFavorite(item.key)) {
    removeFavorite(item.key)
    return false
  }
  saveFavorite(item)
  return true
}

export function getRecentViews() {
  return readList(RECENT_KEY)
}

export function addRecentView(item) {
  const list = getRecentViews().filter((entry) => entry.key !== item.key)
  writeList(RECENT_KEY, [{ ...item, viewedAt: new Date().toISOString() }, ...list].slice(0, 80))
}

export function clearRecentViews() {
  writeList(RECENT_KEY, [])
}

export function clearFavorites() {
  writeList(FAVORITE_KEY, [])
}
