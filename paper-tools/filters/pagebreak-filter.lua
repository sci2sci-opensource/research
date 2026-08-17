-- Lua filter to convert horizontal rules (---) to page breaks in PDF output
function HorizontalRule(elem)
  if FORMAT:match 'latex' then
    return pandoc.RawBlock('latex', '\\newpage')
  else
    return elem
  end
end
