-- Lua filter to make table headers bold
function Table(tbl)
  if not FORMAT:match 'latex' then
    return tbl
  end

  -- Make header cells bold using \bfseries
  for _, row in ipairs(tbl.head.rows) do
    for _, cell in ipairs(row.cells) do
      -- Prepend \bfseries to make content bold
      table.insert(cell.contents, 1, pandoc.RawBlock('latex', '{\\bfseries '))
      table.insert(cell.contents, pandoc.RawBlock('latex', '}'))
    end
  end

  return tbl
end
