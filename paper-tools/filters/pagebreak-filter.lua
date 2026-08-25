-- Lua filter for structural page breaks in LaTeX output.
function HorizontalRule(elem)
  if FORMAT:match 'latex' then
    return pandoc.RawBlock('latex', '\\newpage')
  else
    return elem
  end
end

function RawBlock(elem)
  if FORMAT:match 'latex'
      and elem.format == 'tex'
      and elem.text:match('^%s*\\tableofcontents%s*$') then
    return pandoc.RawBlock('latex', '\\clearpage\n\\tableofcontents')
  end
  return elem
end

function Header(elem)
  if FORMAT:match 'latex'
      and elem.level == 1
      and pandoc.utils.stringify(elem.content) == 'References' then
    return {pandoc.RawBlock('latex', '\\clearpage'), elem}
  end
  return elem
end
