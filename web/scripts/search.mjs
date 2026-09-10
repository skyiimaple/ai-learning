export function tokenize(text) {
  return Array.from(new Intl.Segmenter('zh-CN', { granularity: 'word' }).segment(text))
    .filter(segment => segment.isWordLike)
    .map(segment => segment.segment)
}

// VitePress serializes themeConfig as JSON. Restore the same tokenizer in
// the browser that was used to generate the build-time MiniSearch index.
export function configureLocalSearch(theme) {
  if (theme.search?.provider !== 'local') return
  const options = theme.search.options ??= {}
  const miniSearch = options.miniSearch ??= {}
  miniSearch.options = { ...miniSearch.options, tokenize }
}
