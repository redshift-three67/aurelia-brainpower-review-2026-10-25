const searchable = (value) => String(value ?? "")
  .normalize("NFKD").replace(/\p{M}/gu, "").toLocaleLowerCase("de");

export function filterDatabaseNames(names, groups, query) {
  const needle = searchable(query.trim());
  if (!needle) return [...names];
  return names.filter((name) => {
    if (searchable(name).includes(needle)) return true;
    const group = groups.find(([prefix]) => name.startsWith(prefix));
    return Boolean(group && searchable(group[1]).includes(needle));
  });
}
